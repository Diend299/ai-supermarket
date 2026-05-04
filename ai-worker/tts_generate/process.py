"""
TTS 语音生成处理脚本
从Redis获取任务，调用 GPT-SoVITS-v2pro API 生成语音，更新数据库状态

依赖:
- GPT-SoVITS-v2pro 的 api_v2.py 需要先启动
- 例如: python api_v2.py -a 127.0.0.1 -p 9880 -c GPT_SoVITS/configs/tts_infer.yaml
"""
import json
import os
import time
import requests
from datetime import datetime
from pathlib import Path

from config import config
from db import db


# ========== GPT-SoVITS API 调用封装 ==========

def switch_tts_weights(gpt_path: str, sovits_path: str) -> bool:
    """
    切换 GPT-SoVITS 的模型权重为指定角色
    先设置 SoVITS 权重，再设置 GPT 权重

    :param gpt_path: GPT 模型权重路径（相对于 GPT-SoVITS-v2pro 目录）
    :param sovits_path: SoVITS 模型权重路径
    :return: 是否成功
    """
    base_url = config.TTS_API_BASE_URL

    # 1. 切换 SoVITS 权重
    sovits_resp = requests.get(
        f"{base_url}/set_sovits_weights",
        params={"weights_path": sovits_path},
        timeout=30,
    )
    if sovits_resp.status_code != 200:
        raise Exception(f"切换 SoVITS 权重失败: {sovits_resp.text}")

    # 2. 切换 GPT 权重
    gpt_resp = requests.get(
        f"{base_url}/set_gpt_weights",
        params={"weights_path": gpt_path},
        timeout=30,
    )
    if gpt_resp.status_code != 200:
        raise Exception(f"切换 GPT 权重失败: {gpt_resp.text}")

    return True


def call_tts_api(text: str, **kwargs) -> bytes:
    """
    调用 GPT-SoVITS TTS API 生成语音

    :param text: 要合成的文本
    :param kwargs: 其他参数，如 text_lang, speed_factor, prompt_text, prompt_lang 等
    :return: WAV 音频二进制数据
    """
    base_url = config.TTS_API_BASE_URL

    # 构建请求参数 - 使用音色对应的参考音频和提示文本
    ref_audio_path = kwargs.get("ref_audio_path", config.TTS_REF_AUDIO_PATH)
    prompt_text = kwargs.get("prompt_text", config.TTS_DEFAULT_PROMPT_TEXT)
    prompt_lang = kwargs.get("prompt_lang", config.TTS_DEFAULT_PROMPT_LANG)

    params = {
        "text": text,
        "text_lang": kwargs.get("text_lang", config.TTS_DEFAULT_TEXT_LANG),
        "ref_audio_path": ref_audio_path,
        "media_type": "wav",
        "streaming_mode": False,
    }

    # prompt_lang 是必填参数（告知 API 参考音频的语言）
    params["prompt_lang"] = prompt_lang or "auto"
    # prompt_text 可选：有内容才传，空字符串不传
    if prompt_text and prompt_text.strip():
        params["prompt_text"] = prompt_text

    # 可选参数
    if "speed_factor" in kwargs:
        params["speed_factor"] = float(kwargs["speed_factor"])
    if "top_k" in kwargs:
        params["top_k"] = int(kwargs["top_k"])
    if "temperature" in kwargs:
        params["temperature"] = float(kwargs["temperature"])

    # 调用 TTS API（POST 方式）
    resp = requests.post(
        f"{base_url}/tts",
        json=params,
        timeout=120,
    )

    if resp.status_code != 200:
        error_detail = resp.text
        try:
            error_json = resp.json()
            error_detail = error_json.get("message", error_json.get("Exception", resp.text))
        except Exception:
            pass
        raise Exception(f"TTS API 调用失败: {error_detail}")

    # 返回音频二进制数据
    return resp.content


# ========== 文件保存 ==========

def save_audio_file(task_id: int, audio_data: bytes) -> str:
    """
    保存音频文件到 uploads/audio 目录

    :param task_id: 任务ID（用于文件命名）
    :param audio_data: 音频二进制数据
    :return: 可访问的 URL 路径
    """
    # 确保上传目录存在
    upload_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "uploads",
        "audio",
    )
    os.makedirs(upload_dir, exist_ok=True)

    # 生成文件名: tts_{taskId}_{timestamp}.wav
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"tts_{task_id}_{timestamp}.wav"
    filepath = os.path.join(upload_dir, filename)

    # 写入文件
    with open(filepath, "wb") as f:
        f.write(audio_data)

    # 获取文件大小
    file_size = os.path.getsize(filepath)

    print(f"[TTS] 音频文件已保存: {filepath} ({file_size} bytes)")

    # 返回相对 URL 路径
    return f"/uploads/audio/{filename}", file_size


