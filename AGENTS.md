# Amphoreus 永劫回归模拟器 - AI Agent 开发指南

> 本项目为《崩坏：星穹铁道》的二次创作，仅供娱乐用途，严禁商用。版权归属米哈游所有。

## 项目概述

**Amphoreus**（永劫回归模拟器）是一个基于生成式 AI 的多智能体交互框架，灵感来源于《崩坏：星穹铁道》3.4 版本"翁法罗斯"主线剧情中的"永劫回归"设定。

项目尝试通过多轮 AI Agent 交互，模拟白厄杀死昔涟后的 33550336 次循环迭代（即第二次逐火之旅"永劫回归"），探索：
- 火种循环演化机制
- 智能体间的记忆传承与决策博弈
- AI 叙事与神谕式预言的结合

### 核心概念

- **黄金裔（Chrysos Heir）**：10 位 AI Agent，每位拥有独特的【路径（path）】和【原动力（drive）】
- **盗火行者（Black Heir）**：特殊的 Agent，负责劝说逐火者交出火种，跨迭代累积记忆
- **火种（Fireseed）**：Agent 的交互日志，代表记忆、行为轨迹、选择历史的封装
- **永劫回归**：多轮迭代循环，每轮结束后盗火行者收集火种进入下一轮

## 技术栈

- **编程语言**：Python 3.11+
- **大模型 API**：DeepSeek（主要）、InternLM、MiniMax（支持多提供商切换）
- **Web API**：FastAPI + SSE 流式响应
- **前端**：Vue 3 + Vite
- **数据持久化**：JSON
- **容器化**：Docker + Docker Compose

### 主要依赖

```
requests==2.32.5
python-dotenv==1.1.1
pandas
numpy
fastapi
uvicorn
```

## 项目结构

```
Amphoreus/
├── app/
│   └── server.py                   # FastAPI Web 服务，提供 SSE 流式 API
├── frontend/                       # Vue 前端项目
│   ├── index.html                  # 页面入口
│   ├── src/
│   │   ├── main.js                 # Vue 挂载点
│   │   ├── App.vue                 # 核心组件
│   │   └── style.css               # CRT 终端样式
│   ├── package.json
│   └── vite.config.js
├── main/                           # 核心模拟逻辑
│   ├── main.py                     # 程序入口，永劫回归循环控制
│   ├── interactive_game.py         # 玩家扮演交互模式状态机
│   ├── agent.py                    # Agent 类定义与行为逻辑
│   ├── stage.py                    # 单轮"舞台"流程管理
│   ├── data_export.py              # 数据导出为 JSON
│   └── config/                     # API 配置
│       ├── api_config.py           # API 客户端封装
│       ├── api_doc.txt             # API 使用说明
│       └── API_KEY.txt             # API 密钥（.gitignore 保护）
├── characters/                     # 角色配置数据
│   ├── entity_settings.json        # 角色路径、原动力等配置
│   ├── notes.json                  # 角色铭文、预言等扩展信息
│   └── entity_settings_text/       # 角色设定文本文件
├── nginx/                          # Nginx 配置（Docker 部署用）
│   ├── default.conf                # Nginx 配置文件
│   ├── .htpasswd                   # 基础认证配置
│   └── index.html                  # 默认页面
├── images/                         # 角色头像图片
├── facilities/                     # 工具脚本
│   └── 2json.py                    # 文本配置转 JSON 工具
├── docker-compose.yml              # Docker Compose 配置
├── talks.txt                       # 角色对话示例日志
├── INTRODUCTION.txt                # 项目设计思路与讨论
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
.venv\Scripts\Activate.ps1
```

### 2. 配置 API Key

在项目根目录创建 `.env` 文件：

```env
# DeepSeek API（主要使用）
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat

# InternLM API（可选）
INTERN_API_KEY=your_intern_api_key_here
INTERN_BASE_URL=https://chat.intern-ai.org.cn/api/v1
INTERN_MODEL=internlm3-latest

# MiniMax API（可选）
MINIMAX_API_KEY=your_minimax_api_key_here
MINIMAX_BASE_URL=https://api.minimaxi.com/v1
MINIMAX_MODEL=MiniMax-M1
```

**安全提示**：`.env` 文件已加入 `.gitignore`，切勿提交到版本控制。

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 运行模拟

#### 命令行模式

```bash
python main/main.py
```

#### Web API 模式（FastAPI + SSE）

