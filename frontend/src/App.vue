<template>
  <div class="app-container">
    <!-- 配置面板 -->
    <div v-if="state.stage === 'config'" class="config-panel">
      <h1 class="glow-text highlight">Amphoreus System</h1>
      <p class="subtitle">>>> 交互式逐火协议 // 待命状态</p>

      <div class="form-group">
        <label>轮回迭代次数 [MAX_ROUNDS]:</label>
        <input
          type="number"
          v-model.number="configRounds"
          min="1"
          max="20"
          :disabled="isLoading"
        />
      </div>

      <div class="form-group">
        <label>访问口令 [PASSWORD]:</label>
        <input
          type="password"
          v-model="configPassword"
          placeholder="请输入神谕访问口令"
          :disabled="isLoading"
        />
      </div>

      <button @click="handleStart" class="start-btn" :disabled="isLoading || !configPassword">
        {{ isLoading ? '[ 连接中... ]' : '[ 开始逐火之旅 ]' }}
      </button>

      <div v-if="error" class="error-msg">{{ error }}</div>
    </div>

    <!-- 游戏主界面 -->
    <div v-else class="game-screen">
      <div class="game-header">
        <span class="highlight">
          SYS >> ROUND {{ state.round }} / {{ state.max_rounds }}
        </span>
        <span v-if="state.player_char_id" class="player-info">
          化身: {{ charNames[state.player_char_id] || state.player_char_id }}
        </span>
        <button class="reset-btn" @click="handleReset">[ 重置 ]</button>
      </div>

      <TerminalLog
        :events="displayedEvents"
        :char-names="charNames"
      />

      <!-- 流式指示器 -->
      <div v-if="isStreaming" class="streaming-bar">
        <span class="cursor">█</span>
        <span>正在接收神谕数据...</span>
      </div>

      <!-- 加载指示器 -->
      <div v-else-if="isLoading" class="streaming-bar">
        <span class="cursor">█</span>
        <span>等待回应...</span>
      </div>

      <!-- 交互选择面板 -->
      <ChoicePanel
        v-if="isWaitingForInput"
        :choices="state.choices"
        :stage="state.stage"
        :loading="isLoading"
        v-model="reason"
        @choose-character="handleChooseCharacter"
        @fire-decision="handleFireDecision"
        @handover-decision="handleHandoverDecision"
        @continue-round="handleContinue"
        @reset-game="handleReset"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

import TerminalLog from './components/TerminalLog.vue'
import ChoicePanel from './components/ChoicePanel.vue'
import { useGameSession } from './composables/useGameSession.js'

const {
  state,
  displayedEvents,
  charNames,
  isStreaming,
  isLoading,
  error,
  reason,
  isWaitingForInput,
  tryRestoreSession,
  startGame,
  chooseCharacter,
  submitFireDecision,
  submitHandoverDecision,
  submitHandoverRedecision,
  continueRound,
  resetGame,
} = useGameSession()

const configRounds = ref(1)
const configPassword = ref('')

onMounted(async () => {
  const restored = await tryRestoreSession()
  if (!restored) {
    configRounds.value = state.value.max_rounds || 1
    configPassword.value = state.value.password || ''
  } else {
    configPassword.value = state.value.password || ''
  }
})

async function handleStart() {
  await startGame(configRounds.value, configPassword.value)
}

async function handleChooseCharacter(char_id) {
  await chooseCharacter(char_id)
}

async function handleFireDecision(decision) {
  if (state.value.stage === 'fire_persuasion') {
    await submitFireDecision(decision)
  } else {
    await submitFireDecision(decision)
  }
}

async function handleHandoverDecision(decision) {
  if (state.value.stage === 'handover_persuasion') {
    await submitHandoverRedecision(decision)
  } else {
    await submitHandoverDecision(decision)
  }
}

async function handleContinue() {
  await continueRound()
}

function handleReset() {
  resetGame()
  configRounds.value = 1
}

</script>

<style scoped>
.app-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  padding: 20px;
}

.config-panel {
  background: rgba(13, 17, 29, 0.85);
  border: 1px solid var(--border-color);
  padding: 40px;
  border-radius: 8px;
  box-shadow: 0 0 20px rgba(0, 255, 255, 0.08);
  width: 420px;
}

.subtitle {
  margin-bottom: 30px;
  opacity: 0.7;
  font-size: 0.9em;
}

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

.start-btn:hover:not(:disabled) {
  background: var(--text-highlight);
  color: var(--bg-color-dark);
}

.start-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.error-msg {
  margin-top: 16px;
  color: #ff4d4d;
  font-size: 0.85em;
}

.game-screen {
  width: 100%;
  max-width: 960px;
  height: 90vh;
  background: rgba(0, 0, 0, 0.35);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: inset 0 0 30px rgba(0, 0, 0, 0.7);
}

.game-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px dashed var(--border-color);
  padding: 14px 16px;
  font-size: 0.9em;
}

.player-info {
  color: var(--text-primary);
  opacity: 0.85;
}

.reset-btn {
  background: transparent;
  color: var(--text-warn);
  border: none;
  cursor: pointer;
  font-family: inherit;
}

.reset-btn:hover {
  text-decoration: underline;
}

.streaming-bar {
  padding: 8px 16px;
  border-top: 1px solid var(--border-color);
  color: var(--text-highlight);
  font-size: 0.85em;
  display: flex;
  align-items: center;
  gap: 8px;
}

.cursor {
  display: inline-block;
  animation: blink 1s step-end infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border-color); }
</style>
