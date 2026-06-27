<template>
  <div class="terminal-logs" ref="logsRef" @scroll="onScroll">
    <div
      v-for="(event, index) in events"
      :key="index"
      class="log-entry"
      :class="`type-${event.type}`"
    >
      <!-- 开场 -->
      <template v-if="event.type === 'intro'">
        <div class="log-label">>>> 系统初始化</div>
        <pre class="log-message intro-text">{{ event.message }}</pre>
      </template>

      <!-- 神谕 -->
      <template v-else-if="event.type === 'oracle'">
        <div class="log-label highlight">
          >>> [{{ event.char_name || event.char_id }}] 发布神谕
        </div>
        <pre class="log-message oracle-text">{{ event.message }}</pre>
      </template>

      <!-- 轮次开始 -->
      <template v-else-if="event.type === 'round_start'">
        <div class="log-divider"></div>
        <div class="log-label warn">{{ event.message }}</div>
      </template>

      <!-- 角色选择 -->
      <template v-else-if="event.type === 'character_chosen'">
        <div class="log-label">
          >>> 你选择了扮演 <span class="highlight">{{ event.char_name }}</span>
        </div>
      </template>

      <!-- 提问：逐火 / 交火种 -->
      <template v-else-if="['fire_question', 'handover_question'].includes(event.type)">
        <div class="log-label">>>> {{ event.type === 'fire_question' ? '逐火之问' : '交火种之问' }}</div>
        <pre class="log-message question-text">{{ event.message }}</pre>
      </template>

      <!-- 玩家/AI 决策 -->
      <template v-else-if="['fire_decision', 'handover_decision'].includes(event.type)">
        <div class="log-decision">
          <span class="log-actor">[{{ event.char_name || event.char_id }}]</span>
          <span class="log-decision-text" :class="event.decision === '1' ? 'success' : 'danger'">
            {{ event.decision_text }}
          </span>
          <span v-if="event.is_player" class="player-tag">玩家</span>
        </div>
        <div v-if="event.reason" class="log-reason">
          {{ event.reason }}
        </div>
      </template>

      <!-- 决策结果汇总 -->
      <template v-else-if="event.type === 'fire_result'">
        <div class="log-label">>>> 逐火结果</div>
        <div class="log-dict">
          <div v-for="(status, cid) in event.result" :key="cid" class="log-dict-item">
            <span class="log-dict-key">{{ charName(cid) }}:</span>
            <span class="log-dict-value">{{ status }}</span>
          </div>
        </div>
      </template>

      <template v-else-if="event.type === 'fire_result_update'">
        <div class="log-label">>>> {{ event.message }}</div>
      </template>

      <!-- 劝说 -->
      <template v-else-if="event.type === 'persuasion'">
        <div class="log-label">>>> 盗火行者劝诫</div>
        <pre class="log-message persuasion-text">{{ event.message }}</pre>
      </template>

      <template v-else-if="event.type === 'fire_persuasion'">
        <div class="log-label">
          >>> [{{ event.persuader_name }}] 劝说 [{{ event.target_name }}]
        </div>
        <pre class="log-message persuasion-text">{{ event.message }}</pre>
      </template>

      <template v-else-if="event.type === 'persuasion_attempt'">
        <div class="log-label warn">
          >>> 第 {{ event.attempt }} 次劝说 | 目标: {{ event.targets.map(charName).join(', ') }}
        </div>
      </template>

      <template v-else-if="event.type === 'persuasion_detail'">
        <div class="log-label">
          >>> [{{ event.persuader_name }}] 对 [{{ event.target_name }}]
        </div>
        <pre class="log-message persuasion-text">{{ event.message }}</pre>
      </template>

      <!-- 重新决策 -->
      <template v-else-if="event.type === 'handover_redecision'">
        <div class="log-decision">
          <span class="log-actor">[{{ event.char_name || event.char_id }}]</span>
          <span class="log-decision-text" :class="event.decision === '1' ? 'success' : 'danger'">
            {{ event.decision_text }}
          </span>
          <span v-if="event.is_player" class="player-tag">玩家</span>
        </div>
        <div v-if="extractReason(event.message)" class="log-reason">
          {{ extractReason(event.message) }}
        </div>
      </template>

      <!-- 强夺 -->
      <template v-else-if="event.type === 'robbery'">
        <div class="log-label danger">
          >>> [{{ event.char_name || event.char_id }}] 的火种被强夺！
        </div>
      </template>

      <!-- 回合结束 -->
      <template v-else-if="event.type === 'round_end'">
        <div class="log-divider"></div>
        <div class="log-label highlight">>>> 第 {{ event.round_num }} 轮最终结果</div>
        <div class="log-dict">
          <div v-for="(status, cid) in event.final_result" :key="cid" class="log-dict-item">
            <span class="log-dict-key">{{ charName(cid) }}:</span>
            <span class="log-dict-value">{{ status }}</span>
          </div>
        </div>
        <div v-if="event.robbed_characters?.length" class="log-label danger">
          >>> 被强夺: {{ event.robbed_characters.map(charName).join(', ') }}
        </div>
      </template>

      <!-- 完成 -->
      <template v-else-if="event.type === 'complete'">
        <div class="log-divider"></div>
        <div class="log-label highlight">{{ event.message }}</div>
      </template>

      <!-- 兜底 -->
      <template v-else>
        <pre class="log-message">{{ JSON.stringify(event, null, 2) }}</pre>
      </template>
    </div>
    <button
      v-if="showScrollButton"
      class="scroll-to-bottom"
      @click="scrollToBottom"
      title="跳到底部"
    >
      ↓
    </button>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  events: { type: Array, required: true },
  charNames: { type: Object, default: () => ({}) },
})

