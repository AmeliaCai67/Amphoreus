# Amphoreus: 永劫回归模拟器

## 项目简介

基于《崩坏星穹铁道》3.4 版翁法罗斯主线剧情的多智能体 AI 实验项目。

尝试结合生成式人工智能的 Multi-Agent 交互框架，还原"永劫回归"的演算过程。

> ⚠️ 本项目属于游戏二次创作，严禁商用。部分提示词来自游戏文本，版权归米哈游所有。仅供娱乐，请勿过度解读。

---

## 核心机制

### 角色设定
- **12 位黄金裔 AI Agent** —— 每个角色有独特的命途、驱动力和性格
- **圣女**（HapLotes405 / 缇宝）—— 负责发布神谕
- **盗火行者**（Black_NeiKo / 白厄）—— 来自未来，收集火种与记忆

### 迭代流程
1. **神谕发布** —— 圣女发布关于"逐火"的神谕
2. **逐火决策** —— 黄金裔决定是否追随火种
3. **盗火/劝说** —— 盗火行者劝说交出火种，或"强夺"
4. **记忆累积** —— 盗火行者收集所有记忆，进入下一轮
5. **行为演化** —— 观察 AI 在循环中的行为变化

### 特色
- 🧠 **记忆累积** —— 每轮迭代后记忆会累积，影响后续决策
- 🔄 **多轮循环** —— 模拟"永劫回归"的无限循环
- 📊 **结果导出** —— 支持 JSON/CSV 格式分析

---

## 项目结构

```
Amphoreus/
├── main/
│   ├── main.py           # 程序入口，驱动多轮迭代
│   ├── agent.py          # Agent 类定义与角色初始化
│   ├── stage.py          # 单轮舞台流程
│   ├── data_export.py    # 结果导出
│   └── config/
│       ├── api_config.py # API 配置
│       └── api_doc.txt   # API 使用说明
├── characters/           # 角色设定文件
├── facilities/          # 设施配置
├── images/              # 角色图片
├── app.py               # 主程序
├── requirements.txt      # 依赖列表
└── README.md
```

---

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/AmeliaCai67/Amphoreus.git
cd Amphoreus
```

### 2. 创建虚拟环境

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate  # Windows
```

### 3. 配置 API Key

创建 `.env` 文件：

```env
DEEPSEEK_API_KEY=your_api_key_here
```

### 4. 安装依赖

```bash
pip install -r requirements.txt
```

### 5. 运行

```bash
python main/main.py
```

修改迭代轮数：`main/main.py` 中的 `rounds` 参数

---

## 输出示例

```
=== 开始永劫回归测试，共 6 轮迭代 ===

🔄 第 1 轮永劫回归开始
--------------------
神谕：...
逐火结果：{'EpieiKeia216': '逐火', 'NeiKos496': '逐火', ...}

📊 第 1 轮统计:
   逐火者总数: 8
   主动交出火种: 3
   被强夺火种: 2
   ...

🎯 永劫回归测试完成！共执行 6 轮迭代
```

---

## 技术栈

- Python 3.11+
- DeepSeek API (可切换至其他 LLM)
- 多智能体交互框架

---

## 注意事项

- 🔐 API Key 放在 `.env` 文件中，切勿提交到 Git
- 📝 如有新依赖，请更新 `requirements.txt`
- ⚙️ 调整参数请查看 `main/main.py`

---

## 相关链接

- [项目介绍](./INTRODUCTION.txt)
- [崩坏星穹铁道](https://sr.mihoyo.com/)

---

**Enjoy the eternal regression!**
