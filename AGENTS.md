# Amphoreus 永劫回归模拟器 - AI Agent 开发指南

> 本项目为《崩坏：星穹铁道》的二次创作，仅供娱乐用途，严禁商用。版权归属米哈游所有。

## 项目概述

**Amphoreus**（永劫回归模拟器）是一个基于生成式 AI 的多智能体交互框架，灵感来源于《崩坏：星穹铁道》3.4 版本"翁法罗斯"主线剧情中的"永劫回归"设定。

项目尝试通过多轮 AI Agent 交互，模拟白厄杀死昔涟后的 33550336 次循环迭代（即第二次逐火之旅"永劫回归"），探索：
- 火种循环演化机制
- 智能体间的记忆传承与决策博弈
- AI 叙事与神谕式预言的结合

### 核心概念

- **黄金裔（Chrysos Heir）**：12 位 AI Agent，每位拥有独特的【路径（path）】和【原动力（drive）】
- **盗火行者（Black Heir）**：特殊的 Agent，负责劝说逐火者交出火种，跨迭代累积记忆
- **火种（Fireseed）**：Agent 的交互日志，代表记忆、行为轨迹、选择历史的封装
- **永劫回归**：多轮迭代循环，每轮结束后盗火行者收集火种进入下一轮

## 技术栈

- **编程语言**：Python 3.11+
- **大模型 API**：DeepSeek（主要）、InternLM、MiniMax（支持多提供商切换）
- **Web 可视化**：Streamlit
- **数据持久化**：JSON
- **构建工具**：CMake（C++ 可视化组件）

### 主要依赖

```
requests==2.32.5
python-dotenv==1.1.1
pandas
numpy
streamlit（需单独安装）
```

## 项目结构

```
Amphoreus/
├── app.py                          # Streamlit Web 应用入口
├── main/                           # 核心模拟逻辑
│   ├── main.py                     # 程序入口，永劫回归循环控制
│   ├── agent.py                    # Agent 类定义与行为逻辑
│   ├── stage.py                    # 单轮"舞台"流程管理
│   ├── data_export.py              # 数据导出为 JSON/CSV
│   ├── run_export.sh               # 导出脚本（Unix 环境）
│   └── config/                     # API 配置
│       ├── api_config.py           # API 客户端封装
│       ├── api_doc.txt             # API 使用说明
│       └── API_KEY.txt             # API 密钥（.gitignore 保护）
├── characters/                     # 角色配置数据
│   ├── entity_settings.json        # 角色路径、原动力等配置
│   ├── notes.json                  # 角色铭文、预言等扩展信息
│   └── entity_settings_text/       # 角色设定文本文件
├── images/                         # 角色头像图片
├── facilities/                     # 工具脚本
│   └── 2json.py                    # 文本配置转 JSON 工具
├── build/                          # CMake 构建输出（C++ 可视化）
├── talks.txt                       # 角色对话示例日志
├── Genesis.json                    # 创世涡心数据（预留）
├── .env                            # 环境变量（API 密钥）
└── requirements.txt                # Python 依赖
```

## 运行方式

### 1. 环境准备

```bash
# 创建虚拟环境
python -m venv .venv

# 激活环境（macOS/Linux）
source .venv/bin/activate

# 激活环境（Windows PowerShell）
.\.venv\Scripts\Activate.ps1
```

### 2. 配置 API Key

在项目根目录创建 `.env` 文件：

```env
DEEPSEEK_API_KEY=your_deepseek_api_key_here
INTERN_API_KEY=your_intern_api_key_here
MINIMAX_API_KEY=your_minimax_api_key_here

# 可选：自定义 API 基础 URL
DEEPSEEK_BASE_URL=https://api.deepseek.com
INTERN_BASE_URL=https://chat.intern-ai.org.cn/api/v1
MINIMAX_BASE_URL=https://api.minimaxi.com/v1
```

**安全提示**：`.env` 文件已加入 `.gitignore`，切勿提交到版本控制。

### 3. 安装依赖

```bash
pip install python-dotenv requests streamlit
pip install -r requirements.txt
```

### 4. 运行模拟

#### 命令行模式

```bash
python main/main.py
```

#### Web 可视化模式

```bash
streamlit run app.py
```

### 5. 导出结果

```bash
# Unix 环境（使用脚本）
./main/run_export.sh

# 或直接使用 Python
python main/data_export.py
```

## 代码架构

### 核心模块

#### 1. `agent.py` - Agent 定义

```python
class Chrysos_Heir:
    """黄金裔 Agent 类"""
    
    def __init__(self, name, path, drive, profile, state, memory):
        # name: 角色名
        # path: 路径（死亡、负世、浪漫等）
        # drive: 原动力（平和、憎恨、节制等）
        # profile: 角色背景描述
        # state: 精神状态 0-5
        # memory: 记忆列表
    
    def answer(self, question):      # 对话响应
    def reflect(self):               # 自我反思
    def make_decision(self, question):  # 做出决策（返回 0/1）
```

主要函数：
- `init_chrysos_heir()` - 初始化 12 位黄金裔
- `init_black_heir()` - 初始化盗火行者

#### 2. `stage.py` - 舞台流程

单轮迭代的核心流程：

1. **神谕发布** - 缇宝（HapLotes405）发布逐火神谕
2. **逐火决策** - 每位黄金裔决定是否逐火
3. **盗火行者劝诫** - 盗火行者劝说逐火者交出火种
4. **火种交托** - 逐火者决定是否交出火种
5. **顽固者劝说** - 对拒绝者进行多轮劝说
6. **强夺火种** - 仍拒绝者被强夺火种
7. **记忆承载** - 盗火行者收集所有火种，进入下一轮

