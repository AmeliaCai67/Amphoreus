<template>
  <div class="choice-panel" v-if="choices">
    <!-- 角色选择 -->
    <template v-if="decisionType === 'choose_character'">
      <div class="choice-title">>>> 请选择要扮演的角色</div>
      <div class="character-grid">
        <button
          v-for="(ch, index) in choices.available_characters"
          :key="ch.id"
          class="choice-btn character-btn"
          :class="{ selected: selectedDecision === ch.id }"
          @click="emit('choose-character', ch.id)"
          :disabled="loading"
        >
          <div class="character-name">{{ index + 1 }}. {{ ch.name }}</div>
          <div class="character-id">{{ ch.id }}</div>
        </button>
      </div>
    </template>

    <!-- 逐火决策 -->
    <template v-else-if="['fire_decision', 'fire_persuasion_decision'].includes(decisionType)">
      <div class="choice-title">
        {{ decisionType === 'fire_persuasion_decision' ? '>>> 再次决定：是否逐火？' : '>>> 是否响应神谕，踏上逐火之路？' }}
      </div>
      <div class="choice-actions">
        <button
          class="choice-btn yes"
          :class="{ selected: selectedDecision === '1' }"
          @click="selectDecision('1')"
          :disabled="loading"
        >
          逐火 [Y]
        </button>
        <button
          class="choice-btn no"
          :class="{ selected: selectedDecision === '0' }"
          @click="selectDecision('0')"
          :disabled="loading"
        >
          不逐火 [N]
        </button>
      </div>
      <div class="reason-box">
        <label>理由（可选，留空由 AI 生成）</label>
        <textarea
          v-model="localReason"
          rows="2"
          placeholder="写下你的理由..."
          :disabled="loading"
        />
      </div>
      <button
        class="confirm-btn"
        :disabled="loading || !selectedDecision"
        @click="confirmFire"
      >
        {{ loading ? '发送中...' : '发送决策 [Enter]' }}
      </button>
    </template>

    <!-- 交火种决策 -->
    <template v-else-if="['handover_decision', 'handover_persuasion_decision'].includes(decisionType)">
      <div class="choice-title">
        {{ decisionType === 'handover_persuasion_decision' ? '>>> 盗火行者劝说后，是否改变主意？' : '>>> 是否将火种交予盗火行者？' }}
      </div>
      <div class="choice-actions">
        <button
          class="choice-btn yes"
          :class="{ selected: selectedDecision === '1' }"
          @click="selectDecision('1')"
          :disabled="loading"
        >
          交出火种 [Y]
        </button>
        <button
          class="choice-btn no"
          :class="{ selected: selectedDecision === '0' }"
          @click="selectDecision('0')"
          :disabled="loading"
        >
          拒绝交出 [N]
        </button>
      </div>
      <div class="reason-box">
        <label>理由（可选，留空由 AI 生成）</label>
        <textarea
          v-model="localReason"
          rows="2"
          placeholder="写下你的理由..."
          :disabled="loading"
        />
      </div>
      <button
        class="confirm-btn"
        :disabled="loading || !selectedDecision"
        @click="confirmHandover"
      >
        {{ loading ? '发送中...' : '发送决策 [Enter]' }}
      </button>
    </template>

    <!-- 继续下一轮 -->
    <template v-else-if="decisionType === 'continue'">
      <div class="choice-title">>>> 回合结束</div>
      <button
        class="choice-btn primary"
        @click="emit('continue-round')"
        :disabled="loading"
      >
        进入下一轮 [Enter]
      </button>
    </template>

    <!-- 游戏完成 -->
    <template v-else-if="stage === 'complete'">
      <div class="choice-title">>>> 永劫回归测试完成</div>
      <button
        class="choice-btn primary"
        @click="emit('reset-game')"
        :disabled="loading"
      >
        重新开始 [R]
      </button>
    </template>
  </div>
</template>

<script setup>
import { computed, ref, watch, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  choices: { type: Object, default: null },
  stage: { type: String, default: 'config' },
  loading: { type: Boolean, default: false },
  modelValue: { type: String, default: '' },
})

const emit = defineEmits([
  'choose-character',
  'fire-decision',
  'handover-decision',
  'continue-round',
  'reset-game',
  'update:modelValue',
])

const decisionType = computed(() => props.choices?.decision_type)
const selectedDecision = ref(null)

// 每次进入新的选择阶段时，清空已选决策
watch(
  () => props.choices?.decision_type,
  () => {
    selectedDecision.value = null
  }
)

