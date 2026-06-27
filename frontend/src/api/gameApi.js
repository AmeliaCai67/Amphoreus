/**
 * gameApi.js - 交互式逐火之旅后端 API 封装
 *
 * 后端提供有状态 REST API，前端通过 session_id 推进游戏流程。
 * cloud 分支所有接口均需携带访问口令 password。
 */

const API_BASE = '/api'

let apiPassword = ''

export function setApiPassword(password) {
  apiPassword = password
}

export function getApiPassword() {
  return apiPassword
}

function buildUrl(url) {
  if (!apiPassword) return `${API_BASE}${url}`
  const separator = url.includes('?') ? '&' : '?'
  return `${API_BASE}${url}${separator}password=${encodeURIComponent(apiPassword)}`
}

async function request(url, options = {}) {
  const res = await fetch(buildUrl(url), {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })

  if (!res.ok) {
    let detail = ''
    try {
      detail = await res.text()
    } catch {
      detail = ''
    }
    throw new Error(`[HTTP ${res.status}] ${detail || '请求失败'}`)
  }

  return res.json()
}

export const gameApi = {
  /** 创建游戏会话 */
  createSession(max_rounds = 1) {
    return request('/game/create', {
      method: 'POST',
      body: JSON.stringify({ max_rounds }),
    })
  },

  /** 开始游戏：返回开场文案、神谕、可选角色 */
  start(session_id) {
    return request(`/game/${session_id}/start`, { method: 'POST' })
  },

  /** 查询当前状态 */
  getState(session_id) {
    return request(`/game/${session_id}/state`)
  },

  /** 玩家选择扮演角色 */
  chooseCharacter(session_id, char_id) {
    return request(`/game/${session_id}/choose`, {
      method: 'POST',
      body: JSON.stringify({ char_id }),
    })
  },

  /** 提交逐火决策（含劝说后的二次决策） */
  submitFireDecision(session_id, decision, reason = null) {
    return request(`/game/${session_id}/fire_decision`, {
      method: 'POST',
      body: JSON.stringify({ decision, reason }),
    })
  },

  /** 提交交火种决策 */
  submitHandoverDecision(session_id, decision, reason = null) {
    return request(`/game/${session_id}/handover_decision`, {
      method: 'POST',
      body: JSON.stringify({ decision, reason }),
    })
  },

  /** 盗火行者劝说后，再次提交交火种决策 */
  submitHandoverRedecision(session_id, decision, reason = null) {
    return request(`/game/${session_id}/handover_redecision`, {
      method: 'POST',
      body: JSON.stringify({ decision, reason }),
    })
  },

  /** 回合结束继续下一轮 */
  continueRound(session_id) {
    return request(`/game/${session_id}/continue`, { method: 'POST' })
  },
}
