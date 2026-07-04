"""
独立启动 Memora Connect Web 界面的脚本
"""
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from aiohttp import web
except ImportError:
    print("请先安装 aiohttp: pip install aiohttp")
    sys.exit(1)

from web.server import MemoryWebServer
from core.memory_system import MemorySystem


class SimpleMemorySystem:
    """简化的记忆系统，用于独立运行Web界面"""
    def __init__(self):
        self.memory_graph = None
        self.memory_config = {
            "enable_group_isolation": True,
            "max_memories": 1000,
            "consolidation_threshold": 0.7,
        }

    def load_memory_state(self, scope_id: str = ""):
        """加载记忆状态"""
        pass

    def get_all_memories(self, scope_id: str = "") -> list:
        """获取所有记忆"""
        return []

    def get_all_concepts(self, scope_id: str = "") -> list:
        """获取所有概念"""
        return []

    def get_memory_graph_data(self, scope_id: str = "") -> dict:
        """获取记忆图谱数据"""
        return {"nodes": [], "edges": []}


async def main():
    """启动Web服务器"""
    print("正在启动 Memora Connect Web 界面...")

    # 创建简化的记忆系统
    memory_system = SimpleMemorySystem()

    # 创建Web服务器
    server = MemoryWebServer(
        memory_system=memory_system,
        host="127.0.0.1",
        port=8350,
        access_token=""
    )

    try:
        await server.start()
        print(f"\n✅ Memora Connect Web 界面已启动!")
        print(f"🌐 请在浏览器中访问: http://127.0.0.1:8350")
        print(f"按 Ctrl+C 停止服务器\n")

        # 保持服务器运行
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n正在停止服务器...")
        await server.stop()
        print("服务器已停止")


if __name__ == "__main__":
    asyncio.run(main())
