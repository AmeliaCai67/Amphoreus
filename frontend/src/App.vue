<template>
  <div class="app-container">
    <div v-if="!isStarted" class="config-panel">
      <h1 class="glow-text highlight">Amphoreus System</h1>
      <p class="subtitle">>>> 永劫回归协议 // 待命状态</p>
      
      <div class="form-group">
        <label>访问口令 [PASSWORD]:</label>
        <input type="password" v-model="config.password" placeholder="请输入口令" />
      </div>

      <div class="form-group">
        <label>轮回迭代次数 [ITERATIONS: 1-6]:</label>
        <input type="number" v-model="config.max_iterations" min="1" max="6" />
      </div>

      <div class="form-group">
        <label>最大劝说次数 [PERSUASIONS: 1-3]:</label>
        <input type="number" v-model="config.max_persuasions" min="1" max="3" />
      </div>

      <button @click="startGame" class="start-btn">[ 执行启动程序 ]</button>
    </div>

    <div v-else class="terminal-screen" ref="terminalRef">
      <div class="terminal-header">
        <span class="highlight">SYS >> CONNECTION ESTABLISHED</span>
        <button class="stop-btn" @click="stopGame">[ 中止迭代 ]</button>
      </div>
      
      <div class="log-container">
        <div v-for="(log, index) in logs" :key="index" class="log-line">
          {{ log }}
        </div>
        <div v-if="isRunning" class="cursor">█</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'

// 状态管理
const isStarted = ref(false)
const isRunning = ref(false)
const logs = ref([])
const terminalRef = ref(null)
let eventSource = null

// 配置表单数据
const config = ref({
  password: '',
  max_iterations: 6,
  max_persuasions: 3
})

// 自动滚动到终端底部
const scrollToBottom = async () => {
  await nextTick() // 等待 DOM 更新完成
  if (terminalRef.value) {
    terminalRef.value.scrollTop = terminalRef.value.scrollHeight
  }
}

// 启动游戏逻辑
const startGame = () => {
  if (!config.value.password) {
    alert("请输入访问口令！")
    return
  }
  
  isStarted.value = true
  isRunning.value = true
  logs.value = [] // 清空旧日志
  
  // 组装 URL 参数 (配合后端的 GET 请求)
  const params = new URLSearchParams({
    password: config.value.password,
    max_iterations: config.value.max_iterations,
    max_persuasions: config.value.max_persuasions
  }).toString()

  // 发起 SSE 连接 (注意替换为你的后端实际地址)
  eventSource = new EventSource(`http://127.0.0.1:8000/api/run_game?${params}`)

  // 接收到后端的数据
  eventSource.onmessage = (event) => {
    if (event.data === "[DONE]") {
      isRunning.value = false
      eventSource.close()
      logs.value.push(">>> 永劫回归迭代已完成。")
      scrollToBottom()
      return
    }
    
    // 将接收到的数据加入日志数组
    logs.value.push(event.data)
    scrollToBottom()
  }

  // 处理连接错误
  eventSource.onerror = (error) => {
    console.error("SSE Error:", error)
    logs.value.push(">>> [系统警告] 信号连接丢失。")
    isRunning.value = false
    eventSource.close()
  }
}

// 强行中止
const stopGame = () => {
  if (eventSource) {
    eventSource.close()
  }
  isRunning.value = false
  logs.value.push(">>> [系统警告] 强制手动阻断。")
  setTimeout(() => {
    isStarted.value = false // 2秒后退回配置页
  }, 2000)
}
</script>

<style scoped>
/* 这个区域只对 App.vue 生效 */
.app-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  padding: 20px;
}

/* === 配置面板样式 === */
.config-panel {
  background: rgba(13, 17, 29, 0.8);
  border: 1px solid var(--border-color);
  padding: 40px;
  border-radius: 8px;
  box-shadow: 0 0 20px rgba(0, 255, 255, 0.1);
  width: 400px;
}

.subtitle { margin-bottom: 30px; opacity: 0.7; font-size: 0.9em; }

.form-group {
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
}

.form-group label {
  margin-bottom: 8px;
  font-size: 0.85em;
  color: var(--text-highlight);
}

.form-group input {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  padding: 10px;
  font-family: inherit;
  outline: none;
  transition: all 0.3s;
}

.form-group input:focus {
  border-color: var(--text-highlight);
  box-shadow: 0 0 10px rgba(0, 255, 255, 0.2);
}

.start-btn {
  width: 100%;
  margin-top: 20px;
  padding: 12px;
  background: transparent;
  color: var(--text-highlight);
  border: 1px solid var(--text-highlight);
  font-family: inherit;
  cursor: pointer;
  transition: all 0.3s;
}

.start-btn:hover {
  background: var(--text-highlight);
  color: var(--bg-color-dark);
}

/* === 终端屏幕样式 === */
.terminal-screen {
  width: 100%;
  max-width: 900px;
  height: 85vh;
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  padding: 20px;
  overflow-y: auto; /* 允许滚动 */
  box-shadow: inset 0 0 20px rgba(0,0,0,0.8);
}

.terminal-header {
  display: flex;
  justify-content: space-between;
  border-bottom: 1px dashed var(--border-color);
  padding-bottom: 10px;
  margin-bottom: 20px;
}

.stop-btn {
  background: transparent;
  color: var(--text-warn);
  border: none;
  cursor: pointer;
  font-family: inherit;
}
.stop-btn:hover { text-decoration: underline; }

.log-line {
  margin-bottom: 8px;
  line-height: 1.5;
  white-space: pre-wrap; /* 保持后端传来的换行和空格 */
}

/* 闪烁光标特效 */
.cursor {
  display: inline-block;
  color: var(--text-highlight);
  animation: blink 1s step-end infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

/* 自定义滚动条 */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border-color); }
</style>