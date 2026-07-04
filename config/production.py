"""
生产环境配置
"""

import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent.parent

# 数据库配置
DATABASE = {
    "path": os.getenv("DATABASE_PATH", str(BASE_DIR / "data" / "memora.db")),
    "backup_path": os.getenv("DATABASE_BACKUP_PATH", str(BASE_DIR / "data" / "backups")),
    "max_backups": int(os.getenv("DATABASE_MAX_BACKUPS", "10")),
    "auto_backup_interval": int(os.getenv("DATABASE_BACKUP_INTERVAL", "3600")),
}

# 存储配置
STORAGE = {
    "assets_path": os.getenv("ASSETS_PATH", str(BASE_DIR / "data" / "assets")),
    "max_file_size": int(os.getenv("MAX_FILE_SIZE", str(100 * 1024 * 1024))),  # 100MB
    "allowed_types": ["image/*", "video/*", "audio/*"],
}

# 服务器配置
SERVER = {
    "host": os.getenv("SERVER_HOST", "0.0.0.0"),
    "port": int(os.getenv("SERVER_PORT", "8352")),
    "workers": int(os.getenv("SERVER_WORKERS", "4")),
    "timeout": int(os.getenv("SERVER_TIMEOUT", "30")),
}

# 安全配置
SECURITY = {
    "access_token": os.getenv("ACCESS_TOKEN", ""),
    "rate_limit": int(os.getenv("RATE_LIMIT", "100")),
    "cors_origins": os.getenv("CORS_ORIGINS", "*").split(","),
}

# 日志配置
LOGGING = {
    "level": os.getenv("LOG_LEVEL", "INFO"),
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": os.getenv("LOG_FILE", str(BASE_DIR / "logs" / "app.log")),
}

# 监控配置
MONITORING = {
    "enabled": os.getenv("MONITORING_ENABLED", "true").lower() == "true",
    "health_check_interval": int(os.getenv("HEALTH_CHECK_INTERVAL", "60")),
    "metrics_retention_days": int(os.getenv("METRICS_RETENTION_DAYS", "30")),
}

# 创建必要的目录
def ensure_directories():
    """确保所有必要的目录存在"""
    dirs = [
        DATABASE["path"].rsplit("/", 1)[0],
        DATABASE["backup_path"],
        STORAGE["assets_path"],
        os.path.dirname(LOGGING["file"]),
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)


# 初始化时创建目录
ensure_directories()
