"""
启动 Memora Connect 后端服务 + 前端
包含模拟数据和完整的 REST API
"""
import http.server
import json
import os
import socketserver
import sqlite3
import time
import uuid
from datetime import datetime
from urllib.parse import urlparse, parse_qs

PORT = 8352
WEB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_data.db")


def init_db():
    """初始化数据库并插入测试数据"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 创建表
    cur.execute('''CREATE TABLE IF NOT EXISTS concepts (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        created_at REAL,
        last_accessed REAL,
        access_count INTEGER DEFAULT 0
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS memories (
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
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS connections (
        id TEXT PRIMARY KEY,
        from_concept TEXT NOT NULL,
        to_concept TEXT NOT NULL,
        strength REAL DEFAULT 1.0,
        last_strengthened REAL,
        FOREIGN KEY (from_concept) REFERENCES concepts (id),
        FOREIGN KEY (to_concept) REFERENCES concepts (id)
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS impressions (
        id TEXT PRIMARY KEY,
        person_name TEXT NOT NULL,
        score REAL DEFAULT 50.0,
        tags TEXT DEFAULT '',
        notes TEXT DEFAULT '',
        created_at REAL,
        updated_at REAL
    )''')

    # 检查是否已有数据
    cur.execute("SELECT COUNT(*) FROM concepts")
    if cur.fetchone()[0] > 0:
        conn.close()
        return

    now = time.time()

    # 插入概念
    concepts = [
        ("c1", "工作", now - 86400 * 30),
        ("c2", "学习", now - 86400 * 25),
        ("c3", "生活", now - 86400 * 20),
        ("c4", "健康", now - 86400 * 15),
        ("c5", "兴趣", now - 86400 * 10),
        ("c6", "社交", now - 86400 * 5),
    ]
    cur.executemany(
        "INSERT INTO concepts (id, name, created_at, last_accessed, access_count) VALUES (?,?,?,?,?)",
        [(c[0], c[1], c[2], now, 5) for c in concepts],
    )

    # 插入记忆
    memories = [
        ("m1", "c1", "完成项目汇报", "今天向领导汇报了Q2工作成果，获得好评", "张经理, 李总监", "会议室A", "😊 成就", "工作,汇报,季度", now - 86400 * 2),
        ("m2", "c1", "加班修改方案", "客户需求变更，需要重新调整方案", "王同事", "办公室", "😅 疲惫", "工作,加班,方案", now - 86400),
        ("m3", "c2", "学习Python异步编程", "掌握了asyncio的基本用法", "", "家里", "📖 专注", "学习,python,编程", now - 86400 * 3),
        ("m4", "c2", "阅读《深度学习》第5章", "卷积神经网络的原理和应用", "", "图书馆", "🧠 思考", "学习,深度学习,CNN", now - 86400 * 4),
        ("m5", "c3", "周末去公园野餐", "天气很好，和朋友们一起享受阳光", "小明, 小红, 小李", "城市公园", "😄 开心", "生活,野餐,朋友", now - 86400 * 5),
        ("m6", "c3", "做了一道新菜", "尝试做了红烧肉，味道不错", "", "家里", "😋 满足", "生活,做饭,美食", now - 86400 * 6),
        ("m7", "c4", "跑步5公里", "晨跑感觉身体状态不错", "", "小区", "💪 活力", "健康,运动,跑步", now - 86400),
        ("m8", "c4", "体检报告出来了", "各项指标正常，继续保持", "", "医院", "😌 放心", "健康,体检", now - 86400 * 7),
        ("m9", "c5", "学习弹吉他", "正在练习《小星星》", "", "家里", "🎸 兴奋", "兴趣,音乐,吉他", now - 86400 * 2),
        ("m10", "c5", "看完一部电影", "《星际穿越》太震撼了", "", "家里", "🎬 感动", "兴趣,电影,科幻", now - 86400 * 3),
        ("m11", "c6", "参加同学聚会", "见到了很多老同学，聊得很开心", "张三, 李四, 王五", "餐厅", "🎉 热闹", "社交,聚会,同学", now - 86400 * 8),
        ("m12", "c6", "和朋友视频聊天", "和远在他乡的朋友聊了近况", "小王", "家里", "😊 温暖", "社交,视频,朋友", now - 86400 * 4),
    ]
    cur.executemany(
        "INSERT INTO memories (id, concept_id, content, details, participants, location, emotion, tags, created_at, last_accessed, access_count, strength, group_id) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        [(m[0], m[1], m[2], m[3], m[4], m[5], m[6], m[7], m[8], now, 3, 0.8, "") for m in memories],
    )

    # 插入连接
    connections = [
        ("conn1", "c1", "c2", 0.6),
        ("conn2", "c1", "c6", 0.4),
        ("conn3", "c2", "c5", 0.5),
        ("conn4", "c3", "c4", 0.7),
        ("conn5", "c3", "c5", 0.3),
        ("conn6", "c4", "c5", 0.2),
        ("conn7", "c5", "c6", 0.4),
    ]
    cur.executemany(
        "INSERT INTO connections (id, from_concept, to_concept, strength, last_strengthened) VALUES (?,?,?,?,?)",
        [(c[0], c[1], c[2], c[3], now) for c in connections],
    )

    # 插入印象
    impressions = [
        ("imp1", "张经理", 85.0, "领导,专业", "工作认真负责", now - 86400 * 30, now),
        ("imp2", "小明", 90.0, "朋友,幽默", "很好的朋友，性格开朗", now - 86400 * 60, now),
        ("imp3", "小红", 88.0, "朋友,细心", "做事很细心，很贴心", now - 86400 * 45, now),
        ("imp4", "王同事", 75.0, "同事,靠谱", "技术不错，合作愉快", now - 86400 * 20, now),
        ("imp5", "小李", 82.0, "朋友,热情", "很热情，组织能力强", now - 86400 * 50, now),
    ]
    cur.executemany(
        "INSERT INTO impressions (id, person_name, score, tags, notes, created_at, updated_at) VALUES (?,?,?,?,?,?,?)",
        impressions,
    )

    conn.commit()
    conn.close()
    print(f"✅ 测试数据已生成: {DB_PATH}")


class APIHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        # 静态文件
        if path == "/":
            self.send_file(os.path.join(WEB_DIR, "webui", "index.html"), "text/html")
        elif path.startswith("/static/"):
            file_name = path[8:]
            file_path = os.path.join(WEB_DIR, "static" if os.path.exists(os.path.join(WEB_DIR, "static", file_name)) else "webui", file_name)
            if not os.path.exists(file_path):
                file_path = os.path.join(WEB_DIR, "webui", file_name)
            content_type = "text/css" if file_name.endswith(".css") else "application/javascript"
            self.send_file(file_path, content_type)
        elif path == "/api/status":
            self.send_json({"memory_enabled": True, "db_path": DB_PATH, "web_enabled": True})
        elif path == "/api/groups":
            self.send_json({"groups": ["", "group1", "group2"]})
        elif path == "/api/concepts":
            concepts = self.query_db("SELECT id, name, created_at, last_accessed, access_count FROM concepts")
            self.send_json({"concepts": concepts})
        elif path == "/api/memories":
            group_id = params.get("group_id", [""])[0]
            if group_id:
                memories = self.query_db(
                    "SELECT id, concept_id, content, details, participants, location, emotion, tags, created_at, strength FROM memories WHERE group_id=?",
                    (group_id,),
                )
            else:
                memories = self.query_db("SELECT id, concept_id, content, details, participants, location, emotion, tags, created_at, strength FROM memories")
            self.send_json({"memories": memories})
        elif path == "/api/connections":
            self.send_json(self.query_db("SELECT id, from_concept, to_concept, strength FROM connections"))
        elif path == "/api/impressions":
            person = params.get("person", [""])[0]
            if person:
                # 返回特定人物的详细信息
                impression = self.query_db("SELECT id, person_name as name, score, tags, notes FROM impressions WHERE person_name=?", (person,))
                if impression:
                    imp = impression[0]
                    # 获取该人物相关的记忆
                    memories = self.query_db(
                        "SELECT id, content, emotion, strength FROM memories WHERE participants LIKE ?",
                        (f"%{person}%",),
                    )
                    self.send_json({
                        "summary": {
                            "name": imp["name"],
                            "summary": imp["notes"],
                            "score": imp["score"],
                            "tags": imp["tags"],
                        },
                        "memories": memories,
                    })
                else:
                    self.send_json({"summary": {}, "memories": []})
            else:
                # 返回所有印象列表
                impressions = self.query_db("SELECT id, person_name as name, score, tags, notes, created_at, updated_at FROM impressions")
                self.send_json({"people": impressions})
        elif path == "/api/graph":
            # 获取每个概念的记忆数量
            concepts = self.query_db("SELECT id, name FROM concepts")
            concept_counts = {}
            for c in concepts:
                count_result = self.query_db("SELECT COUNT(*) as cnt FROM memories WHERE concept_id=?", (c["id"],))
                concept_counts[c["id"]] = count_result[0]["cnt"] if count_result else 0

            nodes = [{"id": c["id"], "name": c["name"], "count": concept_counts.get(c["id"], 0)} for c in concepts]
            edges_raw = self.query_db("SELECT id, from_concept, to_concept, strength FROM connections")
            edges = [{"id": e["id"], "from_concept": e["from_concept"], "to_concept": e["to_concept"], "strength": e["strength"]} for e in edges_raw]
            self.send_json({"nodes": nodes, "edges": edges})
        else:
            self.send_error(404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        content_length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(content_length)) if content_length > 0 else {}

        if path == "/api/concepts":
            concept_id = str(uuid.uuid4())[:8]
            self.execute_db(
                "INSERT INTO concepts (id, name, created_at, last_accessed, access_count) VALUES (?,?,?,?,?)",
                (concept_id, body.get("name", ""), time.time(), time.time(), 0),
            )
            self.send_json({"id": concept_id, "name": body.get("name", "")})
        elif path == "/api/memories":
            memory_id = str(uuid.uuid4())[:8]
            self.execute_db(
                "INSERT INTO memories (id, concept_id, content, details, participants, location, emotion, tags, created_at, last_accessed, access_count, strength, group_id) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (memory_id, body.get("concept_id", ""), body.get("content", ""), body.get("details", ""), body.get("participants", ""), body.get("location", ""), body.get("emotion", ""), body.get("tags", ""), time.time(), time.time(), 0, 1.0, body.get("group_id", "")),
            )
            self.send_json({"id": memory_id})
        elif path == "/api/impressions":
            imp_id = str(uuid.uuid4())[:8]
            self.execute_db(
                "INSERT INTO impressions (id, person_name, score, tags, notes, created_at, updated_at) VALUES (?,?,?,?,?,?,?)",
                (imp_id, body.get("person_name", ""), body.get("score", 50), body.get("tags", ""), body.get("notes", ""), time.time(), time.time()),
            )
            self.send_json({"id": imp_id})
        else:
            self.send_error(404)

    def do_DELETE(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path.startswith("/api/concepts/"):
            concept_id = path.split("/")[-1]
            self.execute_db("DELETE FROM memories WHERE concept_id=?", (concept_id,))
            self.execute_db("DELETE FROM concepts WHERE id=?", (concept_id,))
            self.send_json({"ok": True})
        elif path.startswith("/api/memories/"):
            memory_id = path.split("/")[-1]
            self.execute_db("DELETE FROM memories WHERE id=?", (memory_id,))
            self.send_json({"ok": True})
        elif path.startswith("/api/impressions/"):
            imp_id = path.split("/")[-1]
            self.execute_db("DELETE FROM impressions WHERE id=?", (imp_id,))
            self.send_json({"ok": True})
        else:
            self.send_error(404)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def query_db(self, sql, params=()):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(sql, params)
        columns = [desc[0] for desc in cur.description] if cur.description else []
        rows = [dict(zip(columns, row)) for row in cur.fetchall()]
        conn.close()
        return rows

    def execute_db(self, sql, params=()):
        conn = sqlite3.connect(DB_PATH)
        conn.execute(sql, params)
        conn.commit()
        conn.close()

    def send_json(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def send_file(self, file_path, content_type):
        if os.path.exists(file_path):
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.end_headers()
            with open(file_path, "rb") as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404)

    def log_message(self, format, *args):
        print(f"[API] {args[0]}")


def main():
    print("🚀 初始化数据库和测试数据...")
    init_db()

    print(f"🌐 启动服务器...")
    with socketserver.TCPServer(("", PORT), APIHandler) as httpd:
        print(f"\n{'='*50}")
        print(f"✅ Memora Connect 已启动!")
        print(f"{'='*50}")
        print(f"🌐 前端地址: http://localhost:{PORT}")
        print(f"📡 API 地址: http://localhost:{PORT}/api/")
        print(f"{'='*50}")
        print(f"按 Ctrl+C 停止服务器\n")

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n正在停止服务器...")
            httpd.shutdown()
            print("服务器已停止")


if __name__ == "__main__":
    main()
