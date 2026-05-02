"""
文本生成处理脚本
从Redis获取任务，调用DeepSeek API进行文本生成，更新数据库状态

独立脚本，也可被 main.py 导入调用
"""
import json
import time
import requests
from config import config
from db import db


def call_deepseek_api(prompt: str, system_prompt: str = None) -> str:
    """
    调用 DeepSeek API 进行文本生成
    :param prompt: 用户提示词
    :param system_prompt: 系统提示词（可选）
    :return: 生成的文本内容
    """
    if not config.DEEPSEEK_API_KEY:
        raise ValueError("DeepSeek API Key 未配置")

    headers = {
        "Authorization": f"Bearer {config.DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 4096,
    }

    response = requests.post(
        config.DEEPSEEK_API_URL,
        headers=headers,
        json=payload,
        timeout=120,
    )

    if response.status_code != 200:
        raise Exception(f"DeepSeek API 调用失败: {response.status_code} {response.text}")

    result = response.json()
    return result["choices"][0]["message"]["content"]


def process_task(task_data: dict):
    """
    处理单个文本生成任务
    :param task_data: 任务数据字典，包含 taskId, userId, taskType, params
    """
    task_id = task_data.get("taskId")
    params = task_data.get("params", {})

    if not task_id:
        print("[Text2Text] 无效任务数据：缺少taskId")
        return

    print(f"[Text2Text] 开始处理任务: taskId={task_id}")

    try:
        # 1. 更新任务状态为"生成中"
        db.update_task_status(task_id, status=1, progress=10)
        print(f"[Text2Text] 任务 {task_id} 状态已更新为 生成中")

        # 2. 提取参数
        prompt = params.get("prompt", "")
        system_prompt = params.get("system_prompt", "你是一个专业的文案创作助手。")

        if not prompt:
            raise ValueError("缺少 prompt 参数")

        print(f"[Text2Text] 调用 DeepSeek API...")
        print(f"[Text2Text] Prompt: {prompt[:100]}...")

        # 3. 调用 DeepSeek API
        generated_text = call_deepseek_api(prompt, system_prompt)

        print(f"[Text2Text] DeepSeek API 返回成功, 文本长度: {len(generated_text)}")

        # 4. 更新数据库 - 成功
        db.update_task_status(
            task_id=task_id,
            status=2,
            progress=100,
            result_text=generated_text,
        )
        print(f"[Text2Text] 任务 {task_id} 已完成!")

    except Exception as e:
        error_msg = str(e)
        print(f"[Text2Text] 任务 {task_id} 失败: {error_msg}")

        # 更新数据库 - 失败
        try:
            db.update_task_status(
                task_id=task_id,
                status=3,
                progress=0,
                error_msg=error_msg[:500],
            )
        except Exception as db_err:
            print(f"[Text2Text] 更新失败状态时出错: {db_err}")


# ==================== 独立运行入口 ====================
if __name__ == "__main__":
    """
    可以直接运行此脚本测试单次任务处理
    例如: python -m text2text.test
    或者从 main.py 导入后调用
    """
    print("[Text2Text] 脚本独立运行，等待任务...")
    from redis_client import redis_client

    while True:
        task = redis_client.pop_task(timeout=5)
        if task:
            print(f"[Text2Text] 收到任务: {json.dumps(task, ensure_ascii=False)}")
            process_task(task)
        else:
            print("[Text2Text] 当前无任务，继续等待...")
            time.sleep(1)
