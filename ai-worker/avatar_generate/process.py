"""
数字人视频生成处理脚本
从Redis获取任务，模拟数字人视频生成流程，更新数据库状态

TODO: 替换为实际的数字人模型API调用（如 HeyGen、SadTalker 等）
"""
import json
import time
import os
from datetime import datetime
from config import config
from db import db


def process_task(task_data: dict):
    """
    处理单个数字人视频生成任务
    :param task_data: 任务数据字典，包含 taskId, userId, taskType, params
    """
    task_id = task_data.get("taskId")
    params = task_data.get("params", {})

    if not task_id:
        print("[AvatarGenerate] 无效任务数据：缺少taskId")
        return

    print(f"[AvatarGenerate] 开始处理任务: taskId={task_id}")

    try:
        # 1. 更新任务状态为"生成中"
        db.update_task_status(task_id, status=1, progress=10)
        print(f"[AvatarGenerate] 任务 {task_id} 状态已更新为 生成中")

        # 2. 提取参数
        text = params.get("text", "")
        voice = params.get("voice", "female")
        speed = params.get("speed", "1.0")
        resolution = params.get("resolution", "720p")
        # reference_image 为 base64 数据，暂不处理（模拟阶段）

        if not text:
            raise ValueError("缺少 text 参数")

        print(f"[AvatarGenerate] 文本长度: {len(text)}")
        print(f"[AvatarGenerate] 语音: {voice}, 语速: {speed}, 分辨率: {resolution}")

        # 3. 模拟处理进度（实际项目中调用数字人生成API）
        for step in range(2, 10):
            time.sleep(1)  # 模拟处理耗时
            progress = step * 10
            db.update_task_status(task_id, status=1, progress=progress)
            print(f"[AvatarGenerate] 进度 {progress}%")

        # 4. 模拟生成视频文件路径
        # TODO: 实际项目中，此处调用数字人API生成视频并保存到存储服务
        output_filename = f"avatar_{task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        output_url = f"/uploads/avatar/{output_filename}"
        
        # 确保上传目录存在
        upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads", "avatar")
        os.makedirs(upload_dir, exist_ok=True)

        # 模拟生成一个空视频文件（实际项目中替换为真实视频文件）
        dummy_video_path = os.path.join(upload_dir, output_filename)
        with open(dummy_video_path, "wb") as f:
            # 写入一个最小的MP4文件头（仅作为占位，实际应使用真实视频）
            f.write(b'\x00\x00\x00\x08ftypmp42\x00\x00\x00\x00mp42')

        print(f"[AvatarGenerate] 视频文件已生成: {dummy_video_path}")

        # 5. 更新数据库 - 成功，写入 video 类型资源
        db.update_task_status(
            task_id=task_id,
            status=2,
            progress=100,
            result_video_url=output_url,
        )
        print(f"[AvatarGenerate] 任务 {task_id} 已完成!")

    except Exception as e:
        error_msg = str(e)
        print(f"[AvatarGenerate] 任务 {task_id} 失败: {error_msg}")

        # 更新数据库 - 失败
        try:
            db.update_task_status(
                task_id=task_id,
                status=3,
                progress=0,
                error_msg=error_msg[:500],
            )
        except Exception as db_err:
            print(f"[AvatarGenerate] 更新失败状态时出错: {db_err}")


# ==================== 独立运行入口 ====================
if __name__ == "__main__":
    """
    可以直接运行此脚本测试单次任务处理
    例如: python -m avatar_generate.process
    """
    print("[AvatarGenerate] 脚本独立运行，等待任务...")
    from redis_client import redis_client

    while True:
        task = redis_client.pop_task(timeout=5)
        if task:
            print(f"[AvatarGenerate] 收到任务: {json.dumps(task, ensure_ascii=False)}")
            process_task(task)
        else:
            print("[AvatarGenerate] 当前无任务，继续等待...")
            time.sleep(1)
