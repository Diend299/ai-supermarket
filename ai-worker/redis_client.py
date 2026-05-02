"""
Redis 客户端封装
提供连接池和队列操作
"""
import json
import redis
from config import config


class RedisClient:
    """Redis 队列操作封装"""

    def __init__(self):
        pool = redis.ConnectionPool(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            db=config.REDIS_DB,
            password=config.REDIS_PASSWORD or None,
            decode_responses=True,
        )
        self.conn = redis.Redis(connection_pool=pool)

    def pop_task(self, timeout: int = 0) -> dict | None:
        """
        从队列中阻塞式弹出任务 (BRPOP)
        :param timeout: 超时秒数，0表示一直阻塞
        :return: 任务字典或None
        """
        result = self.conn.brpop(config.REDIS_TASK_QUEUE, timeout=timeout)
        if result is None:
            return None

        # BRPOP 返回 (key, value) 元组
        _, value = result
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            print(f"[Redis] 消息解析失败: {value}")
            return None

    def get_queue_length(self) -> int:
        """获取队列长度"""
        return self.conn.llen(config.REDIS_TASK_QUEUE)

    def ping(self) -> bool:
        """测试连接"""
        try:
            return self.conn.ping()
        except redis.ConnectionError:
            return False


# 全局单例
redis_client = RedisClient()