# ========== 任务处理主逻辑 ==========

def process_task(task_data: dict):
    """
    处理单个 TTS 语音生成任务

    :param task_data: 任务数据字典，包含 taskId, userId, taskType, params
        params 支持:
        - text: str (必填) 要合成的文本
        - text_lang: str (可选) 文本语言，默认 ja
        - speed: float (可选) 语速，默认 1.0
        - prompt_text: str (可选) 参考音频文本
        - prompt_lang: str (可选) 参考音频语言
    """
    task_id = task_data.get("taskId")
    params = task_data.get("params", {})

    if not task_id:
        print("[TTS] 无效任务数据：缺少 taskId")
        return

    print(f"[TTS] 开始处理任务: taskId={task_id}")

    try:
        # 1. 更新任务状态为"生成中"
        db.update_task_status(task_id, status=1, progress=10)
        print(f"[TTS] 任务 {task_id} 状态已更新为 生成中")

        # 2. 提取参数
        text = params.get("text", "")
        if not text:
            raise ValueError("缺少 text 参数")

        text_lang = params.get("text_lang", config.TTS_DEFAULT_TEXT_LANG)
        speed = params.get("speed", 1.0)

        print(f"[TTS] 文本: {text[:100]}...")
        print(f"[TTS] 语言: {text_lang}, 语速: {speed}")

        # 3. 选择音色并切换模型权重
        voice = params.get("voice", "asuka")  # 默认 asuka
        voice_profile = config.VOICE_PROFILES.get(voice)

        if not voice_profile:
            raise ValueError(f"不支持的音色: {voice}，可选: {list(config.VOICE_PROFILES.keys())}")

        print(f"[TTS] 选择音色: {voice} ({voice_profile['name']})")
        print(f"[TTS] 切换模型权重...")
        switch_tts_weights(
            gpt_path=voice_profile["gpt_weights"],
            sovits_path=voice_profile["sovits_weights"],
        )
        print(f"[TTS] 模型权重切换成功")
        db.update_task_status(task_id, status=1, progress=30)

        # 4. 调用 TTS API 生成语音
        print(f"[TTS] 调用 GPT-SoVITS API 生成语音...")

        tts_kwargs = {
            "text_lang": text_lang,
            "speed_factor": speed,
            # 音色对应的参考音频和提示文本
            "ref_audio_path": voice_profile["ref_audio_path"],
            "prompt_text": voice_profile["prompt_text"],
            "prompt_lang": voice_profile["prompt_lang"],
            "default_lang": voice_profile["default_lang"],
        }
        # 用户可覆盖提示文本
        if "prompt_text" in params:
            tts_kwargs["prompt_text"] = params["prompt_text"]
        if "prompt_lang" in params:
            tts_kwargs["prompt_lang"] = params["prompt_lang"]

        audio_data = call_tts_api(text, **tts_kwargs)
        print(f"[TTS] 语音生成成功, 音频大小: {len(audio_data)} bytes")

        db.update_task_status(task_id, status=1, progress=70)

        # 5. 保存音频文件
        audio_url, file_size = save_audio_file(task_id, audio_data)

        db.update_task_status(task_id, status=1, progress=90)

        # 6. 更新数据库 - 成功，写入 audio 类型资源
        db.update_task_status(
            task_id=task_id,
            status=2,
            progress=100,
            result_audio_url=audio_url,
            result_audio_size=file_size,
        )
        print(f"[TTS] 任务 {task_id} 已完成! 音频URL: {audio_url}")

    except Exception as e:
        error_msg = str(e)
        print(f"[TTS] 任务 {task_id} 失败: {error_msg}")

        # 更新数据库 - 失败
        try:
            db.update_task_status(
                task_id=task_id,
                status=3,
                progress=0,
                error_msg=error_msg[:500],
            )
        except Exception as db_err:
            print(f"[TTS] 更新失败状态时出错: {db_err}")


# ==================== 独立运行入口 ====================
if __name__ == "__main__":
    """
    可以直接运行此脚本测试单次任务处理
    例如: python -m tts_generate.process
    """
    print("[TTS] 脚本独立运行，等待任务...")
    from redis_client import redis_client

    while True:
        task = redis_client.pop_task(timeout=5)
        if task:
            print(f"[TTS] 收到任务: {json.dumps(task, ensure_ascii=False)}")
            process_task(task)
        else:
            print("[TTS] 当前无任务，继续等待...")
            time.sleep(1)
