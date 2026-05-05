"""
Wav2Lip 数字人视频生成处理脚本
从Redis获取任务，调用 Wav2Lip inference.bat 进行唇形同步视频生成

流程:
1. 接收任务参数（音频文件路径）
2. 随机选择 asuka0.mp4 或 asuka1.mp4 作为人脸视频
3. 将音频复制到 Wav2Lip 临时目录
4. 调用 inference.bat 执行推理
5. 将结果视频复制到 uploads/avatar/ 目录
6. 更新数据库状态
"""
import json
import os
import random
import shutil
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path

from config import config
from db import db


# ========== 路径配置 ==========

def get_worker_base_dir() -> str:
    """获取 ai-worker 根目录"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def resolve_audio_path(audio_path: str) -> str:
    """
    将前端传过来的 URL 路径（如 /uploads/audio/xxx.wav）转换为本地文件系统绝对路径

    注意：Windows 上 os.path.isabs('/xxx') 也返回 True（视作绝对路径），
    所以必须先处理 URL 风格的路径（以 / 开头），否则会直接把 /uploads/... 当作绝对路径返回。
    """
    # URL 风格路径（以 / 开头）→ 拼接 ai-worker 根目录转为本地绝对路径
    if audio_path.startswith("/"):
        rel_path = audio_path.lstrip("/")  # "uploads/audio/xxx.wav"
        worker_base = get_worker_base_dir()
        return os.path.join(worker_base, rel_path)

    # 已是本地绝对路径（如 D:\...）→ 直接返回
    if os.path.isabs(audio_path):
        return audio_path

    # 相对路径 → 拼接 ai-worker 根目录
    worker_base = get_worker_base_dir()
    return os.path.join(worker_base, audio_path)



def get_wav2lip_dir() -> str:

    """获取 Wav2Lip 根目录"""
    return os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        "..", "avatar", "Wav2Lip"
    ))


def get_avatar_video_path(video_name: str) -> str:
    """
    获取数字人模板视频的完整路径
    :param video_name: 如 asuka0.mp4, asuka1.mp4
    """
    return os.path.join(get_wav2lip_dir(), "avatars", "asuka", video_name)


def get_result_video_path() -> str:
    """获取 inference.bat 输出的结果视频路径"""
    return os.path.join(get_wav2lip_dir(), "results", "result_voice.mp4")


def get_uploads_avatar_dir() -> str:
    """获取上传目录（存放最终结果视频）"""
    upload_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "uploads", "avatar"
    )
    os.makedirs(upload_dir, exist_ok=True)
    return upload_dir


def get_temp_audio_dir() -> str:
    """获取 Wav2Lip 临时音频目录"""
    temp_dir = os.path.join(get_wav2lip_dir(), "temp")
    os.makedirs(temp_dir, exist_ok=True)
    return temp_dir


# ========== Wav2Lip 调用封装 ==========

def run_wav2lip_inference(face_video_path: str, audio_path: str, output_path: str,
                          timeout: int = 3600) -> bool:
    """
    调用 Wav2Lip inference.bat 执行唇形同步推理

    改进说明：
    - 使用 Popen + 线程流式读取输出，避免 GBK 编码解码错误
    - 超时后检查结果文件是否已生成，若已生成则视为成功
    - 更长的默认超时（1小时），应付 GFPGAN 人脸增强

    :param face_video_path: 人脸视频完整路径（如 asuka0.mp4）
    :param audio_path: 音频文件完整路径（WAV格式）
    :param output_path: 输出视频文件保存路径
    :param timeout: 超时秒数，默认 3600（1小时）
    :return: 是否成功
    """
    wav2lip_dir = get_wav2lip_dir()
    inference_bat = os.path.join(wav2lip_dir, "inference.bat")
    default_result = get_result_video_path()

    # 检查必备文件
    if not os.path.isfile(face_video_path):
        raise FileNotFoundError(f"人脸视频文件不存在: {face_video_path}")
    if not os.path.isfile(audio_path):
        raise FileNotFoundError(f"音频文件不存在: {audio_path}")
    if not os.path.isfile(inference_bat):
        raise FileNotFoundError(f"inference.bat 不存在: {inference_bat}")

    # 清理上次遗留的结果文件，避免超时误判
    if os.path.isfile(default_result):
        try:
            os.remove(default_result)
            print(f"[Wav2Lip] 已清理旧结果文件: {default_result}")
        except Exception as e:
            print(f"[Wav2Lip] 清理旧结果文件失败: {e}")

    # Windows 下执行 bat 需要用 shell=True，字符串形式传给 cmd.exe
    # 格式: cmd.exe /c "C:\path\bat" "arg1" "arg2"
    cmd = f'"{inference_bat}" "{face_video_path}" "{audio_path}"'
    print(f"[Wav2Lip] 执行命令: {cmd}")
    print(f"[Wav2Lip] 工作目录: {wav2lip_dir}")
    print(f"[Wav2Lip] 超时设置: {timeout}秒")

    # 启动子进程（shell=True 用于执行 bat）
    proc = subprocess.Popen(
        cmd,
        cwd=wav2lip_dir,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # 用线程读取 stdout/stderr（避免管道阻塞），直接以二进制读取再 fallback 解码
    stdout_lines = []
    stderr_lines = []

    def _read_stream(stream, storage):
        """读取流并尝试 UTF-8 解码，失败则用 GBK 回退"""
        try:
            for raw_line in iter(stream.readline, b''):
                try:
                    line = raw_line.decode('utf-8', errors='replace').rstrip('\r\n')
                except UnicodeDecodeError:
                    line = raw_line.decode('gbk', errors='replace').rstrip('\r\n')
                if line:
                    storage.append(line)
                    print(f"[Wav2Lip] {line[:500]}")
        except Exception as e:
            storage.append(f"[读取输出异常]: {e}")

    t_stdout = threading.Thread(target=_read_stream, args=(proc.stdout, stdout_lines), daemon=True)
    t_stderr = threading.Thread(target=_read_stream, args=(proc.stderr, stderr_lines), daemon=True)
    t_stdout.start()
    t_stderr.start()

    # 等待进程完成，支持超时
    start_time = time.time()
    timed_out = False

    while True:
        # 检查进程是否结束
        retcode = proc.poll()
        if retcode is not None:
            # 进程已结束
            elapsed = time.time() - start_time
            print(f"[Wav2Lip] 进程结束，返回码: {retcode}，耗时: {elapsed:.1f}秒")
            break

        # 检查是否超时
        if time.time() - start_time > timeout:
            timed_out = True
            print(f"[Wav2Lip] ⚠ 进程执行超过 {timeout}秒，将检查结果文件是否已生成...")
            # 检查结果文件是否已经生成
            if os.path.isfile(default_result):
                file_size = os.path.getsize(default_result)
                print(f"[Wav2Lip] ✅ 结果文件已存在! ({default_result}, {file_size} bytes)")
                print(f"[Wav2Lip] 将终止进程并视为成功")
                # 终止进程
                try:
                    proc.terminate()
                    proc.wait(timeout=10)
                except Exception:
                    try:
                        proc.kill()
                        proc.wait(timeout=5)
                    except Exception:
                        pass
                break
            else:
                print(f"[Wav2Lip] ❌ 结果文件尚未生成，继续等待...")
                # 还没生成结果，但已经超时了 — 再等 5 分钟看看
                timeout += 300
                print(f"[Wav2Lip] 延长超时至 {timeout}秒，继续等待...")
                continue

        # 每 30 秒输出一次进度
        elapsed = time.time() - start_time
        if int(elapsed) % 60 == 0 and int(elapsed) > 0:
            print(f"[Wav2Lip] 运行中... 已耗时 {elapsed:.0f}秒")

        time.sleep(5)

    # 确保读取线程完成
    t_stdout.join(timeout=5)
    t_stderr.join(timeout=5)

    # 如果进程还在跑，确保被终止
    if proc.poll() is None:
        try:
            proc.terminate()
            proc.wait(timeout=10)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass

    # 获取最终返回码
    returncode = proc.returncode if proc.returncode is not None else -1

    # 拼接完整输出用于日志
    all_stderr = '\n'.join(stderr_lines)

    # 检查结果文件
    if os.path.isfile(default_result):
        file_size = os.path.getsize(default_result)
        print(f"[Wav2Lip] 结果文件确认存在: {default_result} ({file_size} bytes)")

        # 将结果复制到指定输出路径
        shutil.copy2(default_result, output_path)
        print(f"[Wav2Lip] 结果视频已复制到: {output_path}")

        if timed_out:
            print(f"[Wav2Lip] ⚠ 进程超时但结果文件已生成，视为成功 (返回码: {returncode})")
        elif returncode != 0:
            print(f"[Wav2Lip] ⚠ 进程返回码非零({returncode})但结果文件已生成，视为成功")
            print(f"[Wav2Lip] STDERR: {all_stderr[:1000]}")

        return True
    else:
        raise FileNotFoundError(
            f"Wav2Lip 推理未生成结果视频: {default_result}\n"
            f"返回码: {returncode}\n"
            f"STDERR: {all_stderr[:500]}"
        )


def copy_audio_to_temp(audio_path: str) -> str:
    """
    将音频文件复制到 Wav2Lip temp 目录，统一命名为 temp_audio.wav

    :param audio_path: 原始音频路径
    :return: 临时音频路径
    """
    temp_dir = get_temp_audio_dir()
    dest_path = os.path.join(temp_dir, "temp_audio.wav")

    # 如果目标已存在则先删除
    if os.path.isfile(dest_path):
        os.remove(dest_path)

    shutil.copy2(audio_path, dest_path)
    print(f"[Wav2Lip] 音频已复制到临时目录: {dest_path}")
    return dest_path


# ========== 任务处理主逻辑 ==========

def process_task(task_data: dict):
    """
    处理单个 Wav2Lip 数字人视频生成任务

    :param task_data: 任务数据字典，包含 taskId, userId, taskType, params
        params 支持:
        - audio_path: str (必填) TTS生成的音频文件系统路径
    """
    task_id = task_data.get("taskId")
    params = task_data.get("params", {})

    if not task_id:
        print("[Wav2Lip] 无效任务数据：缺少 taskId")
        return

    print(f"[Wav2Lip] 开始处理任务: taskId={task_id}")

    try:
        # 1. 更新任务状态为"生成中"
        db.update_task_status(task_id, status=1, progress=10)
        print(f"[Wav2Lip] 任务 {task_id} 状态已更新为 生成中")

        # 2. 提取参数并解析路径
        raw_audio_path = params.get("audio_path", "")
        if not raw_audio_path:
            raise ValueError("缺少 audio_path 参数")

        audio_path = resolve_audio_path(raw_audio_path)
        if not os.path.isfile(audio_path):
            raise FileNotFoundError(f"音频文件不存在 (原始: {raw_audio_path}, 解析后: {audio_path})")

        print(f"[Wav2Lip] 音频文件: {audio_path}")


        # 3. 随机选择 asuka0.mp4 或 asuka1.mp4 作为人脸视频
        avatar_video_name = random.choice(["asuka0.mp4", "asuka1.mp4"])
        face_video_path = get_avatar_video_path(avatar_video_name)
        print(f"[Wav2Lip] 选择数字人形象: {avatar_video_name}")

        db.update_task_status(task_id, status=1, progress=20)

        # 4. 复制音频到 Wav2Lip 临时目录
        temp_audio_path = copy_audio_to_temp(audio_path)

        db.update_task_status(task_id, status=1, progress=30)

        # 5. 生成输出视频路径
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"avatar_wav2lip_{task_id}_{timestamp}.mp4"
        output_path = os.path.join(get_uploads_avatar_dir(), output_filename)

        # 6. 调用 Wav2Lip 推理
        print(f"[Wav2Lip] 开始执行 Wav2Lip 推理...")
        db.update_task_status(task_id, status=1, progress=40)

        run_wav2lip_inference(face_video_path, temp_audio_path, output_path)

        db.update_task_status(task_id, status=1, progress=90)

        # 7. 确认输出文件存在
        if not os.path.isfile(output_path):
            raise FileNotFoundError(f"结果视频文件未生成: {output_path}")

        file_size = os.path.getsize(output_path)
        print(f"[Wav2Lip] 视频文件已生成: {output_path} ({file_size} bytes)")

        # 8. 生成 URL 路径供前端访问
        video_url = f"/uploads/avatar/{output_filename}"

        # 9. 更新数据库 - 成功，写入 video 类型资源
        db.update_task_status(
            task_id=task_id,
            status=2,
            progress=100,
            result_video_url=video_url,
        )
        print(f"[Wav2Lip] 任务 {task_id} 已完成! 视频URL: {video_url}")

    except Exception as e:
        error_msg = str(e)
        print(f"[Wav2Lip] 任务 {task_id} 失败: {error_msg}")

        # 更新数据库 - 失败
        try:
            db.update_task_status(
                task_id=task_id,
                status=3,
                progress=0,
                error_msg=error_msg[:500],
            )
        except Exception as db_err:
            print(f"[Wav2Lip] 更新失败状态时出错: {db_err}")


# ==================== 独立运行入口 ====================
if __name__ == "__main__":
    """
    可以直接运行此脚本测试单次任务处理
    例如: python -m wav2lip_generate.process
    """
    print("[Wav2Lip] 脚本独立运行，等待任务...")
    from redis_client import redis_client

    while True:
        task = redis_client.pop_task(timeout=5)
        if task:
            print(f"[Wav2Lip] 收到任务: {json.dumps(task, ensure_ascii=False)}")
            process_task(task)
        else:
            print("[Wav2Lip] 当前无任务，继续等待...")
            time.sleep(1)
