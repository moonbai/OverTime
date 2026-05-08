# 加班管理系统 (OverTime)

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

一个基于 Python Tkinter 的加班管理系统，支持桌面应用和 Web 服务两种交互方式。

**主要特性：**
- 📝 加班/请假记录管理
- 🗓️ 智能节假日检测
- 💰 加班工资自动计算
- 🔔 多平台 Webhook 推送（飞书/钉钉/企微/Slack）
- 🌐 Web 网页端填报
- 📊 数据导入导出

---

## 📦 项目结构

```
OverTime/
├── core/                       # 核心模块
│   ├── __init__.py            # 包初始化（导出公共接口）
│   ├── config.py               # 配置管理器
│   ├── constants.py            # 常量定义
│   ├── data_manager.py         # 数据管理器
│   ├── models.py               # 数据模型
│   └── utils.py                # 工具函数
├── modules/                    # 业务模块
│   ├── __init__.py            # 包初始化
│   ├── holiday.py              # 节假日检查器
│   ├── holiday.json            # 节假日本地数据
│   ├── overtime.py            # 加班统计模块
│   ├── salary.py               # 工资计算模块
│   ├── leave.py                # 请假管理模块
│   ├── webhook.py              # Webhook 推送模块
│   └── web_service/            # Web 服务子模块
│       ├── __init__.py         # 包初始化
│       ├── server.py           # 服务启动器
│       ├── handlers.py         # 请求处理器
│       └── templates.py        # HTML 模板
├── ui/                         # UI 模块
│   ├── __init__.py            # 包初始化
│   ├── main_window.py          # 主窗口界面
│   └── settings_dialog.py      # 设置对话框
├── tests/                      # 单元测试
│   ├── __init__.py
│   ├── test_models.py          # 数据模型测试
│   └── test_utils.py           # 工具函数测试
├── scripts/                    # 辅助脚本
│   ├── install_deps.py         # 依赖安装
│   ├── check_env.py            # 环境检测
│   └── backup_data.py          # 数据备份
├── docs/                       # 文档
│   ├── README.md               # 项目说明
│   └── code_wiki.md            # 完整代码文档
├── data/                       # 数据目录
│   ├── overtime_records.csv    # 加班记录
│   └── backup/                 # 备份目录
├── main.py                     # 程序入口
├── system.py                   # 系统集成器
├── config.json                 # 配置文件（自动生成）
├── requirements.txt            # 依赖清单
├── pyproject.toml              # 项目配置（Python 打包）
└── .gitignore                  # Git 忽略文件
```

---

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Windows / Linux / macOS

### 安装依赖

```bash
# 克隆项目
git clone https://github.com/moonbai/OverTime.git
cd OverTime

# 安装核心依赖
pip install -r requirements.txt

# 或使用 pyproject.toml (推荐)
pip install -e .
```

### 运行程序

```bash
python main.py
```

### 可选依赖

| 依赖 | 安装命令 | 功能 |
|------|----------|------|
| `chinesecalendar` | `pip install chinesecalendar` | 节假日自动判断 |
| `openpyxl` | `pip install openpyxl` | Excel 导出 |

---

## 🎯 核心功能

### 1. 桌面应用

- **数据录入**：用户、日期、加班时长、请假类型
- **汇总统计**：月度工时统计、分类汇总
- **数据筛选**：按用户、日期、类型筛选记录
- **导入导出**：CSV/Excel 数据交换

### 2. Web 服务

启动服务后可通过浏览器访问：

```
http://localhost:8080          # 本机访问
http://<IP地址>:8080            # 局域网访问
```

支持的功能：
- 📝 网页端填报加班/请假
- 🔍 API 接口数据查询
- 📊 日期类型自动检测

### 3. Webhook 推送

支持多平台消息推送，消息字段拆分显示：

| 平台 | 消息格式 | 显示效果 |
|------|----------|----------|
| 飞书/Lark | Interactive 卡片 | 字段两列显示 + 按钮 |
| 钉钉 | Markdown | 分行列表 |
| 企业微信 | Text | 每行一个字段 |
| Slack | Block Kit | 字段分列显示 |

---

## 📊 架构设计

### 模块关系

```
┌─────────────────────────────────────────────────────┐
│                    main.py                          │
│                   (程序入口)                         │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│                   system.py                          │
│               (系统集成器)                            │
│  - 模块初始化                                        │
│  - 生命周期管理                                      │
└─────────────────────┬───────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│   UI 模块     │ │  业务模块     │ │  核心模块     │
│  main_window  │ │  overtime     │ │  config       │
│  settings     │ │  salary       │ │  data_manager │
│               │ │  leave        │ │  models       │
│               │ │  webhook      │ │  utils        │
│               │ │  holiday      │ │  constants    │
└───────────────┘ └───────────────┘ └───────────────┘
```

### 数据模型

| 模型 | 说明 |
|------|------|
| `OvertimeRecord` | 加班记录数据模型 |
| `MonthlySummary` | 月度汇总数据模型 |
| `SalaryConfig` | 工资配置数据模型 |
| `HolidayInfo` | 节假日信息数据模型 |
| `SubmitData` | 提交数据模型 |

---

## 🧪 测试

```bash
# 运行单元测试
python -m pytest tests/ -v

# 运行特定测试
python -m pytest tests/test_models.py -v
```

---

## ⚙️ 配置说明

### config.json

```json
{
  "last_user": "",
  "default_hours": "8",
  "page_size": 10,
  "web_port": 8080,
  "leave_types": ["事假", "病假", "年假", "婚假", "产假"],
  "deduct_rest_day_hours": true,
  "overtime_pay": {
    "enabled": false,
    "hourly_wage": 50.0,
    "weekday_rate": 1.0,
    "weekend_rate": 1.5,
    "holiday_rate": 2.0,
    "deduct_types": ["事假"]
  },
  "webhook": {
    "enabled": false,
    "url": "",
    "platform": "feishu",
    "timeout": 10,
    "retry": 3,
    "sync_mode": "sync"
  }
}
```

---

## 🔌 API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 网页填报界面 |
| `/api/data` | GET | 获取所有记录 |
| `/api/check_date?date=YYYY-MM-DD` | GET | 检测日期类型 |
| `/submit` | POST | 表单提交（网页） |
| `/api/submit` | POST | 数据提交（API） |
| `/status` | GET | 服务状态检查 |

---

## 🛠️ 开发指南

### 添加新模块

1. 在对应目录创建模块文件
2. 在 `__init__.py` 中导出
3. 在 `system.py` 中初始化

### 运行代码检查

```bash
# 安装工具
pip install black ruff

# 格式化代码
black .

# 代码检查
ruff check .
```

---

## 📝 更新日志

### v2.0 (2026-05)
- ✨ 新增数据模型 (`core/models.py`)
- ✨ 新增常量定义 (`core/constants.py`)
- ✨ 优化 Webhook 消息格式（字段拆分）
- ✨ 添加单元测试
- ✨ 新增 `pyproject.toml` 项目配置
- ✨ 添加 `.gitignore`
- 🔧 优化代码结构和类型注解

### v1.x
- 基础加班记录管理
- 节假日判断
- Web 服务支持
- Webhook 推送

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证

MIT License

---

## 💖 致谢

- [chinesecalendar](https://pypi.org/project/chinesecalendar/) - 节假日数据
- [tkcalendar](https://pypi.org/project/tkcalendar/) - 日期选择器
