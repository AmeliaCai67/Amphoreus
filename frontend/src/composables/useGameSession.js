import { ref, computed, nextTick } from 'vue'
import { gameApi, setApiPassword, getApiPassword } from '../api/gameApi.js'

const STORAGE_KEY = 'amphoreus_session_id'
const PASSWORD_STORAGE_KEY = 'amphoreus_password'
const STREAM_INTERVAL = 180 // 每条事件 reveal 间隔（ms）

const defaultState = {
  session_id: null,
  stage: 'config',
  round: 0,
  max_rounds: 1,
  player_char_id: null,
  events: [],
  choices: null,
  fire_chasers_dict: {},
  robbed_characters: [],
  password: '',
}

const state = ref({ ...defaultState })
const displayedEvents = ref([])
const charNames = ref({})
const isStreaming = ref(false)
const isLoading = ref(false)
const error = ref(null)
const reason = ref('')

let streamTimer = null
let streamedCount = 0

/**
 * 从 JSON 字符串中提取 reason 字段，兼容 markdown 代码块。
 */
function extractReason(message) {
  if (!message || typeof message !== 'string') return ''
  let text = message.trim()

  if (text.startsWith('```')) {
    const lines = text.split('\n')
    if (lines.length > 2) {
      text = lines.slice(1, -1).join('\n').trim()
    } else {
      text = text.replace(/```/g, '').trim()
    }
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

async function scrollToBottom() {
  await nextTick()
  const logs = document.querySelector('.terminal-logs')
  if (logs) {
    logs.scrollTop = logs.scrollHeight
  }
}

function saveSession() {
  if (state.value.session_id) {
    localStorage.setItem(STORAGE_KEY, state.value.session_id)
  }
  if (state.value.password) {
    localStorage.setItem(PASSWORD_STORAGE_KEY, state.value.password)
  }
}

function clearSavedSession() {
  localStorage.removeItem(STORAGE_KEY)
  localStorage.removeItem(PASSWORD_STORAGE_KEY)
}

function flushStreamQueue() {
  if (streamTimer) {
    clearInterval(streamTimer)
    streamTimer = null
  }
  if (streamedCount < state.value.events.length) {
    displayedEvents.value = [...state.value.events]
    streamedCount = state.value.events.length
  }
  isStreaming.value = false
}

function streamNewEvents() {
  const pending = state.value.events.slice(streamedCount)
  if (!pending.length) {
    isStreaming.value = false
    return
  }

  isStreaming.value = true
  let index = 0

  streamTimer = setInterval(() => {
    if (index >= pending.length) {
      clearInterval(streamTimer)
      streamTimer = null
      streamedCount = state.value.events.length
      isStreaming.value = false
      return
    }
    displayedEvents.value.push(pending[index])
    index++
    scrollToBottom()
  }, STREAM_INTERVAL)
}

function setState(newState, { immediate = false } = {}) {
  Object.assign(state.value, newState)

  // 持久化角色名映射（从可选角色列表中提取）
  if (newState.choices?.available_characters) {
    for (const ch of newState.choices.available_characters) {
      charNames.value[ch.id] = ch.name
    }
  }

  saveSession()

  if (immediate) {
    // 恢复旧会话时一次性展示所有事件，不再逐条打字
    flushStreamQueue()
    scrollToBottom()
  } else {
    streamNewEvents()
  }
}

async function tryRestoreSession() {
  const session_id = localStorage.getItem(STORAGE_KEY)
  const savedPassword = localStorage.getItem(PASSWORD_STORAGE_KEY)
  if (!session_id || !savedPassword) return false

  setApiPassword(savedPassword)
  state.value.password = savedPassword

  isLoading.value = true
  try {
    const newState = await gameApi.getState(session_id)
    setState({ ...newState, password: savedPassword }, { immediate: true })
    return true
  } catch (err) {
    clearSavedSession()
    resetGame()
    return false
  } finally {
    isLoading.value = false
  }
}

async function startGame(max_rounds, password) {
  isLoading.value = true
  error.value = null
  try {
    setApiPassword(password)
    state.value.password = password
    const created = await gameApi.createSession(max_rounds)
    const started = await gameApi.start(created.session_id)
    setState({ ...started, max_rounds, password })
  } catch (err) {
    error.value = err.message
  } finally {
    isLoading.value = false
  }
}

async function chooseCharacter(char_id) {
  isLoading.value = true
  error.value = null
  try {
    const newState = await gameApi.chooseCharacter(state.value.session_id, char_id)
    setState(newState)
  } catch (err) {
    error.value = err.message
  } finally {
    isLoading.value = false
  }
}

async function submitFireDecision(decision) {
  isLoading.value = true
  error.value = null
  try {
    const newState = await gameApi.submitFireDecision(
      state.value.session_id,
      decision,
      reason.value.trim() || null
    )
    reason.value = ''
    setState(newState)
  } catch (err) {
    error.value = err.message
  } finally {
    isLoading.value = false
  }
}

async function submitHandoverDecision(decision) {
  isLoading.value = true
  error.value = null
  try {
    const newState = await gameApi.submitHandoverDecision(
      state.value.session_id,
      decision,
      reason.value.trim() || null
    )
    reason.value = ''
    setState(newState)
  } catch (err) {
    error.value = err.message
  } finally {
    isLoading.value = false
  }
}

async function submitHandoverRedecision(decision) {
  isLoading.value = true
  error.value = null
  try {
    const newState = await gameApi.submitHandoverRedecision(
      state.value.session_id,
      decision,
      reason.value.trim() || null
    )
    reason.value = ''
    setState(newState)
  } catch (err) {
    error.value = err.message
  } finally {
    isLoading.value = false
  }
}

async function continueRound() {
  isLoading.value = true
  error.value = null
  try {
    const newState = await gameApi.continueRound(state.value.session_id)
    setState(newState)
  } catch (err) {
    error.value = err.message
  } finally {
    isLoading.value = false
  }
}

function resetGame() {
  flushStreamQueue()
  clearSavedSession()
  setApiPassword('')
  state.value = { ...defaultState }
  displayedEvents.value = []
  charNames.value = {}
  streamedCount = 0
  reason.value = ''
  error.value = null
}

const isWaitingForInput = computed(() => {
  if (isLoading.value || isStreaming.value) return false
  const interactiveStages = [
    'choose_character',
    'fire_decision',
    'fire_persuasion',
    'handover_decision',
    'handover_persuasion',
    'round_end',
    'complete',
  ]
  return interactiveStages.includes(state.value.stage)
})

const decisionType = computed(() => state.value.choices?.decision_type || null)

export function useGameSession() {
  return {
    state,
    displayedEvents,
    charNames,
    isStreaming,
    isLoading,
    error,
    reason,
    isWaitingForInput,
    decisionType,
    extractReason,
    tryRestoreSession,
    startGame,
    chooseCharacter,
    submitFireDecision,
    submitHandoverDecision,
    submitHandoverRedecision,
    continueRound,
    resetGame,
  }
}
