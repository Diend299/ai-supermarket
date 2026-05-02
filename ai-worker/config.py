"""
配置文件
从环境变量加载配置，支持 .env 文件
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # 数据库
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "root123456")
    DB_NAME = os.getenv("DB_NAME", "ai_supermarket")

    # Redis
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")

    # Redis 队列Key
    REDIS_TASK_QUEUE = "ai:task:queue"

    # DeepSeek API
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_API_URL = os.getenv(
        "DEEPSEEK_API_URL",
        "https://api.deepseek.com/v1/chat/completions"
    )

    # Worker
    WORKER_POLL_INTERVAL = int(os.getenv("WORKER_POLL_INTERVAL", "1"))


config = Config()