```bash
# 启动 FastAPI 服务
python app/server.py

# 或使用 uvicorn
uvicorn app.server:app --host 0.0.0.0 --port 8000
```

服务启动后，可通过 GET 请求访问 `/api/run_game` 接口：

```bash
curl "http://localhost:8000/api/run_game?password=33550336@Neikos496&max_iterations=6&max_persuasions=3"
```

#### 前端开发模式

```bash
cd frontend
npm install
npm run dev
```

前端服务启动在 http://localhost:5173

#### Docker 部署

```bash
docker-compose up -d
```

### 5. 导出结果

```bash
python main/data_export.py
```

## 代码架构

### 核心模块

#### 1. `agent.py` - Agent 定义

```python
class Chrysos_Heir:
    """黄金裔 Agent 类"""
    
    def __init__(self, char_id, client_provider="deepseek", client_model="deepseek-chat"):
        # char_id: 角色 ID，对应 prompts/characters/*.yaml
    
    def answer(self, question):      # 对话响应
    def reflect(self):               # 自我反思
    def make_decision(self, question):  # 做出决策（返回 0/1）
```

主要函数：
- `init_chrysos_heir()` - 初始化 10 位黄金裔
- `init_black_heir()` - 初始化盗火行者

角色配置已从 `agent.py` 迁移到 `prompts/characters/*.yaml`，由 `PromptManager` 统一管理。

**角色 ID 映射**（`CHARACTER_NAMES`）：

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
| SkeMma720 | 阿那克萨戈拉斯 | 理性 | 批判 |
| OreXis945 | 赛飞儿 | 诡计 | 渴望 |
| Black_NeiKo | 盗火行者·白厄 | 负世 | 憎恨 |

#### 1.5 `prompt_manager.py` - 提示词与角色配置管理器

`PromptManager` 负责从 `prompts/` 目录加载所有提示词和角色配置，并向 `agent.py`、`stage.py`、`main.py` 提供格式化后的提示词。

```python
from prompt_manager import get_prompt_manager

pm = get_prompt_manager()

# 获取角色配置
config = pm.get_character("EpieiKeia216")

# 获取渲染后的系统提示词
system = pm.get_system_prompt("EpieiKeia216", memory=[...])

# 获取场景问题
question = pm.get_scene_prompt("fire_decision", oracle="...", name="遐蝶", path="死亡", drive="平和")
```

**目录结构**：

```
prompts/
├── base/                      # 基础提示词模板
│   ├── system.md              # 黄金裔系统提示词
│   ├── black_heir_system.md   # 盗火行者系统提示词
│   ├── decision_format.md     # 决策输出格式
│   ├── self_reflection.md     # 自我反思引导
│   └── decode_fallback.md     # 决策解析兜底提示
├── scenes/                    # 场景问题提示词
│   ├── oracle.md
│   ├── intro.md
│   ├── fire_decision.md
│   ├── black_heir_persuade.md
│   ├── handover_decision.md
│   ├── persuade_target.md
│   ├── reconsider.md
│   ├── player_fire_decision.md
│   ├── player_handover_decision.md
│   └── fire_persuade_player.md
└── characters/                # 角色配置（YAML）
    ├── EpieiKeia216.yaml
    ├── ...
    └── black_heir/
        └── Black_NeiKo.yaml
```

**模板变量**：
- 角色配置中可使用 `{name}`、`{path}`、`{drive}`、`{profile}`、`{memory}`
- 场景提示词中可使用 `{name}`、`{path}`、`{drive}`、`{profile}`、`{memory}`、`{oracle}`、`{black_heir_word}`、`{target_name}`、`{attempt}` 等

#### 2. `stage.py` - 舞台流程

单轮迭代的核心流程：

1. **神谕发布** - 缇宝（HapLotes405）发布逐火神谕
2. **逐火决策** - 除缇宝外的每位黄金裔决定是否逐火（缇宝作为神谕发布者天然逐火）
3. **盗火行者劝诫** - 盗火行者劝说逐火者交出火种
4. **火种交托** - 所有逐火者（含缇宝）决定是否交出火种
5. **顽固者劝说** - 对拒绝者进行多轮劝说
6. **强夺火种** - 仍拒绝者被强夺火种
7. **记忆承载** - 盗火行者收集所有火种，进入下一轮

关键函数：
- `run_one_iteration(black_heirs, max_persuasion_attempts)` - 运行单轮迭代
- `decode_decision_from_memory(name, last_memory)` - 解析 Agent 决策结果

