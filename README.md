# Amphoreus: 永劫回归模拟器

## 项目背景

- 本项目基于游戏《崩坏星穹铁道》3.4版翁法罗斯主线剧情中，角色来古士的实验。尝试结合生成式人工智能的multi-agent交互框架，还原delta-me-13 （即翁法罗斯本体）的演算，复现部分游戏设定
- 由于技术所限，本项目不可能完全还原游戏设定，仅模拟白厄杀死昔涟后的33550336次循环迭代（即第二次逐火之旅“永劫回归”）
- 本项目属于游戏二次创作，严禁商用，部分提示词来自游戏文本，版权归米哈游所有
- 仅供娱乐，请勿过度解读

## 实验思路

我们设计了以下实验流程来模拟永劫回归：

1. **角色设定**：模拟 12 位“黄金裔”AI Agent，其中包含一位特殊的“圣女”角色（HapLotes405），负责发布神谕。
2. **迭代机制**：整个模拟过程分为多轮“永劫回归”迭代。每轮迭代中，AI Agent 们会经历一系列决策和交互。
3. **核心事件**：
    - **神谕发布**：圣女发布关于“逐火”的神谕。
    - **逐火决策**：所有黄金裔根据神谕，决定是否“逐火”（即是否追寻火种）。
    - **盗火行者劝说**：特殊的“盗火行者”AI Agent 出现，劝说逐火者交出火种。
    - **火种交出/强夺**：逐火者决定是否交出火种。对于不愿交出火种的顽固者，盗火行者会进行多轮劝说，若仍不成功，则会“强夺”火种。
    - **记忆累积**：每轮迭代结束后，盗火行者会收集所有逐火者的记忆（包括主动交出和被强夺火种的），并将其累积到自己的记忆库中，进入下一轮迭代。不逐火的黄金裔仅贡献第一条记忆。
4. **Checkpoint 与判定**：在每轮迭代的关键节点，我们会记录 AI Agent 的决策和交互结果，形成日志，用于后续分析 AI 行为模式的演变。

## 核心机制

- **多智能体交互**：模拟多个 AI Agent 之间的复杂对话和决策过程。
- **记忆累积与演化**：盗火行者通过累积多轮迭代的记忆，模拟知识和经验的传承，这可能影响其在后续迭代中的行为模式。
- **决策与劝说**：AI Agent 需根据当前情境和记忆做出决策，并参与到劝说与被劝说的过程中。
- **永劫回归循环**：通过多轮迭代，观察 AI Agent 在重复情境下的行为变化，探索“永劫回归”对智能体的影响。


## 代码构成

- main/main.py — 程序入口，负责解析运行参数、驱动多轮迭代（永劫回归循环），并汇总每轮日志/统计信息。
- main/agent.py — 定义 Agent 类与行为决策逻辑（黄金裔、圣女、盗火行者等），包含记忆读写与劝说/强夺流程。
- main/stage.py — 管理单轮“舞台”流程（神谕发布、逐火决策、劝说与火种交互、记忆收集与合并）。
- main/data_export.py — 将模拟结果导出为 JSON/CSV，用于后续分析与可视化。
- main/run_export.sh — 导出脚本（用于类 Unix 环境，Windows 可使用相应 Python 脚本或在 WSL/Git Bash 中运行）。
- config/api_config.py — 对接外部 API（如 DeepSeek）的配置与加载辅助逻辑。
- config/api_doc.txt — API 使用说明与示例（可参考）。
- __pycache__/ — Python 字节码缓存（自动生成，不需纳入版本控制）。

备注：
- 若添加新依赖，请将 requirements.txt 或在 README 中记录依赖列表。
- 建议将敏感信息（API Key）放到 .env 或系统环境变量，不要提交到版本控制。

## 如何运行

1. 环境准备（Windows）：
   - 安装 Python 3.11+（或与项目兼容的版本）。
   - 在项目根目录创建虚拟环境并激活（PowerShell）：
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
   - 或使用 CMD：
     ```cmd
     python -m venv .venv
     .\.venv\Scripts\activate
     ```

2. 配置 API Key：
   - 在项目根目录创建 `.env` 文件，写入：
     ```
     DEEPSEEK_API_KEY=your_deepseek_api_key_here
     ```
   - 或在 PowerShell 暂时设置（仅当前会话）：
     ```powershell
     $env:DEEPSEEK_API_KEY="your_deepseek_api_key_here"
     ```

3. 安装依赖：
   ```powershell
   pip install python-dotenv requests
   pip install -r requirements.txt
     ```

4. 运行模拟：
   ```powershell
   python main/main.py
   ```
   - 程序会按预设轮数执行永劫回归模拟，并在控制台输出每轮统计信息与最终分析。可在 main/ 下查找或配置结果导出位置。

5. 导出结果：
   - 在类 Unix 环境（WSL / Git Bash / macOS / Linux）可运行：
     ```bash
     ./main/run_export.sh
     ```
   - 或直接使用 Python 导出脚本（跨平台）：
     ```powershell
     python main/data_export.py
     ```

6. 常见提示：
   - 切勿将 `.env` 或含有真实 API Key 的文件提交到版本控制；建议在 .gitignore 中加入 `.env`。
   - 如需更改迭代轮数或日志级别，查看 main/main.py 中的参数或配置项并调整。



运行后，程序将执行预设轮数的永劫回归模拟，并输出每轮的统计信息和最终分析结果。
