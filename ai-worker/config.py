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

    # GPT-SoVITS TTS API 配置
    TTS_API_BASE_URL = os.getenv("TTS_API_BASE_URL", "http://127.0.0.1:9880")
    # 默认参考音频路径（相对于 GPT-SoVITS-v2pro 目录）
    TTS_REF_AUDIO_PATH = os.getenv("TTS_REF_AUDIO_PATH", "refer_audio/asukadesu01.wav")
    # 默认 GPT 模型权重路径（相对于 GPT-SoVITS-v2pro 目录）
    TTS_GPT_WEIGHTS = os.getenv("TTS_GPT_WEIGHTS", "GPT_weights_v2ProPlus/asuka.ckpt")
    # 默认 SoVITS 模型权重路径（相对于 GPT-SoVITS-v2pro 目录）
    TTS_SOVITS_WEIGHTS = os.getenv("TTS_SOVITS_WEIGHTS", "SoVITS_weights_v2ProPlus/asuka.pth")
    # 默认文本语言
    TTS_DEFAULT_TEXT_LANG = os.getenv("TTS_DEFAULT_TEXT_LANG", "ja")
    # 默认参考音频文本
    TTS_DEFAULT_PROMPT_TEXT = os.getenv("TTS_DEFAULT_PROMPT_TEXT", "")
    # 默认参考音频语言
    TTS_DEFAULT_PROMPT_LANG = os.getenv("TTS_DEFAULT_PROMPT_LANG", "ja")
    # 马老师（中文）音频配置
    TTS_MLS_REF_AUDIO_PATH = os.getenv("TTS_MLS_REF_AUDIO_PATH", "refer_audio/mls.wav")
    TTS_MLS_GPT_WEIGHTS = os.getenv("TTS_MLS_GPT_WEIGHTS", "GPT_weights_v2Pro/mls.ckpt")
    TTS_MLS_SOVITS_WEIGHTS = os.getenv("TTS_MLS_SOVITS_WEIGHTS", "SoVITS_weights_v2Pro/mls_e4_s136.pth")
    TTS_MLS_PROMPT_TEXT = os.getenv("TTS_MLS_PROMPT_TEXT", "")
    TTS_MLS_PROMPT_LANG = os.getenv("TTS_MLS_PROMPT_LANG", "zh")
    TTS_MLS_DEFAULT_LANG = os.getenv("TTS_MLS_DEFAULT_LANG", "zh")

    # 音色配置表
    @property
    def VOICE_PROFILES(self):
        return {
            "asuka": {
                "name": "Asuka (日语)",
                "gpt_weights": self.TTS_GPT_WEIGHTS,
                "sovits_weights": self.TTS_SOVITS_WEIGHTS,
                "ref_audio_path": self.TTS_REF_AUDIO_PATH,
                "prompt_text": self.TTS_DEFAULT_PROMPT_TEXT,
                "prompt_lang": self.TTS_DEFAULT_PROMPT_LANG,
                "default_lang": self.TTS_DEFAULT_TEXT_LANG,
            },
            "malashi": {
                "name": "马老师 (中文)",
                "gpt_weights": self.TTS_MLS_GPT_WEIGHTS,
                "sovits_weights": self.TTS_MLS_SOVITS_WEIGHTS,
                "ref_audio_path": self.TTS_MLS_REF_AUDIO_PATH,
                "prompt_text": self.TTS_MLS_PROMPT_TEXT,
                "prompt_lang": self.TTS_MLS_PROMPT_LANG,
                "default_lang": self.TTS_MLS_DEFAULT_LANG,
            },
        }


config = Config()
