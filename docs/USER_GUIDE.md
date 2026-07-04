# Memora Connect 用户指南

> **版本**: 1.0.0  
> **更新日期**: 2026-07-05

---

## 目录

- [快速开始](#快速开始)
- [功能介绍](#功能介绍)
- [副本工作流](#副本工作流)
- [API使用指南](#api使用指南)
- [配置说明](#配置说明)
- [常见问题](#常见问题)

---

## 快速开始

### 1. 安装

```bash
# 克隆仓库
git clone https://github.com/kaori-seasons/Infinite-Genre-Instance-Dungeons.git
cd Infinite-Genre-Instance-Dungeons

# 运行部署脚本
./deploy.sh
```

### 2. 启动服务

```bash
# 开发环境
python3 start_backend.py

# 生产环境
python3 production_server.py
```

### 3. 访问界面

打开浏览器访问: `http://localhost:8352`

---

## 功能介绍

### 核心功能

| 功能 | 说明 |
|------|------|
| **记忆系统** | 自动形成、存储、召回记忆 |
| **副本工作流** | 管理场景、周目、属性 |
| **回忆系统** | 跨周目记忆、结局追踪 |
| **存档系统** | 自动/手动存档、导入导出 |
| **可视化** | 记忆图谱、属性面板 |

### 副本工作流

- **场景时间线**: 按章节分组管理场景
- **属性面板**: 追踪角色属性变化
- **回忆系统**: 管理跨周目记忆和结局
- **存档管理**: 支持自动/手动存档

---

## 副本工作流

### 创建新周目

1. 点击左侧"副本"标签
2. 点击"新周目"按钮
3. 输入路线名称（可选）
4. 点击确定

### 管理场景

1. 在场景时间线中查看所有场景
2. 点击场景查看详情
3. 更新场景进度
4. 完成场景后自动解锁下一个

### 管理属性

1. 在右侧面板查看属性
2. 点击 +/- 按钮调整属性值
3. 点击属性查看变化历史

### 使用存档

1. 点击"手动存档"创建存档
2. 点击"加载"恢复存档
3. 点击"导出全部"导出存档

---

## API使用指南

### 基础端点

```bash
# 获取API状态
curl http://localhost:8352/api/status

# 获取周目列表
curl http://localhost:8352/api/playthroughs

# 创建新周目
curl -X POST http://localhost:8352/api/playthroughs \
  -H "Content-Type: application/json" \
  -d '{"route": "测试路线"}'
```

### 场景管理

```bash
# 获取场景时间线
curl http://localhost:8352/api/scenes/timeline/{playthrough_id}

# 创建场景
curl -X POST http://localhost:8352/api/scenes \
  -H "Content-Type: application/json" \
  -d '{
    "playthrough_id": "xxx",
    "chapter": "第一夜",
    "scene_number": "1-1",
    "name": "月光森林"
  }'

# 更新场景进度
curl -X PUT http://localhost:8352/api/scenes/{scene_id}/progress \
  -H "Content-Type: application/json" \
  -d '{"progress": 50}'
```

### 属性管理

```bash
# 获取属性列表
curl http://localhost:8352/api/attributes?playthrough_id=xxx

# 创建属性
curl -X POST http://localhost:8352/api/attributes \
  -H "Content-Type: application/json" \
  -d '{
    "playthrough_id": "xxx",
    "name": "狐族信任",
    "initial_value": 30
  }'

# 更新属性值
curl -X PUT http://localhost:8352/api/attributes/{attr_id} \
  -H "Content-Type: application/json" \
  -d '{"delta": 10, "reason": "完成任务"}'
```

### 存档管理

```bash
# 创建存档
curl -X POST http://localhost:8352/api/saves \
  -H "Content-Type: application/json" \
  -d '{
    "playthrough_id": "xxx",
    "save_type": "manual",
    "save_name": "我的存档",
    "save_data": {"step": 1}
  }'

# 加载存档
curl http://localhost:8352/api/saves/{save_id}

# 导出存档
curl -X POST http://localhost:8352/api/saves/{save_id}/export
```

### 回忆系统

```bash
# 获取回忆面板
curl http://localhost:8352/api/recall?playthrough_id=xxx

# 发现跨周目记忆
curl -X POST http://localhost:8352/api/recall/memories \
  -H "Content-Type: application/json" \
  -d '{
    "memory_content": "你在月光森林中醒来",
    "playthrough_id": "xxx"
  }'

# 解锁结局
curl -X POST http://localhost:8352/api/recall/endings \
  -H "Content-Type: application/json" \
  -d '{
    "ending_name": "好结局",
    "playthrough_id": "xxx"
  }'

# 获取命运地图
curl http://localhost:8352/api/recall/destiny-map
```

---

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DATABASE_PATH` | 数据库路径 | `./data/memora.db` |
| `SERVER_PORT` | 监听端口 | `8352` |
| `ACCESS_TOKEN` | 访问令牌 | 空 |
| `LOG_LEVEL` | 日志级别 | `INFO` |

### 配置文件

生产环境配置位于 `config/production.py`

---

## 常见问题

### Q: 如何备份数据？

```bash
# 手动备份
curl -X POST http://localhost:8352/backups

# 查看备份列表
curl http://localhost:8352/backups
```

### Q: 如何查看系统状态？

```bash
# 健康检查
curl http://localhost:8352/health

# 监控指标
curl http://localhost:8352/metrics
```

### Q: 如何重置数据库？

```bash
# 停止服务
pkill -f production_server.py

# 删除数据库
rm -f data/memora.db

# 重启服务
python3 production_server.py
```

---

## 技术支持

- **GitHub**: https://github.com/kaori-seasons/Infinite-Genre-Instance-Dungeons
- **Issues**: https://github.com/kaori-seasons/Infinite-Genre-Instance-Dungeons/issues

---

**文档维护者**: kaori-seasons  
**最后更新**: 2026-07-05
