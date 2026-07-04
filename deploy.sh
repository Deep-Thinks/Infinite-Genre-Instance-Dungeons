#!/bin/bash
# Memora Connect 部署脚本

set -e

echo "=========================================="
echo "Memora Connect 部署脚本"
echo "=========================================="

# 检查Python版本
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python版本: $python_version"

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install psutil

# 创建必要目录
echo "创建必要目录..."
mkdir -p data/backups
mkdir -p data/assets
mkdir -p logs

# 复制环境变量文件
if [ ! -f ".env" ]; then
    echo "创建环境变量文件..."
    cp .env.example .env
    echo "请编辑 .env 文件配置环境变量"
fi

# 初始化数据库
echo "初始化数据库..."
python3 -c "
import sqlite3
import os

db_path = 'data/memora.db'
os.makedirs(os.path.dirname(db_path), exist_ok=True)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 创建表
tables = [
    '''CREATE TABLE IF NOT EXISTS concepts (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        created_at REAL,
        last_accessed REAL,
        access_count INTEGER DEFAULT 0
    )''',
    '''CREATE TABLE IF NOT EXISTS memories (
        id TEXT PRIMARY KEY,
        concept_id TEXT NOT NULL,
        content TEXT NOT NULL,
        details TEXT DEFAULT '',
        participants TEXT DEFAULT '',
        location TEXT DEFAULT '',
        emotion TEXT DEFAULT '',
        tags TEXT DEFAULT '',
        created_at REAL,
        last_accessed REAL,
        access_count INTEGER DEFAULT 0,
        strength REAL DEFAULT 1.0,
        group_id TEXT DEFAULT '',
        FOREIGN KEY (concept_id) REFERENCES concepts (id)
    )''',
    '''CREATE TABLE IF NOT EXISTS playthroughs (
        id TEXT PRIMARY KEY,
        playthrough_number INTEGER NOT NULL,
        status TEXT DEFAULT 'active',
        route TEXT,
        started_at REAL,
        completed_at REAL,
        ending TEXT,
        summary TEXT,
        created_at REAL,
        updated_at REAL
    )''',
    '''CREATE TABLE IF NOT EXISTS scenes (
        id TEXT PRIMARY KEY,
        playthrough_id TEXT NOT NULL,
        chapter TEXT NOT NULL,
        scene_number TEXT NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        status TEXT DEFAULT 'locked',
        progress INTEGER DEFAULT 0,
        sort_order INTEGER DEFAULT 0,
        created_at REAL,
        updated_at REAL,
        FOREIGN KEY (playthrough_id) REFERENCES playthroughs(id)
    )''',
]

for table_sql in tables:
    cursor.execute(table_sql)

conn.commit()
conn.close()
print('数据库初始化完成')
"

# 运行测试
echo "运行测试..."
python3 -m pytest tests/test_dungeon_workflow.py -v --tb=short

echo ""
echo "=========================================="
echo "部署完成!"
echo "=========================================="
echo ""
echo "启动服务器:"
echo "  开发环境: python3 start_backend.py"
echo "  生产环境: python3 production_server.py"
echo ""
echo "访问地址: http://localhost:8352"
echo "=========================================="
