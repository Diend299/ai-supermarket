"""
ai_worker 主入口
持续从 Redis 队列获取任务，根据 task_type 分发到不同模块处理
"""
import signal
import sys
import time
import json

from config import config
from redis_client import redis_client
from db import db


class AiWorker:
    """AI Worker 主循环"""

    def __init__(self):
        self.running = True
        self._register_signal_handlers()

    def _register_signal_handlers(self):
        """注册信号处理器，支持优雅关闭"""
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)

    def _handle_shutdown(self, signum, frame):
        """处理关闭信号"""
        print("\n[Worker] 收到关闭信号，正在优雅退出...")
        self.running = False

    def _dispatch_task(self, task_data: dict):
        """
        根据任务类型分发任务
        :param task_data: 任务数据
        """
        task_type = task_data.get("taskType", "")
        print(f"[Worker] 分发任务: type={task_type}, data={json.dumps(task_data, ensure_ascii=False)}")

        if task_type == "text2text":
            # 导入 text2text 模块处理
            from text2text.test import process_task
            process_task(task_data)

        elif task_type == "video_generate":
            # TODO: 视频生成任务处理
            print(f"[Worker] 视频生成任务暂未实现: taskId={task_data.get('taskId')}")

        elif task_type == "avatar_generate":
            # 导入 avatar_generate 模块处理
            from avatar_generate.process import process_task
            process_task(task_data)

        elif task_type == "tts_generate":
            # 导入 tts_generate 模块处理
            from tts_generate.process import process_task
            process_task(task_data)

        else:
            # 未知类型，标记为失败
            print(f"[Worker] 未知任务类型: {task_type}")
            task_id = task_data.get("taskId")
            if task_id:
                db.update_task_status(
                    task_id=task_id,
                    status=3,
                    progress=0,
                    error_msg=f"不支持的任务类型: {task_type}",
                )

    def run(self):
        """启动 Worker 主循环"""
        print("=" * 50)
        print("  AI Worker 启动")
        print(f"  Redis: {config.REDIS_HOST}:{config.REDIS_PORT}")
        print(f"  MySQL: {config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}")
        print(f"  队列Key: {config.REDIS_TASK_QUEUE}")
        print("=" * 50)

        # 检查连接
        if not redis_client.ping():
            print("[Worker] Redis 连接失败，请检查配置！")
            sys.exit(1)

        print("[Worker] Redis 连接成功，等待任务...")

        while self.running:
            try:
                # 阻塞式获取任务（最多等待5秒）
                task_data = redis_client.pop_task(timeout=5)

                if task_data:
                    print(f"[Worker] 获取到新任务: {json.dumps(task_data, ensure_ascii=False)}")
                    self._dispatch_task(task_data)
                else:
                    # 没有任务时短暂等待
                    time.sleep(config.WORKER_POLL_INTERVAL)

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"[Worker] 处理异常: {e}")
                time.sleep(1)

        self._cleanup()

    def _cleanup(self):
        """清理资源"""
        print("[Worker] 清理资源...")
        db.close()
        print("[Worker] 已退出")


if __name__ == "__main__":
    worker = AiWorker()
    worker.run()
