# OverTime 加班管理系统 - Code Wiki

> **文档版本**: 2.0 (优化版)
> **更新时间**: 2024-01-15

## 项目概述

OverTime 是一个基于 Python Tkinter 开发的加班管理系统，提供桌面应用和 Web 服务两种交互方式。系统支持加班记录管理、节假日智能判断、加班工资计算、Webhook 推送等功能。

---

## 代码优化说明

### 优化要点

本次代码优化主要包含以下改进：

| 优化类别 | 具体改进 | 收益 |
|----------|----------|------|
| **类型注解** | 添加完整的函数返回值和参数类型注解 | 提升代码可读性，便于IDE智能提示 |
| **数据模型** | 新增 `core/models.py` 统一数据结构 | 消除硬编码，增强类型安全 |
| **常量管理** | 新增 `core/constants.py` 集中管理常量 | 消除魔法数字，便于维护 |
| **错误处理** | 改进异常捕获和验证逻辑 | 增强系统健壮性 |
| **代码复用** | 提取公共函数，消除重复代码 | 提升可维护性 |
| **Web服务** | 重构处理器，添加路由分发 | 代码结构更清晰 |
| **项目配置** | 新增 `pyproject.toml` | 支持现代Python打包工具 |

### 新增文件

```
core/
├── models.py          # 数据模型（新增）
├── constants.py       # 常量定义（新增）
└── __init__.py        # 包初始化（新增）

modules/
├── __init__.py        # 包初始化（新增）
└── web_service/
    └── __init__.py    # 包初始化（新增）

ui/
└── __init__.py        # 包初始化（新增）

tests/
├── __init__.py        # 测试包初始化
├── test_models.py     # 数据模型测试
└── test_utils.py      # 工具函数测试

pyproject.toml         # 项目配置（新增）
.gitignore            # Git忽略文件（新增）
```

---

## 项目架构

### 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        应用层 (Application)                     │
├─────────────────────────────────────────────────────────────────┤
│  main.py                    │  Web Service (8080端口)          │
│  └─ UI入口                  │  └─ /index.html (网页填报)        │
│                             │  └─ /api/data (数据接口)         │
│                             │  └─ /api/check_date (日期检测)   │
│                             │  └─ /submit (表单提交)           │
├─────────────────────────────────────────────────────────────────┤
│                        系统层 (System)                          │
├─────────────────────────────────────────────────────────────────┤
│  system.py - OvertimeSystem                                    │
│  ├─ 核心组件管理                                               │
│  ├─ 模块初始化                                                 │
│  └─ 生命周期管理                                               │
├─────────────────────────────────────────────────────────────────┤
│                        业务模块 (Modules)                       │
├─────────────────────────────────────────────────────────────────┤
│  modules/overtime.py    → 加班记录管理                          │
│  modules/holiday.py     → 节假日检测与判断                      │
│  modules/salary.py      → 加班工资计算                          │
│  modules/leave.py       → 请假管理                              │
│  modules/webhook.py     → Webhook推送 (飞书/钉钉/企微/Slack)    │
│  modules/web_service/   → HTTP服务模块                          │
│    ├─ server.py         → 服务启动与管理                        │
│    ├─ handlers.py       → 请求处理器                            │
│    └─ templates.py      → HTML模板                             │
├─────────────────────────────────────────────────────────────────┤
│                        核心模块 (Core)                          │
├─────────────────────────────────────────────────────────────────┤
│  core/config.py         → 配置管理 (config.json)                │
│  core/data_manager.py   → 数据持久化 (CSV/Excel)                │
│  core/utils.py          → 通用工具函数                          │
├─────────────────────────────────────────────────────────────────┤
│                        数据层 (Data)                           │
├─────────────────────────────────────────────────────────────────┤
│  data/overtime_records.csv    → 加班记录数据                    │
│  data/backup/                 → 备份目录                       │
│  modules/holiday.json         → 节假日配置 (可选)               │
│  config.json                  → 系统配置                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 目录结构

