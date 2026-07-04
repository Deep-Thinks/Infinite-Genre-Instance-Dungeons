"""
数据库备份系统
"""

import os
import shutil
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import Optional


class BackupManager:
    """备份管理器"""

    def __init__(self, db_path: str, backup_dir: str, max_backups: int = 10):
        """
        初始化备份管理器

        Args:
            db_path: 数据库路径
            backup_dir: 备份目录
            max_backups: 最大备份数量
        """
        self.db_path = db_path
        self.backup_dir = backup_dir
        self.max_backups = max_backups

        # 确保备份目录存在
        os.makedirs(backup_dir, exist_ok=True)

    def create_backup(self, name: Optional[str] = None) -> str:
        """
        创建数据库备份

        Args:
            name: 备份名称（可选）

        Returns:
            备份文件路径
        """
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"数据库文件不存在: {self.db_path}")

        # 生成备份文件名
        if name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name = f"backup_{timestamp}"

        backup_path = os.path.join(self.backup_dir, f"{name}.db")

        # 复制数据库文件
        shutil.copy2(self.db_path, backup_path)

        # 同时备份WAL文件（如果存在）
        wal_path = self.db_path + "-wal"
        if os.path.exists(wal_path):
            shutil.copy2(wal_path, backup_path + "-wal")

        # 同时备份SHM文件（如果存在）
        shm_path = self.db_path + "-shm"
        if os.path.exists(shm_path):
            shutil.copy2(shm_path, backup_path + "-shm")

        print(f"备份创建成功: {backup_path}")
        return backup_path

    def restore_backup(self, backup_path: str) -> bool:
        """
        从备份恢复数据库

        Args:
            backup_path: 备份文件路径

        Returns:
            是否恢复成功
        """
        if not os.path.exists(backup_path):
            print(f"备份文件不存在: {backup_path}")
            return False

        try:
            # 先创建当前数据库的备份
            self.create_backup("pre_restore")

            # 恢复数据库
            shutil.copy2(backup_path, self.db_path)

            # 恢复WAL文件（如果存在）
            wal_path = backup_path + "-wal"
            if os.path.exists(wal_path):
                shutil.copy2(wal_path, self.db_path + "-wal")

            # 恢复SHM文件（如果存在）
            shm_path = backup_path + "-shm"
            if os.path.exists(shm_path):
                shutil.copy2(shm_path, self.db_path + "-shm")

            print(f"数据库恢复成功: {backup_path}")
            return True

        except Exception as e:
            print(f"恢复失败: {e}")
            return False

    def list_backups(self) -> list:
        """
        列出所有备份

        Returns:
            备份文件列表
        """
        backups = []
        for file in os.listdir(self.backup_dir):
            if file.endswith(".db"):
                file_path = os.path.join(self.backup_dir, file)
                stat = os.stat(file_path)
                backups.append({
                    "name": file,
                    "path": file_path,
                    "size": stat.st_size,
                    "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                })

        # 按创建时间排序
        backups.sort(key=lambda x: x["created_at"], reverse=True)
        return backups

    def cleanup_old_backups(self) -> int:
        """
        清理旧的备份

        Returns:
            删除的备份数量
        """
        backups = self.list_backups()
        deleted_count = 0

        # 保留最新的max_backups个备份
        for backup in backups[self.max_backups:]:
            try:
                os.remove(backup["path"])
                # 同时删除WAL和SHM文件
                wal_path = backup["path"] + "-wal"
                shm_path = backup["path"] + "-shm"
                if os.path.exists(wal_path):
                    os.remove(wal_path)
                if os.path.exists(shm_path):
                    os.remove(shm_path)
                deleted_count += 1
                print(f"删除旧备份: {backup['name']}")
            except Exception as e:
                print(f"删除备份失败: {e}")

        return deleted_count

    def get_backup_info(self, backup_path: str) -> Optional[dict]:
        """
        获取备份信息

        Args:
            backup_path: 备份文件路径

        Returns:
            备份信息
        """
        if not os.path.exists(backup_path):
            return None

        stat = os.stat(backup_path)

        # 验证数据库完整性
        is_valid = self._validate_backup(backup_path)

        return {
            "path": backup_path,
            "size": stat.st_size,
            "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "is_valid": is_valid,
        }

    def _validate_backup(self, backup_path: str) -> bool:
        """验证备份文件的完整性"""
        try:
            conn = sqlite3.connect(backup_path)
            cursor = conn.cursor()
            # 执行简单的查询来验证数据库完整性
            cursor.execute("SELECT COUNT(*) FROM sqlite_master")
            cursor.fetchone()
            conn.close()
            return True
        except Exception:
            return False