关键函数：
- `run_one_iteration(black_heirs, max_persuasion_attempts)` - 运行单轮迭代
- `decode_decision_from_memory(name, last_memory)` - 解析 Agent 决策结果

#### 3. `main.py` - 主控循环

```python
def eternal_regression(rounds: int):
    """永劫回归主循环"""
    # 返回每轮迭代结果的日志字典

def eternal_regression_realtime_streaming(rounds: int):
    """流式版本，供 Streamlit 实时显示"""
    # 使用生成器逐事件返回结果
```

#### 4. `api_config.py` - API 封装

```python
class SimpleAPIClient:
    """支持多提供商的统一 API 客户端"""
    
    # 支持：deepseek、intern、minimax
    def chat(self, content, system_prompt=None, ...)
    def chat_stream(self, ...)  # 流式响应

class APIManager:
    """多客户端管理器"""
```

## 角色配置

角色配置位于 `main/agent.py` 中的 `heir_profiles` 字典：

```python
heir_profiles = {
    "EpieiKeia216": {  # 遐蝶
        "name": "遐蝶",
        "path": "死亡",
        "drive": "平和",
        "profile": "拥有夺走他人生命气息的双手...",
        "memory": ["预言...", "背景..."]
    },
    "NeiKos496": {  # 白厄
        "name": "白厄",
        "path": "负世",
        "drive": "憎恨",
        ...
    },
    # ... 其他 10 位黄金裔
}
```

现有角色（10 位）：
| ID | 名称 | 路径 | 原动力 |
|----|------|------|--------|
| EpieiKeia216 | 遐蝶 | 死亡 | 平和 |
| NeiKos496 | 白厄 | 负世 | 憎恨 |
| KaLos618 | 阿格莱雅 | 浪漫 | 节制 |
| HapLotes405 | 缇宝 | 门径 | 传递 |
| PoleMos600 | 万敌 | 纷争 | 约束 |
| HubRis504 | 刻律德菈 | 律法 | 支配 |
| EleOs252 | 风堇 | 天空 | 治愈 |
| ApoRia432 | 海瑟音 | 海洋 | 自否 |
| SkeMma720 | 那刻夏 | 理性 | 批判 |
| OreXis945 | 赛飞儿 | 诡计 | 渴望 |

## 开发约定

### 代码风格

- 使用中文注释说明业务逻辑
- 函数和变量使用英文命名（snake_case）
- 类名使用驼峰命名法
- 保留适当量的调试日志（`logging` 模块）

### 决策解析约定

Agent 的决策通过 `make_decision` 方法返回格式化的 JSON：

```python
{"decision": "0 或 1", "reason": "决策理由"}
```

解析逻辑在 `stage.decode_decision_from_memory()` 中实现：
1. 正则匹配
2. `json.loads` 解析
3. `ast.literal_eval` 解析
4. 失败时调用 AI 模型辅助解析

### 记忆累积规则

每轮迭代结束后，盗火行者的记忆按以下规则更新：
- **主动交出火种** 或 **被强夺火种** 的逐火者：继承全部记忆
- **不逐火** 的角色：仅继承第一条记忆

### API 调用重试机制

所有 API 调用均实现了重试机制：

```python
while response == '请求超时，请稍后重试':
    time.sleep(5)
    response = self.client.chat(question, prompt)
```

## 测试与调试

### 运行单元测试

各模块可直接运行进行测试：

```bash
# 测试 Agent 模块
python main/agent.py

# 测试单轮舞台
python main/stage.py

# 测试 API 配置
python main/config/api_config.py
```

### 调试技巧

1. **查看日志**：Web 模式下的日志会输出到终端
2. **调整迭代次数**：在 `app.py` 中通过滑块调整（1-20 轮）
3. **清空数据**：Web 界面提供"清空数据"按钮重置状态

## 扩展开发

### 添加新角色

1. 在 `agent.py` 的 `heir_profiles` 中添加角色配置
2. 在 `app.py` 的 `CHARACTER_AVATARS` 和 `CHARACTER_NAMES` 中添加对应条目
3. 准备角色头像图片放入 `images/` 目录

### 切换 API 提供商

修改 `agent.py` 中 `Chrysos_Heir.__init__` 的客户端初始化：

```python
# 当前使用 DeepSeek
self.client = SimpleAPIClient(provider="deepseek", model="deepseek-chat")

# 可切换为其他提供商
self.client = SimpleAPIClient(provider="intern", model="internlm3-latest")
self.client = SimpleAPIClient(provider="minimax", model="MiniMax-M1")
```

### 自定义流程

`stage.py` 中的 `run_one_iteration` 函数定义了完整的单轮流程，可在此处插入自定义的 checkpoint 或事件。

## 注意事项

1. **API 密钥安全**：切勿将 `.env` 或 API_KEY.txt 提交到版本控制
2. **成本控制**：每次完整模拟（6 轮）约需 50-100 次 API 调用，请注意用量
3. **响应时间**：单轮迭代约需 2-5 分钟，取决于 API 响应速度
4. **记忆长度**：随着迭代进行，盗火行者的记忆会累积，可能导致后续 API 调用成本增加

## 相关文件参考

- `README.md` - 项目介绍与快速开始
- `INTRODUCTION.txt` - 项目设计思路与讨论
- `talks.txt` - 角色对话示例与测试日志
- `characters/notes.json` - 角色铭文与预言配置
- `main/config/api_doc.txt` - 各 API 提供商使用示例
