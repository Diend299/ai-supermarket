"""
数据库操作封装
提供 MySQL 连接和任务状态更新
"""
import json
from datetime import datetime
import pymysql
import redis
from config import config


class DatabaseClient:
    """数据库操作封装"""

    def __init__(self):
        self.connection = None
        self._connect()
        # Redis 连接(用于发布任务完成通知)
        self._redis = redis.Redis(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            db=config.REDIS_DB,
            password=config.REDIS_PASSWORD or None,
            decode_responses=True,
        )

    def _connect(self):
        """建立数据库连接"""
        self.connection = pymysql.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )

    def _ensure_connection(self):
        """确保连接有效，断线重连"""
        try:
            self.connection.ping(reconnect=True)
        except pymysql.Error:
            self._connect()

    def get_task(self, task_id: int) -> dict | None:
        """查询任务信息"""
        self._ensure_connection()
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT * FROM `ai_task` WHERE id = %s", (task_id,))
            return cursor.fetchone()

    def update_task_status(
        self,
        task_id: int,
        status: int,
        progress: int = 0,
        error_msg: str = None,
        result_text: str = None,
        result_video_url: str = None,
    ):
        """
        更新任务状态
        :param task_id: 任务ID
        :param status: 状态 0=排队中, 1=生成中, 2=成功, 3=失败
        :param progress: 进度 0-100
        :param error_msg: 错误信息
        :param result_text: 生成的文本结果
        :param result_video_url: 生成的视频URL
        """
        self._ensure_connection()
        now = datetime.now()

        with self.connection.cursor() as cursor:
            # 更新 ai_task 表
            if status == 1:
                # 开始执行
                cursor.execute(
                    """UPDATE `ai_task`
                       SET task_status = %s, progress = %s, started_at = %s, updated_at = NOW()
                       WHERE id = %s""",
                    (status, progress, now, task_id),
                )
            elif status == 2:
                # 成功 - 同时设置finished_at
                cursor.execute(
                    """UPDATE `ai_task`
                       SET task_status = %s, progress = %s, finished_at = %s, updated_at = NOW()
                       WHERE id = %s""",
                    (status, progress, now, task_id),
                )
            elif status == 3:
                # 失败
                cursor.execute(
                    """UPDATE `ai_task`
                       SET task_status = %s, progress = %s, error_msg = %s,
                           finished_at = %s, updated_at = NOW()
                       WHERE id = %s""",
                    (status, progress, error_msg, now, task_id),
                )

        # 如果生成成功且有结果文本，写入 ai_result_resource 表
        if status == 2 and result_text:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO `ai_result_resource` (task_id, resource_type, resource_url, content_text)
                       VALUES (%s, %s, %s, %s)""",
                    (task_id, "text", "text_result", result_text),
                )

        # 如果生成成功且有视频URL，写入 ai_result_resource 表
        if status == 2 and result_video_url:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO `ai_result_resource` (task_id, resource_type, resource_url, content_text)
                       VALUES (%s, %s, %s, %s)""",
                    (task_id, "video", result_video_url, ""),
                )

        self.connection.commit()

        # 任务终态(成功或失败) 发布 Redis 通知，供 Java SSE 推送
        if status in (2, 3):
            try:
                notify = json.dumps({
                    "taskId": task_id,
                    "status": status,
                    "errorMsg": error_msg,
                })
                self._redis.publish("ai:task:notify", notify)
            except Exception as e:
                print(f"[DB] Redis publish failed: {e}")

    def close(self):
        """关闭连接"""
        if self.connection:
            self.connection.close()


# 全局单例
db = DatabaseClient()
