"""
健康检查和监控系统
"""

import os
import time
import sqlite3
import psutil
from datetime import datetime
from typing import Dict, Any


class HealthChecker:
    """健康检查器"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.start_time = time.time()

    def check_database(self) -> Dict[str, Any]:
        """检查数据库状态"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 检查表是否存在
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]

            # 获取记录数
            stats = {}
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                stats[table] = cursor.fetchone()[0]

            conn.close()

            return {
                "status": "healthy",
                "tables": len(tables),
                "records": stats,
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
            }

    def check_storage(self) -> Dict[str, Any]:
        """检查存储状态"""
        try:
            # 检查磁盘使用情况
            disk = psutil.disk_usage("/")

            return {
                "status": "healthy",
                "disk_total": disk.total,
                "disk_used": disk.used,
                "disk_free": disk.free,
                "disk_percent": disk.percent,
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
            }

    def check_memory(self) -> Dict[str, Any]:
        """检查内存使用情况"""
        try:
            memory = psutil.virtual_memory()

            return {
                "status": "healthy",
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent,
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
            }

    def check_cpu(self) -> Dict[str, Any]:
        """检查CPU使用情况"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)

            return {
                "status": "healthy",
                "percent": cpu_percent,
                "count": psutil.cpu_count(),
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
            }

    def get_uptime(self) -> float:
        """获取运行时间（秒）"""
        return time.time() - self.start_time

    def get_full_health_check(self) -> Dict[str, Any]:
        """获取完整的健康检查结果"""
        db_status = self.check_database()
        storage_status = self.check_storage()
        memory_status = self.check_memory()
        cpu_status = self.check_cpu()

        # 判断整体状态
        all_healthy = all([
            db_status["status"] == "healthy",
            storage_status["status"] == "healthy",
            memory_status["status"] == "healthy",
            cpu_status["status"] == "healthy",
        ])

        return {
            "status": "healthy" if all_healthy else "degraded",
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": self.get_uptime(),
            "version": "1.0.0",
            "components": {
                "database": db_status,
                "storage": storage_status,
                "memory": memory_status,
                "cpu": cpu_status,
            },
        }


class MetricsCollector:
    """指标收集器"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.metrics = {
            "api_requests": 0,
            "api_errors": 0,
            "api_latency_sum": 0.0,
            "api_latency_count": 0,
        }

    def record_request(self, latency: float, is_error: bool = False):
        """记录API请求"""
        self.metrics["api_requests"] += 1
        if is_error:
            self.metrics["api_errors"] += 1
        self.metrics["api_latency_sum"] += latency
        self.metrics["api_latency_count"] += 1

    def get_metrics(self) -> Dict[str, Any]:
        """获取指标"""
        avg_latency = 0
        if self.metrics["api_latency_count"] > 0:
            avg_latency = self.metrics["api_latency_sum"] / self.metrics["api_latency_count"]

        return {
            "api_requests": self.metrics["api_requests"],
            "api_errors": self.metrics["api_errors"],
            "api_error_rate": (
                self.metrics["api_errors"] / self.metrics["api_requests"]
                if self.metrics["api_requests"] > 0
                else 0
            ),
            "api_avg_latency_ms": avg_latency * 1000,
        }

    def get_database_stats(self) -> Dict[str, Any]:
        """获取数据库统计"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            stats = {}
            tables = ["playthroughs", "scenes", "attributes", "saves", "cross_playthrough_memories", "unlocked_endings"]

            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    stats[table] = cursor.fetchone()[0]
                except:
                    stats[table] = 0

            conn.close()
            return stats

        except Exception as e:
            return {"error": str(e)}

    def get_all_metrics(self) -> Dict[str, Any]:
        """获取所有指标"""
        return {
            "api": self.get_metrics(),
            "database": self.get_database_stats(),
            "timestamp": datetime.now().isoformat(),
        }