```
OverTime/
├── core/                    # 核心模块
│   ├── __init__.py         # 包初始化（导出公共接口）
│   ├── config.py           # 配置管理器
│   ├── constants.py       # 常量定义（新增）
│   ├── data_manager.py     # 数据管理器
│   ├── models.py           # 数据模型（新增）
│   └── utils.py            # 工具函数
├── modules/                # 业务模块
│   ├── __init__.py        # 包初始化（新增）
│   ├── web_service/        # Web服务子模块
│   │   ├── __init__.py    # 包初始化（新增）
│   │   ├── handlers.py     # HTTP请求处理器
│   │   ├── server.py       # Web服务启动器
│   │   └── templates.py    # HTML模板
│   ├── holiday.json        # 节假日数据配置(可选)
│   ├── holiday.py          # 节假日检查器
│   ├── leave.py            # 请假管理
│   ├── overtime.py         # 加班统计
│   ├── salary.py           # 工资计算
│   └── webhook.py          # Webhook推送
├── scripts/                # 辅助脚本
│   ├── backup_data.py      # 数据备份脚本
│   ├── check_env.py        # 环境检查脚本
│   └── install_deps.py     # 依赖安装脚本
├── tests/                  # 测试目录（新增）
│   ├── __init__.py         # 测试包初始化
│   ├── test_models.py      # 数据模型测试
│   └── test_utils.py       # 工具函数测试
├── ui/                     # UI模块
│   ├── __init__.py        # 包初始化（新增）
│   ├── main_window.py      # 主窗口界面
│   └── settings_dialog.py  # 设置对话框
├── main.py                 # 程序入口
├── system.py               # 系统集成器
├── requirements.txt        # 依赖清单
├── pyproject.toml          # 项目配置（新增）
├── .gitignore             # Git忽略文件（新增）
└── docs/                   # 文档目录
    ├── README.md           # 项目说明
    └── code_wiki.md        # 代码文档（本文件）
```

---

## 核心模块详解

### 1. 配置管理器 (core/config.py)

**功能定位**：统一管理系统配置，支持默认配置合并和运行时配置修改。

**核心类：ConfigManager**

| 方法 | 功能 | 参数 | 返回值 |
|------|------|------|--------|
| `__init__(config_file)` | 初始化配置管理器 | `config_file`: 配置文件路径，默认 `config.json` | - |
| `load_config()` | 加载配置，缺失项使用默认值 | - | `Dict[str, Any]` |
| `save_config()` | 保存配置到文件 | - | `bool` (成功/失败) |
| `get(key, default)` | 获取配置项，支持点号路径 | `key`: 配置键路径，如 `webhook.enabled` | 配置值或默认值 |
| `set(key, value)` | 设置配置项，支持点号路径 | `key`: 配置键路径；`value`: 配置值 | - |
| `reset_to_default()` | 重置为默认配置 | - | `bool` |

**默认配置结构**：

```python
DEFAULT_CONFIG = {
    'last_user': '',                    # 上次使用的用户名
    'default_hours': '8',               # 默认加班时长
    'page_size': 10,                    # 每页显示记录数
    'web_port': 8080,                   # Web服务端口
    'leave_types': ['事假', '病假', '年假', '婚假', '产假'],
    'deduct_rest_day_hours': True,      # 是否扣除休息日工时
    'overtime_pay': {                   # 加班工资配置
        'enabled': False,               # 是否启用
        'hourly_wage': 50.0,            # 小时加班工资
        'weekday_rate': 1.0,            # 工作日倍率
        'weekend_rate': 1.5,            # 休息日倍率
        'holiday_rate': 2.0,            # 节假日倍率
        'deduct_types': ['事假']         # 扣除工时的请假类型
    },
    'webhook': {                        # Webhook配置
        'enabled': False,
        'url': '',
        'platform': 'feishu',           # feishu/dingtalk/wechat/lark/slack/custom
        'headers': '{}',
        'timeout': 10,
        'retry': 3,
        'sync_mode': 'sync'
    },
    'modules': {                        # 模块开关
        'overtime': True,
        'salary': True,
        'leave': True,
        'webhook': True,
        'web_service': True,
        'holiday': True
    }
}
```

---

### 2. 数据管理器 (core/data_manager.py)

**功能定位**：负责加班记录的持久化存储，支持 CSV 文件操作和 Excel 导入导出。

**核心类：DataManager**

| 方法 | 功能 | 关键特性 |
|------|------|----------|
| `add_record(record)` | 添加记录到 CSV | 使用 UTF-8-sig 编码，兼容 Excel |
| `get_all_records()` | 获取所有记录 | 自动检测编码 (utf-8-sig/utf-8/gbk) |
| `get_monthly_records(month)` | 获取月度记录 | 按月份筛选 |
| `get_filtered_records(filters)` | 多条件筛选 | 支持用户、日期范围、类型筛选 |
| `import_csv(file_path)` | 导入外部 CSV | 支持多种编码和格式检测 |
| `export_excel(file_path)` | 导出为 Excel | 自动格式化表头和列宽 |
| `backup()` | 备份数据文件 | 自动生成时间戳文件名 |

