"""
生产环境服务器
包含健康检查、监控指标、备份管理等生产级功能
"""

import http.server
import json
import os
import signal
import socketserver
import sqlite3
import sys
import time
import threading
from datetime import datetime
from urllib.parse import urlparse, parse_qs

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.production import DATABASE, SERVER, LOGGING
from monitoring.health import HealthChecker, MetricsCollector
from monitoring.backup import BackupManager

PORT = SERVER["port"]
HOST = SERVER["host"]
DB_PATH = DATABASE["path"]
BACKUP_DIR = DATABASE["backup_path"]

# 全局变量
health_checker = None
metrics_collector = None
backup_manager = None
start_time = time.time()


def init_monitoring():
    """初始化监控系统"""
    global health_checker, metrics_collector, backup_manager

    health_checker = HealthChecker(DB_PATH)
    metrics_collector = MetricsCollector(DB_PATH)
    backup_manager = BackupManager(DB_PATH, BACKUP_DIR, DATABASE["max_backups"])

    print(f"监控系统初始化完成")
    print(f"  数据库: {DB_PATH}")
    print(f"  备份目录: {BACKUP_DIR}")


class ProductionHandler(http.server.BaseHTTPRequestHandler):
    """生产环境请求处理器"""

    def log_message(self, format, *args):
        """自定义日志格式"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {args[0]}")

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        # 健康检查端点
        if path == "/health":
            self.handle_health_check()
        # 监控指标端点
        elif path == "/metrics":
            self.handle_metrics()
        # 数据库统计端点
        elif path == "/metrics/database":
            self.handle_database_stats()
        # 备份列表端点
        elif path == "/backups":
            self.handle_list_backups()
        # 服务器信息端点
        elif path == "/info":
            self.handle_server_info()
        # API状态端点
        elif path == "/api/status":
            self.handle_api_status()
        # 静态文件
        elif path.startswith("/static/"):
            self.handle_static_file(path)
        # 主页
        elif path == "/":
            self.handle_index()
        else:
            self.send_error(404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(content_length)) if content_length > 0 else {}

        # 创建备份端点
        if path == "/backups":
            self.handle_create_backup(body)
        # 恢复备份端点
        elif path == "/backups/restore":
            self.handle_restore_backup(body)
        else:
            self.send_error(404)

    def do_DELETE(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path.startswith("/backups/"):
            backup_name = path.split("/")[-1]
            self.handle_delete_backup(backup_name)
        else:
            self.send_error(404)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    # ==================== 健康检查 ====================

    def handle_health_check(self):
        """处理健康检查请求"""
        health = health_checker.get_full_health_check()
        status_code = 200 if health["status"] == "healthy" else 503
        self.send_json(health, status_code)

    def handle_metrics(self):
        """处理监控指标请求"""
        metrics = metrics_collector.get_all_metrics()
        self.send_json(metrics)

    def handle_database_stats(self):
        """处理数据库统计请求"""
        stats = metrics_collector.get_database_stats()
        self.send_json(stats)

    def handle_server_info(self):
        """处理服务器信息请求"""
        info = {
            "name": "Memora Connect",
            "version": "1.0.0",
            "description": "无限流副本记忆系统",
            "uptime_seconds": time.time() - start_time,
            "start_time": datetime.fromtimestamp(start_time).isoformat(),
            "current_time": datetime.now().isoformat(),
            "python_version": sys.version,
            "pid": os.getpid(),
        }
        self.send_json(info)

    def handle_api_status(self):
        """处理API状态请求"""
        stats = metrics_collector.get_database_stats()
        status = {
            "memory_enabled": True,
            "db_path": DB_PATH,
            "web_enabled": True,
            "monitoring_enabled": True,
            "stats": stats,
        }
        self.send_json(status)

    # ==================== 备份管理 ====================

    def handle_list_backups(self):
        """处理备份列表请求"""
        backups = backup_manager.list_backups()
        self.send_json({"backups": backups, "total": len(backups)})

    def handle_create_backup(self, body):
        """处理创建备份请求"""
        name = body.get("name")
        try:
            backup_path = backup_manager.create_backup(name)
            backup_info = backup_manager.get_backup_info(backup_path)
            self.send_json({"success": True, "backup": backup_info})
        except Exception as e:
            self.send_json({"success": False, "error": str(e)}, 500)

    def handle_restore_backup(self, body):
        """处理恢复备份请求"""
        backup_path = body.get("backup_path")
        if not backup_path:
            self.send_json({"success": False, "error": "缺少backup_path参数"}, 400)
            return

        success = backup_manager.restore_backup(backup_path)
        if success:
            self.send_json({"success": True, "message": "备份恢复成功"})
        else:
            self.send_json({"success": False, "error": "备份恢复失败"}, 500)

    def handle_delete_backup(self, backup_name):
        """处理删除备份请求"""
        backup_path = os.path.join(BACKUP_DIR, backup_name)
        if os.path.exists(backup_path):
            os.remove(backup_path)
            self.send_json({"success": True, "message": f"备份 {backup_name} 已删除"})
        else:
            self.send_json({"success": False, "error": "备份不存在"}, 404)

    # ==================== 静态文件 ====================

    def handle_static_file(self, path):
        """处理静态文件请求"""
        file_name = path[8:]  # 移除 "/static/"
        file_path = os.path.join(os.path.dirname(__file__), "web", "static", file_name)

        if not os.path.exists(file_path):
            file_path = os.path.join(os.path.dirname(__file__), "web", "webui", file_name)

        if os.path.exists(file_path):
            content_type = "text/css" if file_name.endswith(".css") else "application/javascript"
            self.send_file(file_path, content_type)
        else:
            self.send_error(404)

    def handle_index(self):
        """处理主页请求"""
        index_path = os.path.join(os.path.dirname(__file__), "web", "webui", "index.html")
        if os.path.exists(index_path):
            self.send_file(index_path, "text/html")
        else:
            self.send_error(404)

    def send_file(self, file_path, content_type):
        """发送文件"""
        try:
            with open(file_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", len(content))
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500)

    def send_json(self, data, status_code=200):
        """发送JSON响应"""
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())


def auto_backup_task():
    """自动备份任务"""
    while True:
        try:
            time.sleep(DATABASE["auto_backup_interval"])
            backup_manager.create_backup("auto")
            backup_manager.cleanup_old_backups()
        except Exception as e:
            print(f"自动备份失败: {e}")


def signal_handler(signum, frame):
    """信号处理器"""
    print("\n正在停止服务器...")
    sys.exit(0)


def main():
    """主函数"""
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # 初始化监控系统
    init_monitoring()

    # 启动自动备份线程
    backup_thread = threading.Thread(target=auto_backup_task, daemon=True)
    backup_thread.start()

    print("=" * 60)
    print("Memora Connect 生产环境服务器")
    print("=" * 60)
    print(f"监听地址: {HOST}:{PORT}")
    print(f"数据库: {DB_PATH}")
    print(f"备份目录: {BACKUP_DIR}")
    print(f"自动备份间隔: {DATABASE['auto_backup_interval']}秒")
    print("=" * 60)
    print("可用端点:")
    print(f"  GET  /health          - 健康检查")
    print(f"  GET  /metrics         - 监控指标")
    print(f"  GET  /metrics/database - 数据库统计")
    print(f"  GET  /backups         - 备份列表")
    print(f"  POST /backups         - 创建备份")
    print(f"  GET  /info            - 服务器信息")
    print(f"  GET  /api/status      - API状态")
    print(f"  GET  /                - 前端界面")
    print("=" * 60)

    # 启动服务器
    with socketserver.TCPServer((HOST, PORT), ProductionHandler) as httpd:
        httpd.allow_reuse_address = True
        print(f"\n服务器已启动: http://{HOST}:{PORT}")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