const localReason = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

function selectDecision(decision) {
  selectedDecision.value = decision
}

function confirmFire() {
  if (!selectedDecision.value) return
  emit('fire-decision', selectedDecision.value)
}

function confirmHandover() {
  if (!selectedDecision.value) return
  emit('handover-decision', selectedDecision.value)
}

function handleKeydown(e) {
  if (props.loading) return

  // 焦点在输入框/文本域内时，只响应 Enter 确认，不响应 Y/N
  const tag = e.target?.tagName?.toLowerCase()
  const inInput = tag === 'input' || tag === 'textarea'

  const type = decisionType.value

  if (type === 'choose_character') {
    const chars = props.choices?.available_characters || []
    const num = parseInt(e.key, 10)
    if (!isNaN(num) && num >= 1 && num <= chars.length) {
      e.preventDefault()
      emit('choose-character', chars[num - 1].id)
    }
    return
  }

  if (['fire_decision', 'fire_persuasion_decision'].includes(type)) {
    if (e.key === 'Enter' && selectedDecision.value) {
      e.preventDefault()
      confirmFire()
      return
    }
    if (!inInput) {
      if (e.key.toLowerCase() === 'y') {
        e.preventDefault()
        selectDecision('1')
      }
      if (e.key.toLowerCase() === 'n') {
        e.preventDefault()
        selectDecision('0')
      }
    }
    return
  }

  if (['handover_decision', 'handover_persuasion_decision'].includes(type)) {
    if (e.key === 'Enter' && selectedDecision.value) {
      e.preventDefault()
      confirmHandover()
      return
    }
    if (!inInput) {
      if (e.key.toLowerCase() === 'y') {
        e.preventDefault()
        selectDecision('1')
      }
      if (e.key.toLowerCase() === 'n') {
        e.preventDefault()
        selectDecision('0')
      }
    }
    return
  }

  if (type === 'continue' && e.key === 'Enter') {
    e.preventDefault()
    emit('continue-round')
    return
  }

  if (props.stage === 'complete' && e.key.toLowerCase() === 'r') {
    e.preventDefault()
    emit('reset-game')
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.choice-panel {
  border-top: 1px solid var(--border-color);
  padding: 16px;
  background: rgba(0, 0, 0, 0.35);
}

.choice-title {
  color: var(--text-highlight);
  margin-bottom: 12px;
  font-weight: 500;
}

.choice-actions {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.character-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 10px;
}

.choice-btn {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  font-family: inherit;
  padding: 10px 16px;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
}

.choice-btn:hover:not(:disabled) {
  border-color: var(--text-highlight);
  box-shadow: 0 0 10px rgba(0, 255, 255, 0.15);
}

.choice-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.choice-btn.selected {
  background: rgba(0, 255, 255, 0.12);
  border-color: var(--text-highlight);
  color: #ffffff;
}

.choice-btn.yes {
  border-color: #00ff9d;
  color: #00ff9d;
}

.choice-btn.yes.selected {
  background: rgba(0, 255, 157, 0.2);
  border-color: #00ff9d;
  color: #ffffff;
}

.choice-btn.no {
  border-color: #ff4d4d;
  color: #ff4d4d;
}

.choice-btn.no.selected {
  background: rgba(255, 77, 77, 0.2);
  border-color: #ff4d4d;
  color: #ffffff;
}

.choice-btn.primary {
  border-color: var(--text-highlight);
  color: var(--text-highlight);
  width: 100%;
}

.choice-btn.primary:hover:not(:disabled) {
  background: rgba(0, 255, 255, 0.1);
}

.character-btn {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.character-name {
  color: var(--text-highlight);
  font-weight: 500;
}

.character-id {
  font-size: 0.8em;
  opacity: 0.7;
}

.reason-box {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 12px;
}

.reason-box label {
  font-size: 0.8em;
  color: var(--text-primary);
  opacity: 0.7;
}

.reason-box textarea {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  font-family: inherit;
  padding: 8px;
  resize: vertical;
  outline: none;
}

.reason-box textarea:focus {
  border-color: var(--text-highlight);
}

.confirm-btn {
  width: 100%;
  padding: 12px;
  background: transparent;
  border: 1px solid var(--text-highlight);
  color: var(--text-highlight);
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s;
}

.confirm-btn:hover:not(:disabled) {
  background: var(--text-highlight);
  color: var(--bg-color-dark);
}

.confirm-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  border-color: var(--border-color);
  color: var(--text-primary);
}
</style>