#### 3. `main.py` - 主控循环

```python
def eternal_regression(rounds: int, max_persuasion_attempts: int = 3):
    """永劫回归主循环（标准版）
    
    Args:
        rounds: 迭代次数
        max_persuasion_attempts: 每轮中盗火行者劝说顽固者的最大尝试次数，默认为3次
    """

def eternal_regression_realtime_streaming(rounds: int, max_persuasion_attempts: int = 3):
    """永劫回归流式版本（供 Web API 使用）
    
    Args:
        rounds: 迭代次数
        max_persuasion_attempts: 每轮中盗火行者劝说顽固者的最大尝试次数，默认为3次
    
    Yields:
        dict: 事件字典，格式为 {'type': 'oracle'|'decision'|'persuasion'|'result', ...}
        事件类型: start, round_start, oracle, fire_decision, fire_result, 
                 persuasion, handover_decision, handover_result, 
                 persuasion_attempt, persuasion_detail, handover_redecision, 
                 robbery, round_end, complete
    """

def analyze_regression_logs(logs_dict: dict):
    """分析永劫回归日志，提供统计洞察"""

def get_visualization_data(logs_dict):
    """将日志数据转换为可视化所需的格式"""
```

#### 4. `api_config.py` - API 封装

```python
class SimpleAPIClient:
    """支持多提供商的统一 API 客户端"""
    
    # 支持：deepseek、intern、minimax
    def __init__(self, provider, api_key=None, model=None)
    def chat(self, content, system_prompt=None, ...)
    def chat_stream(self, ...)  # 流式响应
    def get_response_time(self)  # 获取响应时间

class APIManager:
    """多客户端管理器，支持统一管理多个 API 提供商"""
    
    def add_client(self, name, provider, api_key=None, model=None)
    def chat(self, client_name, content, **kwargs)
    def get_all_response_times(self)
```

**环境变量支持**：
- `DEEPSEEK_API_KEY` / `DEEPSEEK_BASE_URL` / `DEEPSEEK_MODEL`
- `INTERN_API_KEY` / `INTERN_BASE_URL` / `INTERN_MODEL`
- `MINIMAX_API_KEY` / `MINIMAX_BASE_URL` / `MINIMAX_MODEL`

#### 5. `app/server.py` - FastAPI Web 服务

提供 SSE（Server-Sent Events）流式 API：

```python
@app.get("/api/run_game")
async def start_game_endpoint(
    password: str,
    max_iterations: int = 6,
    max_persuasions: int = 3
):
    """
    对外暴露的 API 接口 (GET)
    
    参数:
    - password: 访问密码（必须）
    - max_iterations: 迭代次数，默认6
    - max_persuasions: 最大劝说次数，默认3
    
    返回 StreamingResponse，media_type 为 text/event-stream
    """
```

**辅助函数**：
```python
def extract_reason_from_message(message: str) -> str:
    """
    从消息中提取 reason 字段
    如果消息是 JSON 格式且包含 reason 字段，则返回 reason 的内容
    否则返回原消息
    """
```

**请求格式：**
```
GET /api/run_game?password=33550336@Neikos496&max_iterations=6&max_persuasions=3
```

**响应格式（SSE）：**
```
data: >>> 启动永劫回归测试程序

data: >>> [第 1 轮永劫回归开始]

data: >>> [缇宝] 发布神谕:
data: {神谕内容}

data: >>> [遐蝶] 决定: 逐火
data:    理由: {reason字段内容}

data: [DONE]
```

**输出格式说明：**
- 使用 `>>>` 作为前缀标识，保持 CRT 终端风格
- JSON 格式的决策理由会自动提取 `reason` 字段内容
- 所有 SSE 事件都以 `data: ` 开头

### 交互式玩家扮演 API

除了自动运行的 SSE 模式，还提供一套有状态的多 Endpoint API，让玩家扮演其中一位黄金裔（除缇宝外），在关键决策点介入。

**流程**：
1. `POST /api/game/create` 创建会话
2. `POST /api/game/{session_id}/start` 开始游戏，返回开场文案、神谕、可选角色
3. `POST /api/game/{session_id}/choose` 玩家选择扮演角色
4. `POST /api/game/{session_id}/fire_decision` 玩家提交逐火决策（可填写理由）
   - 若玩家选择不逐火，缇宝与阿格莱雅会各劝一轮，stage 变为 `fire_persuasion`
   - 前端需再次调用本接口提交二次决策