const logsRef = ref(null)
const showScrollButton = ref(false)
const SCROLL_THRESHOLD = 80

function charName(cid) {
  return props.charNames[cid] || cid
}

function extractReason(message) {
  if (!message || typeof message !== 'string') return ''
  let text = message.trim()
  if (text.startsWith('```')) {
    const lines = text.split('\n')
    text = lines.length > 2
      ? lines.slice(1, -1).join('\n').trim()
      : text.replace(/```/g, '').trim()
  }
  if (text.includes('reason')) {
    try {
      const match = text.match(/['"]reason['"]\s*:\s*['"](.+?)['"](?:,|\})/s)
      if (match) return match[1].trim()
      const data = JSON.parse(text)
      if (data && typeof data.reason === 'string') return data.reason.trim()
    } catch {
      // ignore
    }
  }
  return ''
}

function onScroll() {
  if (!logsRef.value) return
  const { scrollTop, scrollHeight, clientHeight } = logsRef.value
  showScrollButton.value = scrollHeight - scrollTop - clientHeight > SCROLL_THRESHOLD
}

async function scrollToBottom() {
  await nextTick()
  if (logsRef.value) {
    logsRef.value.scrollTop = logsRef.value.scrollHeight
  }
}

watch(
  () => props.events.length,
  async () => {
    await scrollToBottom()
  }
)

onMounted(() => {
  onScroll()
})

onUnmounted(() => {
  // 无需清理 window 事件，scroll 监听绑定在元素上
})

defineExpose({ logsRef, scrollToBottom })
</script>

<style scoped>
.terminal-logs {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  font-size: 0.95rem;
  line-height: 1.6;
  position: relative;
}

.scroll-to-bottom {
  position: sticky;
  bottom: 16px;
  left: 50%;
  transform: translateX(-50%);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(13, 17, 29, 0.9);
  border: 1px solid var(--text-highlight);
  color: var(--text-highlight);
  font-size: 1.4rem;
  line-height: 1;
  cursor: pointer;
  box-shadow: 0 0 12px rgba(0, 255, 255, 0.25);
  transition: all 0.2s;
  z-index: 10;
}

.scroll-to-bottom:hover {
  background: var(--text-highlight);
  color: var(--bg-color-dark);
}

.log-entry {
  margin-bottom: 14px;
  animation: fadeIn 0.15s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}

.log-label {
  color: var(--text-highlight);
  margin-bottom: 4px;
  font-weight: 500;
}

.log-message {
  margin: 0;
  padding: 10px 12px;
  background: rgba(0, 0, 0, 0.25);
  border-left: 2px solid var(--border-color);
  white-space: pre-wrap;
  word-break: break-word;
  font-family: inherit;
}

.intro-text {
  color: var(--text-primary);
  opacity: 0.9;
  font-style: italic;
}

.oracle-text {
  border-left-color: var(--text-highlight);
  color: #ffffff;
  text-shadow: 0 0 8px rgba(0, 255, 255, 0.3);
}

.question-text {
  border-left-color: var(--text-warn);
  color: var(--text-warn);
}

.persuasion-text {
  border-left-color: #9b59b6;
  color: #d8b4e2;
}

.log-decision {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.log-actor {
  color: var(--text-highlight);
}

.log-decision-text {
  font-weight: 700;
}

.log-decision-text.success {
  color: #00ff9d;
}

.log-decision-text.danger {
  color: #ff4d4d;
}

.player-tag {
  font-size: 0.75em;
  padding: 1px 6px;
  border: 1px solid var(--text-warn);
  color: var(--text-warn);
  border-radius: 3px;
}

.log-reason {
  margin-top: 4px;
  padding-left: 12px;
  color: var(--text-primary);
  opacity: 0.85;
  font-size: 0.9em;
}

.log-dict {
  background: rgba(0, 0, 0, 0.25);
  border-left: 2px solid var(--border-color);
  padding: 10px 12px;
}

.log-dict-item {
  display: flex;
  gap: 8px;
  margin-bottom: 4px;
}

.log-dict-key {
  color: var(--text-highlight);
  min-width: 120px;
}

.log-dict-value {
  color: var(--text-primary);
}

.log-divider {
  border-top: 1px dashed var(--border-color);
  margin: 20px 0;
  opacity: 0.5;
}

.highlight {
  color: var(--text-highlight);
}

.warn {
  color: var(--text-warn);
}

.danger {
  color: #ff4d4d;
}
</style>