**数据文件格式**：`data/overtime_records.csv`

| 字段 | 说明 | 示例 |
|------|------|------|
| 日期 | 记录日期 | 2024-01-15 |
| 用户 | 用户名 | 张三 |
| 类型 | 日期类型 | 工作日/休息日/节假日/调休日 |
| 加班时长 | 工时数 | 8.0 |
| 请假类型 | 请假类型 | 事假/病假/无 |
| 请假时长 | 请假工时 | -4 |
| 提交时间 | 记录时间 | 2024-01-15 10:30:00 |
| 加班工资 | 计算结果 | 400.00元 |

---

### 3. 工具函数 (core/utils.py)

| 函数 | 功能 | 参数 | 返回值 |
|------|------|------|--------|
| `validate_date(date_string)` | 验证日期格式 | `date_string`: 日期字符串 | `bool` |
| `format_timestamp()` | 获取格式化时间戳 | - | `str` (YYYY-MM-DD HH:MM:SS) |
| `get_local_ip()` | 获取本机IP地址 | - | `str` (IP地址或 localhost) |
| `get_web_service_url(port)` | 构建Web服务URL | `port`: 端口号 | `str` |
| `calculate_salary(hours, day_type, overtime_pay)` | 计算加班工资 | 工时、日期类型、工资配置 | `str` (格式化金额) |

---

## 业务模块详解

### 1. 节假日检查器 (modules/holiday.py)

**功能定位**：智能判断日期类型，支持两种数据源。

**核心类：HolidayChecker**

**数据源策略**：

| 数据源 | 特点 | 支持范围 |
|--------|------|----------|
| `chinese_calendar` | 自动判断，无需配置 | 2004-2026年 |
| `holiday.json` | 需手动配置，支持API格式 | 自定义年份 |

**日期类型映射**：

| detailsType | 日期类型 | 说明 |
|-------------|----------|------|
| 0 | 工作日 | 正常工作日 |
| 1 | 休息日 | 周末或普通节假日 |
| 2 | 休息日 | 普通节假日（如中秋、端午） |
| 3 | 节假日 | 三倍工资法定节假日（如国庆、春节） |

**核心方法**：

| 方法 | 功能 |
|------|------|
| `get_holiday_info(date_str)` | 获取完整节假日信息（星座、农历、节气等） |
| `get_day_type(date_str)` | 获取日期类型（工作日/休息日/节假日） |
| `get_supported_years()` | 获取支持的年份列表 |

---

### 2. 加班统计模块 (modules/overtime.py)

**功能定位**：处理加班记录的提交和统计。

**核心类：OvertimeModule**

| 方法 | 功能 |
|------|------|
| `get_monthly_summary(month)` | 获取月度汇总统计 |
| `submit_overtime(data)` | 提交加班记录 |

**月度汇总结构**：

```python
{
    "month": "2024-01",
    "total_hours": 48.5,
    "details": {
        "工作日": {"hours": 32.0, "count": 4},
        "休息日": {"hours": 12.0, "count": 2},
        "节假日": {"hours": 4.5, "count": 1},
        "调休日": {"hours": 0, "count": 0},
        "请假": {"hours": 0, "count": 0}
    },
    "empty": False
}
```

---

### 3. 工资计算模块 (modules/salary.py)

**功能定位**：根据日期类型计算加班工资。

**核心类：SalaryModule**

**计算公式**：
```
加班工资 = 小时加班工资 × 时长 × 倍率
```

**倍率规则**：

| 日期类型 | 默认倍率 | 说明 |
|----------|----------|------|
| 工作日 | 1.0 | 日常加班 |
| 休息日 | 1.5 | 周末加班 |
| 节假日 | 2.0 | 法定节假日 |
| 调休日 | 1.5 | 调休上班 |

---

### 4. 请假管理模块 (modules/leave.py)

**功能定位**：管理请假类型和工时扣除规则。

**核心类：LeaveModule**

| 方法 | 功能 |
|------|------|
| `get_leave_types()` | 获取请假类型列表 |
| `should_deduct_hours(leave_type)` | 判断是否扣除工时 |
| `process_leave(data)` | 处理请假数据，返回标准化结果 |

---

### 5. Webhook推送模块 (modules/webhook.py)