5. `POST /api/game/{session_id}/handover_decision` 玩家提交交火种决策（可填写理由）
6. `POST /api/game/{session_id}/continue` 回合结束后继续下一回合
7. `GET /api/game/{session_id}/state` 随时查询当前状态

**请求示例**：
```bash
# 创建会话
curl -X POST http://localhost:8000/api/game/create \
  -H "Content-Type: application/json" \
  -d '{"max_rounds": 1}'

# 开始游戏
curl -X POST http://localhost:8000/api/game/{session_id}/start

# 选择角色
curl -X POST http://localhost:8000/api/game/{session_id}/choose \
  -H "Content-Type: application/json" \
  -d '{"char_id": "NeiKos496"}'

# 提交逐火决策（带理由）
curl -X POST http://localhost:8000/api/game/{session_id}/fire_decision \
  -H "Content-Type: application/json" \
  -d '{"decision": "1", "reason": "我是哀丽秘榭的白厄。"}'

# 提交交火种决策（不带理由，由AI生成）
curl -X POST http://localhost:8000/api/game/{session_id}/handover_decision \
  -H "Content-Type: application/json" \
  -d '{"decision": "0"}'
```

**统一响应结构**：
```json
{
  "session_id": "...",
  "stage": "fire_decision",
  "round": 1,
  "player_char_id": "NeiKos496",
  "events": [...],
  "choices": {
    "can_decide": true,
    "decision_type": "fire_decision",
    "target_char": "NeiKos496",
    "target_name": "白厄"
  },
  "fire_chasers_dict": {...},
  "robbed_characters": []
}
```

**核心文件**：
- `main/interactive_game.py`：游戏状态机与业务逻辑
- `app/server.py`：新增 7 个 REST endpoints
- `prompts/scenes/intro.md`：开场文案
- `prompts/scenes/player_fire_decision.md`：玩家逐火决策提示词
- `prompts/scenes/player_handover_decision.md`：玩家交火种决策提示词
- `prompts/scenes/fire_persuade_player.md`：缇宝/阿格莱雅劝说玩家逐火提示词

## 决策解析约定

Agent 的决策通过 `make_decision` 方法返回格式化的 JSON：

```python
{"decision": "0 或 1", "reason": "决策理由"}
```

解析逻辑在 `stage.decode_decision_from_memory()` 中实现：
1. 正则匹配
2. `json.loads` 解析
3. `ast.literal_eval` 解析
4. 失败时调用 AI 模型辅助解析

## 记忆累积规则

每轮迭代结束后，盗火行者的记忆按以下规则更新：
- **主动交出火种** 或 **被强夺火种** 的逐火者：继承全部记忆
- **不逐火** 的角色：仅继承第一条记忆
- 同时记录被强夺火种的角色列表

## API 调用重试机制

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

# 启动后端服务
python app/server.py

# 启动前端开发服务器
cd frontend && npm run dev
```

### 调试技巧

1. **查看日志**：API 调用会输出响应时间和错误信息
2. **调整迭代次数**：在 `main.py` 或 Web API 参数中调整
3. **切换 API 提供商**：修改 `agent.py` 中 `Chrysos_Heir` 的默认 `client_provider`/`client_model`

## 扩展开发

### 添加新角色

1. 在 `prompts/characters/` 下新增 `{char_id}.yaml`：
   ```yaml
   id: NewChar001
   name: 新角色名
   path: 命途
   drive: 原动力
   profile: >
     角色背景描述...
   memory:
     - 初始记忆1
     - 初始记忆2
   ```
2. 如需覆盖基础系统提示词，可在 YAML 中添加 `system_override: | ...`
3. `CHARACTER_NAMES` 会自动从 `PromptManager` 生成，无需手动维护

### 切换 API 提供商

修改 `agent.py` 中 `Chrysos_Heir.__init__` 的客户端初始化：

```python
# 当前使用 DeepSeek（默认）
self.client = SimpleAPIClient(provider="deepseek", model="deepseek-chat")

# 可切换为其他提供商
self.client = SimpleAPIClient(provider="intern", model="internlm3-latest")
self.client = SimpleAPIClient(provider="minimax", model="MiniMax-M1")
```

或通过环境变量配置默认模型。

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
- `characters/entity_settings.json` - 角色配置
- `characters/notes.json` - 角色铭文与预言
- `main/config/api_doc.txt` - 各 API 提供商使用示例