**功能定位**：支持多种平台的消息推送。

**核心类：WebhookModule**

**支持平台**：

| 平台 | 消息格式 | 特点 |
|------|----------|------|
| 飞书 (feishu) | Interactive卡片 | 支持按钮和跳转 |
| 钉钉 (dingtalk) | Markdown | 需配置安全关键词 |
| 企业微信 (wechat) | 文本消息 | 简单直接 |
| Lark | Interactive卡片 | 飞书国际版 |
| Slack | Block JSON | 国际团队协作 |
| 自定义 (custom) | JSON | 自定义Webhook |

**核心方法**：

| 方法 | 功能 |
|------|------|
| `send(data)` | 发送Webhook消息 |
| `test()` | 测试Webhook连接 |
| `get_supported_platforms()` | 获取支持的平台列表 |

---

### 6. Web服务模块 (modules/web_service/)

**功能定位**：提供HTTP服务，支持网页填报和API访问。

#### Server (server.py)

**核心类：WebServiceModule**

| 方法 | 功能 |
|------|------|
| `start()` | 启动Web服务，返回服务URL |
| `stop()` | 停止Web服务 |
| `is_running()` | 检查服务状态 |
| `register_callback(name, callback)` | 注册回调函数 |

#### Handlers (handlers.py)

**核心类：OvertimeWebHandler**

**HTTP接口**：

| 路径 | 方法 | 功能 |
|------|------|------|
| `/` | GET | 返回网页填报界面 |
| `/api/data` | GET | 获取记录数据（JSON） |
| `/api/check_date?date=YYYY-MM-DD` | GET | 检测日期类型 |
| `/submit` | POST | 提交表单（网页） |
| `/api/submit` | POST | 提交数据（API） |
| `/status` | GET | 服务状态检查 |

---

## UI模块详解

### 1. 主窗口 (ui/main_window.py)

**功能定位**：桌面应用主界面，包含三个标签页。

**标签页结构**：

| 标签页 | 功能 | 主要组件 |
|--------|------|----------|
| 📝 数据录入 | 提交加班/请假记录 | 用户输入、日期选择、类型选择、表单提交 |
| 📊 汇总统计 | 月度统计展示 | 各类型工时汇总、工资计算 |
| 🔍 数据筛选 | 记录查询和管理 | 条件筛选、分页浏览、导入导出 |

**核心方法**：

| 方法 | 功能 |
|------|------|
| `submit_record()` | 提交加班记录 |
| `auto_detect_day_type()` | 自动检测日期类型 |
| `refresh_records()` | 刷新记录列表 |
| `update_summary()` | 更新汇总统计 |
| `import_records()` | 导入CSV文件 |
| `export_to_excel()` | 导出Excel文件 |

---

### 2. 设置对话框 (ui/settings_dialog.py)

**功能定位**：系统配置管理界面。

**配置标签页**：

| 标签页 | 配置项 |
|--------|--------|
| 基础设置 | 默认用户、默认时长、每页记录数、依赖安装 |
| 请假配置 | 请假类型列表、工时扣除规则 |
| 加班工资 | 启用开关、小时工资、倍率配置 |
| 节假日数据 | 数据源选择、JSON配置 |
| Web服务/Webhook | 端口、平台、URL、高级设置、测试 |

---

## 系统集成器 (system.py)

**功能定位**：负责模块连接和生命周期管理。

**核心类：OvertimeSystem**

**初始化流程**：

```
1. 创建配置管理器 (ConfigManager)
2. 创建数据管理器 (DataManager)
3. 创建业务模块实例
   - HolidayChecker
   - OvertimeModule
   - SalaryModule
   - LeaveModule
   - WebhookModule
   - WebServiceModule
4. 设置Web服务回调函数
5. 创建主窗口UI
6. 绑定菜单栏和关闭事件
```

**回调函数注册**：

| 回调名称 | 功能 |
|----------|------|
| `get_html` | 返回网页模板 |
| `get_data` | 获取最新记录 |
| `check_date` | 检测日期类型 |
| `submit_record` | 提交记录 |

---

## 依赖关系

### 核心依赖

| 依赖 | 版本 | 用途 |
|------|------|------|
| `tkcalendar` | >=1.16.0 | 日期选择器组件 |
| `requests` | >=2.25.0 | HTTP请求（Webhook） |

### 推荐依赖

| 依赖 | 版本 | 用途 |
|------|------|------|
| `chinesecalendar` | >=1.11.0 | 节假日自动判断 |

### 可选依赖

| 依赖 | 版本 | 用途 |
|------|------|------|
| `openpyxl` | >=3.1.0 | Excel文件导出 |

### 安装命令

```bash
# 安装核心依赖
pip install tkcalendar>=1.16.0 requests>=2.25.0

# 安装推荐依赖
pip install chinesecalendar>=1.11.0

# 安装可选依赖
pip install openpyxl>=3.1.0
```

---

## 运行方式

### 环境要求

- Python 3.8+
- Windows/Linux/macOS

### 启动方式

**方式一：直接运行**

```bash
cd OverTime
python main.py
```

**方式二：安装依赖后运行**

```bash
cd OverTime
pip install -r requirements.txt
python main.py
```

### Web服务访问

启动应用后，点击「▶️ 启动」按钮启动Web服务，默认访问地址：

```
http://localhost:8080
```

### 命令行参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--help` | 显示帮助信息 | `python main.py --help` |

---

## 数据流程

### 记录提交流程

```
用户输入 → 日期类型检测 → 工资计算 → 数据持久化 → Webhook推送
              ↓
         节假日检查器
              ↓
         chinese_calendar / holiday.json
```

### Web服务数据流

```
浏览器 → HTTP请求 → OvertimeWebHandler → 回调函数 → 业务模块 → 数据管理器
     ↓                                              ↓
  HTML响应                                       CSV文件
```

---

## 配置文件说明

### config.json

```json
{
  "last_user": "张三",
  "default_hours": "8",
  "page_size": 10,
  "web_port": 8080,
  "leave_types": ["事假", "病假", "年假", "婚假", "产假"],
  "deduct_rest_day_hours": true,
  "overtime_pay": {
    "enabled": true,
    "hourly_wage": 50.0,
    "weekday_rate": 1.0,
    "weekend_rate": 1.5,
    "holiday_rate": 2.0,
    "deduct_types": ["事假"]
  },
  "webhook": {
    "enabled": true,
    "url": "https://open.feishu.cn/open-apis/bot/v2/hook/xxx",
    "platform": "feishu",
    "timeout": 10,
    "retry": 3,
    "sync_mode": "sync"
  },
  "use_builtin_holiday": false
}
```

### holiday.json 格式

支持两种格式：

**格式一：API响应格式**
```json
[
  {"month": 1, "year": 2024, "days": [
    {"date": "2024-01-01", "type": 2, "typeDes": "元旦", "detailsType": 3}
  ]}
]
```

**格式二：原始格式**
```json
{
  "2024": {
    "01-01": {"type": 2, "typeDes": "元旦", "detailsType": 3}
  }
}
```

---

## 扩展开发

### 添加新的Webhook平台

1. 在 `modules/webhook.py` 的 `platform_configs` 中添加平台配置
2. 在 `_format_payload()` 方法中添加格式处理逻辑
3. 在 `get_supported_platforms()` 中注册平台

### 添加新的数据源

1. 在 `modules/holiday.py` 中添加数据源检测逻辑
2. 实现 `get_holiday_info()` 和 `get_day_type()` 的适配

### 添加新的UI功能

1. 在 `ui/main_window.py` 中添加新的标签页或组件
2. 在对应的业务模块中实现核心逻辑

---

## 故障排除

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 日期检测失败 | chinese_calendar未安装 | `pip install chinesecalendar` |
| Excel导出失败 | openpyxl未安装 | `pip install openpyxl` |
| Web服务启动失败 | 端口被占用 | 修改 `web_port` 配置 |
| Webhook推送失败 | URL或平台配置错误 | 检查配置并测试连接 |
| CSV文件乱码 | 编码不兼容 | 使用UTF-8-sig编码保存 |

### 日志输出

系统启动时会输出以下信息：

```
============================================================
加班管理系统
============================================================
✓ 配置加载成功
✓ chinese_calendar 已安装
✓ holiday.json API格式加载成功
支持年份: ['2024', '2025', '2026']
✓ 创建数据目录: data
✓ 创建备份目录: data/backup
✓ CSV文件已存在: data/overtime_records.csv
============================================================
✓ 系统初始化完成
============================================================
```

---

## 版本历史

### v2.0
- 支持API格式节假日数据
- 按detailsType精确分类
- 普通节假日统计为休息日
- 三倍工资节假日单独识别

### v1.x
- 基础加班记录管理
- chinese_calendar集成
- Web服务支持
- Webhook推送（飞书/钉钉/企微）