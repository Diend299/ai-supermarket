<template>
  <div class="workbench-page">
    <div class="main-content">
      <!-- 左侧主面板 -->
      <div class="left-panel">
        <!-- Tab 切换 -->
        <div class="tab-bar">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            :class="['tab-btn', { active: activeTab === tab.id }]"
            @click="activeTab = tab.id"
          >
            <span class="tab-icon">{{ tab.icon }}</span>
            <span class="tab-label">{{ tab.label }}</span>
          </button>
        </div>

        <!-- 文案创作 Tab -->
        <div v-if="activeTab === 'text'" class="tab-content">
          <div class="input-card">
            <div class="card-header">
              <div class="header-title">
                <svg viewBox="0 0 24 24" class="header-icon" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                </svg>
                <h3>创作需求</h3>
              </div>
              <span class="badge">AI驱动</span>
            </div>

            <div class="form-group">
              <label>文案主题 / 内容描述</label>
              <textarea
                v-model="textForm.prompt"
                placeholder="请输入您想要生成的文案主题或内容描述，例如：写一篇618大促活动推广文案，目标用户为25-35岁女性..."
                rows="7"
                :disabled="textSubmitting"
              ></textarea>
              <span class="char-count">{{ textForm.prompt.length }} / 2000</span>
            </div>

            <div class="form-group">
              <label>补充要求（可选）</label>
              <textarea
                v-model="textForm.systemPrompt"
                placeholder="可指定文案风格、语气、字数要求等，例如：风格活泼、字数500字左右、加入emoji表情"
                rows="4"
                :disabled="textSubmitting"
              ></textarea>
            </div>

            <button
              class="submit-btn"
              :disabled="textSubmitting || !textForm.prompt.trim()"
              @click="handleTextSubmit"
            >
              <span class="btn-icon">🚀</span>
              <span v-if="!textSubmitting">开始创作</span>
              <span v-else>生成中...</span>
            </button>
          </div>

          <div class="result-card" v-if="textShowResult">
            <div class="card-header">
              <div class="header-title">
                <svg viewBox="0 0 24 24" class="header-icon" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M9 11l3 3L22 4"></path>
                  <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
                </svg>
                <h3>创作结果</h3>
              </div>
              <span :class="['status-badge', textStatusClass]">
                <span class="dot" :class="{ animate: textTaskStatus === 1 }"></span>
                {{ textStatusText }}
              </span>
            </div>

            <div class="progress-bar" v-if="textTaskStatus === 0 || textTaskStatus === 1">
              <div class="progress-fill" :style="{ width: textProgress + '%' }"></div>
            </div>

            <div class="result-content" v-if="textTaskStatus === 2 && textResultText">
              <div class="result-text">{{ textResultText }}</div>
              <div class="result-actions">
                <button class="action-btn secondary" @click="handleCopyText">
                  <svg viewBox="0 0 24 24" class="btn-icon-svg" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                  </svg>
                  复制文案
                </button>
                <button class="action-btn primary" @click="sendToTts">
                  🔊 转为语音
                </button>
              </div>
            </div>

            <div class="error-msg" v-if="textTaskStatus === 3 && textErrorMsg">
              <svg viewBox="0 0 24 24" class="error-icon" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="8" x2="12" y2="12"></line>
                <line x1="12" y1="16" x2="12.01" y2="16"></line>
              </svg>
              <span>{{ textErrorMsg }}</span>
            </div>
          </div>
        </div>

        <!-- 语音合成 Tab -->
        <div v-if="activeTab === 'tts'" class="tab-content">
          <div class="input-card">
            <div class="card-header">
              <div class="header-title">
                <svg viewBox="0 0 24 24" class="header-icon" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M11 5L6 9H2v6h4l5 4V5z"></path>
                  <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path>
                </svg>
                <h3>语音合成</h3>
              </div>
              <span class="badge">GPT-SoVITS</span>
            </div>

            <div class="form-group">
              <label>合成文本 <span class="required">*</span></label>
              <textarea
                v-model="ttsForm.text"
                placeholder="请输入要转换为语音的文本内容..."
                rows="6"
                :disabled="ttsSubmitting"
              ></textarea>
              <span class="char-count">{{ ttsForm.text.length }} 字符</span>
            </div>

            <div class="form-row">
              <div class="form-group flex-1">
                <label>音色</label>
                <select v-model="ttsForm.voice" :disabled="ttsSubmitting" @change="onVoiceChange">
                  <option
                    v-for="v in voiceOptions"
                    :key="v.id"
                    :value="v.id"
                  >{{ v.label }}</option>
                </select>
              </div>
              <div class="form-group flex-1">
                <label>语言</label>
                <select v-model="ttsForm.lang" :disabled="ttsSubmitting">
                  <option value="ja">日语 (ja)</option>
                  <option value="zh">中文 (zh)</option>
                  <option value="en">英文 (en)</option>
                </select>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group flex-1">
                <label>语速: {{ ttsForm.speed.toFixed(1) }}</label>
                <div class="slider-group">
                  <span>0.5</span>
                  <input
                    type="range"
                    v-model.number="ttsForm.speed"
                    min="0.5"
                    max="2.0"
                    step="0.1"
                    :disabled="ttsSubmitting"
                  />
                  <span>2.0</span>
                </div>
              </div>
            </div>

            <button
              class="submit-btn"
              :disabled="ttsSubmitting || !ttsForm.text.trim()"
              @click="handleTtsSubmit"
            >
              <span class="btn-icon">🔊</span>
              <span v-if="!ttsSubmitting">开始合成</span>
              <span v-else>合成中...</span>
            </button>
          </div>

          <div class="result-card" v-if="ttsShowResult">
            <div class="card-header">
              <div class="header-title">
                <svg viewBox="0 0 24 24" class="header-icon" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M9 18V5l12-2v13"></path>
                  <circle cx="6" cy="18" r="3"></circle>
                  <circle cx="18" cy="16" r="3"></circle>
                </svg>
                <h3>合成结果</h3>
              </div>
              <span :class="['status-badge', ttsStatusClass]">
                <span class="dot" :class="{ animate: ttsTaskStatus === 1 }"></span>
                {{ ttsStatusText }}
              </span>
            </div>

            <div class="progress-bar" v-if="ttsTaskStatus === 0 || ttsTaskStatus === 1">
              <div class="progress-fill" :style="{ width: ttsProgress + '%' }"></div>
            </div>

            <div class="result-content" v-if="ttsTaskStatus === 2 && ttsAudioUrl">
              <div class="audio-player">
                <audio
                  ref="audioPlayer"
                  :src="audioFullUrl"
                  controls
                  class="audio-control"
                  @ended="audioPlaying = false"
                  @play="audioPlaying = true"
                  @pause="audioPlaying = false"
                ></audio>
              </div>
              <div class="result-actions">
                <button class="action-btn secondary" @click="handleDownloadAudio">
                  <svg viewBox="0 0 24 24" class="btn-icon-svg" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                    <polyline points="7,10 12,15 17,10"></polyline>
                    <line x1="12" y1="15" x2="12" y2="3"></line>
                  </svg>
                  下载音频
                </button>
              </div>
            </div>

            <div class="error-msg" v-if="ttsTaskStatus === 3 && ttsErrorMsg">
              <svg viewBox="0 0 24 24" class="error-icon" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="8" x2="12" y2="12"></line>
                <line x1="12" y1="16" x2="12.01" y2="16"></line>
              </svg>
              <span>{{ ttsErrorMsg }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧历史面板 -->
      <div class="right-panel">
        <div class="history-card">
          <div class="card-header">
            <div class="header-title">
              <svg viewBox="0 0 24 24" class="header-icon" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <polyline points="12,6 12,12 16,14"></polyline>
              </svg>
              <h3>任务历史</h3>
            </div>
            <span class="count-badge">{{ historyList.length }}</span>
          </div>

          <div class="history-filter">
            <button
              v-for="filter in historyFilters"
              :key="filter.id"
              :class="['filter-btn', { active: activeFilter === filter.id }]"
              @click="activeFilter = filter.id"
            >
              {{ filter.label }}
            </button>
          </div>

          <div class="history-list">
            <div
              v-for="item in filteredHistory"
              :key="item.taskId"
              class="history-item"
              :class="{ active: currentTaskId === item.taskId }"
              @click="viewHistory(item)"
            >
              <div class="history-icon" :class="getStatusClass(item.status)">
                <svg v-if="item.status === 2" viewBox="0 0 24 24" class="item-icon-svg" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="20,6 9,17 4,12"></polyline>
                </svg>
                <svg v-else-if="item.status === 3" viewBox="0 0 24 24" class="item-icon-svg" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
                <svg v-else viewBox="0 0 24 24" class="item-icon-svg" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"></circle>
                  <polyline points="12,6 12,12 16,14"></polyline>
                </svg>
              </div>
              <div class="history-info">
                <span class="history-type">{{ item.typeLabel }}</span>
                <span class="history-time">{{ item.time }}</span>
              </div>
              <span :class="['history-status', getStatusClass(item.status)]">
                {{ getStatusText(item.status) }}
              </span>
            </div>
            <div v-if="filteredHistory.length === 0" class="empty-hint">
              <svg viewBox="0 0 24 24" class="empty-icon" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M9.172 16.172a4 4 0 0 1 5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0z"></path>
              </svg>
              <p>暂无任务记录</p>
              <span>开始您的第一次创作吧</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { createTask, getTaskDetail, getTaskResult, getUserTasks } from '@/api/task'
import type { TaskListItem } from '@/api/task'

// ========== Tab 切换 ==========
const tabs = [
  { id: 'text', icon: '📝', label: '文案创作' },
  { id: 'tts', icon: '🔊', label: '语音合成' }
]
const activeTab = ref('text')

// ========== 工具函数 ==========
const getToken = () => localStorage.getItem('token') || ''
const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080'

// ========== 文案创作（复用 Copywriting 逻辑） ==========
const textForm = reactive({
  prompt: '',
  systemPrompt: ''
})
const textSubmitting = ref(false)
const textShowResult = ref(false)
const textTaskStatus = ref(0)
const textProgress = ref(0)
const textErrorMsg = ref('')
const textResultText = ref('')

const textStatusClass = computed(() => {
  const map: Record<number, string> = { 0: 'pending', 1: 'processing', 2: 'success', 3: 'failed' }
  return map[textTaskStatus.value] || ''
})
const textStatusText = computed(() => {
  const map: Record<number, string> = { 0: '排队中', 1: '生成中', 2: '已完成', 3: '失败' }
  return map[textTaskStatus.value] || ''
})

const handleTextSubmit = async () => {
  if (!textForm.prompt.trim()) return
  textSubmitting.value = true
  textShowResult.value = true
  textTaskStatus.value = 0
  textProgress.value = 0
  textErrorMsg.value = ''
  textResultText.value = ''
  try {
    const res = await createTask({
      taskType: 'text2text',
      params: { prompt: textForm.prompt.trim(), system_prompt: textForm.systemPrompt.trim() || undefined }
    })
    if (res.code === 0) {
      currentTaskId.value = res.data.taskId
      startSse(res.data.taskId, 'text')
      loadHistory()
    } else {
      throw new Error(res.msg || '创建任务失败')
    }
  } catch (e: any) {
    textTaskStatus.value = 3
    textErrorMsg.value = e.message || '网络错误'
    textSubmitting.value = false
  }
}

const handleCopyText = async () => {
  try {
    await navigator.clipboard.writeText(textResultText.value)
    alert('✅ 文案已复制到剪贴板')
  } catch {
    const textarea = document.createElement('textarea')
    textarea.value = textResultText.value
    document.body.appendChild(textarea)
    textarea.select()
    document.execCommand('copy')
    document.body.removeChild(textarea)
    alert('✅ 文案已复制到剪贴板')
  }
}

// 将文案结果发送到语音合成 Tab
const sendToTts = () => {
  ttsForm.text = textResultText.value
  activeTab.value = 'tts'
}

// ========== 语音合成 ==========
const voiceOptions = [
  { id: 'asuka', label: 'Asuka (日语)', lang: 'ja' },
  { id: 'malashi', label: '马老师 (中文)', lang: 'zh' }
]

const ttsForm = reactive({
  text: '',
  lang: 'ja',
  speed: 1.0,
  voice: 'asuka'
})
const ttsSubmitting = ref(false)
const ttsShowResult = ref(false)
const ttsTaskStatus = ref(0)
const ttsProgress = ref(0)
const ttsErrorMsg = ref('')
const ttsAudioUrl = ref('')
const audioPlaying = ref(false)
const audioPlayer = ref<HTMLAudioElement | null>(null)

const audioFullUrl = computed(() => {
  if (!ttsAudioUrl.value) return ''
  return `${baseUrl}${ttsAudioUrl.value}`
})

// 音色切换时自动匹配对应语言的默认值
const onVoiceChange = () => {
  const selected = voiceOptions.find(v => v.id === ttsForm.voice)
  if (selected) {
    ttsForm.lang = selected.lang
  }
}

const ttsStatusClass = computed(() => {
  const map: Record<number, string> = { 0: 'pending', 1: 'processing', 2: 'success', 3: 'failed' }
  return map[ttsTaskStatus.value] || ''
})
const ttsStatusText = computed(() => {
  const map: Record<number, string> = { 0: '排队中', 1: '合成中', 2: '已完成', 3: '失败' }
  return map[ttsTaskStatus.value] || ''
})

const handleTtsSubmit = async () => {
  if (!ttsForm.text.trim()) return
  ttsSubmitting.value = true
  ttsShowResult.value = true
  ttsTaskStatus.value = 0
  ttsProgress.value = 0
  ttsErrorMsg.value = ''
  ttsAudioUrl.value = ''
  try {
    const res = await createTask({
      taskType: 'tts_generate',
      params: {
        text: ttsForm.text.trim(),
        text_lang: ttsForm.lang,
        speed: ttsForm.speed,
        voice: ttsForm.voice
      }
    })
    if (res.code === 0) {
      currentTaskId.value = res.data.taskId
      startSse(res.data.taskId, 'tts')
      loadHistory()
    } else {
      throw new Error(res.msg || '创建任务失败')
    }
  } catch (e: any) {
    ttsTaskStatus.value = 3
    ttsErrorMsg.value = e.message || '网络错误'
    ttsSubmitting.value = false
  }
}

const handleDownloadAudio = () => {
  const a = document.createElement('a')
  a.href = audioFullUrl.value
  a.download = `tts_${currentTaskId.value}.wav`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
}

// ========== 通用 SSE / 轮询 ==========
let eventSource: EventSource | null = null
let pollingTimer: ReturnType<typeof setInterval> | null = null
const currentTaskId = ref<number | null>(null)
const currentTaskType = ref<'text' | 'tts'>('text')

const startSse = (taskId: number, type: 'text' | 'tts') => {
  closeSse()
  currentTaskType.value = type
  const url = `${baseUrl}/api/task/${taskId}/subscribe?token=${encodeURIComponent(getToken())}`
  eventSource = new EventSource(url)

  eventSource.addEventListener('heartbeat', () => {})

  eventSource.addEventListener('task-completed', (e: MessageEvent) => {
    console.log('[SSE] completed:', e.data)
    if (type === 'text') {
      textSubmitting.value = false
      textTaskStatus.value = 2
      if (taskId) fetchTextResult(taskId)
    } else {
      ttsSubmitting.value = false
      ttsTaskStatus.value = 2
      if (taskId) fetchTtsResult(taskId)
    }
    closeSse()
    loadHistory()
  })

  eventSource.addEventListener('task-failed', (e: MessageEvent) => {
    console.log('[SSE] failed:', e.data)
    try {
      const data = JSON.parse(e.data)
      if (type === 'text') {
        textSubmitting.value = false
        textTaskStatus.value = 3
        textErrorMsg.value = data.errorMsg || '生成失败'
      } else {
        ttsSubmitting.value = false
        ttsTaskStatus.value = 3
        ttsErrorMsg.value = data.errorMsg || '合成失败'
      }
    } catch {
      if (type === 'text') {
        textErrorMsg.value = '生成失败'
      } else {
        ttsErrorMsg.value = '合成失败'
      }
    }
    closeSse()
    loadHistory()
  })

  eventSource.onerror = () => {
    console.warn('[SSE] error, switch to polling')
    closeSse()
    startPolling(taskId, type)
  }
}

const closeSse = () => {
  if (eventSource) {
    eventSource.close()
    eventSource = null
  }
  if (pollingTimer) {
    clearInterval(pollingTimer)
    pollingTimer = null
  }
}

const startPolling = (taskId: number, type: 'text' | 'tts') => {
  pollingTimer = setInterval(async () => {
    try {
      const res = await getTaskDetail(taskId)
      if (res.code === 0) {
        const data = res.data
        if (type === 'text') {
          textTaskStatus.value = data.taskStatus
          textProgress.value = data.progress
          if (data.taskStatus === 2) {
            clearInterval(pollingTimer!)
            pollingTimer = null
            textSubmitting.value = false
            await fetchTextResult(taskId)
            loadHistory()
          } else if (data.taskStatus === 3) {
            clearInterval(pollingTimer!)
            pollingTimer = null
            textSubmitting.value = false
            textErrorMsg.value = data.errorMsg || '生成失败'
            loadHistory()
          }
        } else {
          ttsTaskStatus.value = data.taskStatus
          ttsProgress.value = data.progress
          if (data.taskStatus === 2) {
            clearInterval(pollingTimer!)
            pollingTimer = null
            ttsSubmitting.value = false
            await fetchTtsResult(taskId)
            loadHistory()
          } else if (data.taskStatus === 3) {
            clearInterval(pollingTimer!)
            pollingTimer = null
            ttsSubmitting.value = false
            ttsErrorMsg.value = data.errorMsg || '合成失败'
            loadHistory()
          }
        }
      }
    } catch (e) {
      console.error('Polling error:', e)
    }
  }, 2000)
}

const fetchTextResult = async (taskId: number) => {
  try {
    const res = await getTaskResult(taskId)
    if (res.code === 0) {
      const resources = res.data.resources
      const first = resources && resources.length > 0 ? resources[0] : null
      if (first) {
        textResultText.value = first.contentText || first.resourceUrl
      }
    }
  } catch (e) {
    console.error('Fetch text result error:', e)
  }
}

const fetchTtsResult = async (taskId: number) => {
  try {
    const res = await getTaskResult(taskId)
    if (res.code === 0) {
      const resources = res.data.resources
      const audioResource = resources && resources.find((r: any) => r.resourceType === 'audio')
      if (audioResource) {
        ttsAudioUrl.value = audioResource.resourceUrl
      }
      // 延迟加载音频后自动播放
      setTimeout(() => {
        if (audioPlayer.value) {
          audioPlayer.value.play().catch(() => {})
        }
      }, 300)
    }
  } catch (e) {
    console.error('Fetch audio result error:', e)
  }
}

// ========== 历史记录 ==========
interface HistoryItem {
  taskId: number
  taskType: string
  typeLabel: string
  time: string
  status: number
}

const historyList = ref<HistoryItem[]>([])
const activeFilter = ref('all')

const historyFilters = [
  { id: 'all', label: '全部' },
  { id: 'text2text', label: '文案' },
  { id: 'tts_generate', label: '语音' }
]

const filteredHistory = computed(() => {
  if (activeFilter.value === 'all') return historyList.value
  return historyList.value.filter(item => item.taskType === activeFilter.value)
})

const loadHistory = async () => {
  try {
    const res = await getUserTasks()
    if (res.code === 0) {
      const typeLabels: Record<string, string> = {
        text2text: '📝 文案创作',
        tts_generate: '🔊 语音合成'
      }
      historyList.value = res.data
        .filter((t: TaskListItem) => t.taskType === 'text2text' || t.taskType === 'tts_generate')
        .map((t: TaskListItem) => ({
          taskId: t.taskId,
          taskType: t.taskType,
          typeLabel: typeLabels[t.taskType] || t.taskType,
          time: new Date(t.createdAt).toLocaleString(),
          status: t.taskStatus
        }))
        .sort((a: HistoryItem, b: HistoryItem) => b.taskId - a.taskId)
    }
  } catch (e) {
    console.error('加载历史记录失败:', e)
  }
}

const viewHistory = async (item: HistoryItem) => {
  if (item.taskId === currentTaskId.value) return

  if (item.taskType === 'text2text') {
    activeTab.value = 'text'
    textShowResult.value = true
    textTaskStatus.value = 0
    textProgress.value = 0
    textErrorMsg.value = ''
    textResultText.value = ''
  } else {
    activeTab.value = 'tts'
    ttsShowResult.value = true
    ttsTaskStatus.value = 0
    ttsProgress.value = 0
    ttsErrorMsg.value = ''
    ttsAudioUrl.value = ''
  }

  currentTaskId.value = item.taskId
  currentTaskType.value = item.taskType === 'text2text' ? 'text' : 'tts'

  try {
    const res = await getTaskDetail(item.taskId)
    if (res.code === 0) {
      const data = res.data
      if (item.taskType === 'text2text') {
        textTaskStatus.value = data.taskStatus
        textProgress.value = data.progress
        if (data.taskStatus === 2) {
          await fetchTextResult(item.taskId)
        } else if (data.taskStatus === 3) {
          textErrorMsg.value = data.errorMsg || '生成失败'
        } else {
          startPolling(item.taskId, 'text')
        }
      } else {
        ttsTaskStatus.value = data.taskStatus
        ttsProgress.value = data.progress
        if (data.taskStatus === 2) {
          await fetchTtsResult(item.taskId)
        } else if (data.taskStatus === 3) {
          ttsErrorMsg.value = data.errorMsg || '合成失败'
        } else {
          startPolling(item.taskId, 'tts')
        }
      }
    }
  } catch (e: any) {
    if (item.taskType === 'text2text') {
      textTaskStatus.value = 3
      textErrorMsg.value = e.message || '查询失败'
    } else {
      ttsTaskStatus.value = 3
      ttsErrorMsg.value = e.message || '查询失败'
    }
  }
}

const getStatusClass = (status: number) => {
  const map: Record<number, string> = { 0: 'pending', 1: 'processing', 2: 'success', 3: 'failed' }
  return map[status] || ''
}
const getStatusText = (status: number) => {
  const map: Record<number, string> = { 0: '排队中', 1: '生成中', 2: '已完成', 3: '失败' }
  return map[status] || '未知'
}

onMounted(() => {
  loadHistory()
})

onUnmounted(() => {
  closeSse()
})
</script>

<style scoped>
.workbench-page {
  width: 100%;
  min-height: calc(100vh - 180px);
  display: flex;
  justify-content: flex-start;
  background: transparent;
}

.main-content {
  display: flex;
  gap: 24px;
  width: 100%;
  min-width: 0;
}

.left-panel {
  flex: 3;
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-width: 450px;
  width: 100%;
}

.right-panel {
  flex: 1;
  min-width: 300px;
  max-width: 420px;
  display: flex;
  flex-direction: column;
}

/* Tab Bar */
.tab-bar {
  display: flex;
  gap: 0;
  background: white;
  border-radius: 16px 16px 0 0;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.tab-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 18px 24px;
  background: transparent;
  border: none;
  border-bottom: 3px solid transparent;
  font-size: 16px;
  font-weight: 600;
  color: #9ca3af;
  cursor: pointer;
  transition: all 0.3s;
}

.tab-btn:hover {
  color: #6b7280;
  background: #f9fafb;
}

.tab-btn.active {
  color: #8b5cf6;
  border-bottom-color: #8b5cf6;
  background: #fafbff;
}

.tab-icon {
  font-size: 20px;
}

.tab-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Cards */
.input-card,
.result-card,
.history-card {
  background: white;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
  display: flex;
  flex-direction: column;
}

.input-card,
.result-card {
  flex-shrink: 0;
}

.history-card {
  flex: 1;
  min-height: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-icon {
  width: 22px;
  height: 22px;
  color: #8b5cf6;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #1e1b4b;
}

.badge {
  background: linear-gradient(135deg, #8b5cf6, #6d28d9);
  color: white;
  font-size: 11px;
  padding: 6px 14px;
  border-radius: 14px;
  font-weight: 600;
  letter-spacing: 0.3px;
}

.count-badge {
  background: #f3f4f6;
  color: #6b7280;
  font-size: 12px;
  padding: 4px 12px;
  border-radius: 12px;
  font-weight: 600;
}

/* Form */
.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 10px;
}

.required {
  color: #ef4444;
}

.form-row {
  display: flex;
  gap: 16px;
}

.flex-1 {
  flex: 1;
}

textarea {
  width: 100%;
  padding: 16px;
  border: 2px solid #e5e7eb;
  border-radius: 14px;
  font-size: 15px;
  color: #374151;
  resize: vertical;
  font-family: inherit;
  line-height: 1.7;
  transition: all 0.2s;
  box-sizing: border-box;
}

textarea:focus {
  outline: none;
  border-color: #8b5cf6;
  box-shadow: 0 0 0 4px rgba(139, 92, 246, 0.1);
  background: #fafbff;
}

textarea:disabled {
  background: #f9fafb;
  cursor: not-allowed;
  opacity: 0.7;
}

select {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  font-size: 15px;
  color: #374151;
  background: white;
  font-family: inherit;
  transition: all 0.2s;
  cursor: pointer;
  appearance: auto;
}

select:focus {
  outline: none;
  border-color: #8b5cf6;
  box-shadow: 0 0 0 4px rgba(139, 92, 246, 0.1);
}

select:disabled {
  background: #f9fafb;
  cursor: not-allowed;
  opacity: 0.7;
}

.char-count {
  display: block;
  text-align: right;
  font-size: 12px;
  color: #9ca3af;
  margin-top: 8px;
  font-weight: 500;
}

/* Slider */
.slider-group {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 4px 0;
}

.slider-group span {
  font-size: 12px;
  color: #9ca3af;
  min-width: 24px;
  text-align: center;
}

input[type="range"] {
  flex: 1;
  height: 6px;
  appearance: none;
  background: #e5e7eb;
  border-radius: 3px;
  outline: none;
}

input[type="range"]::-webkit-slider-thumb {
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #8b5cf6;
  cursor: pointer;
  border: 2px solid white;
  box-shadow: 0 2px 6px rgba(139, 92, 246, 0.3);
}

input[type="range"]:disabled {
  opacity: 0.5;
}

input[type="range"]:disabled::-webkit-slider-thumb {
  cursor: not-allowed;
}

/* Buttons */
.submit-btn {
  width: 100%;
  padding: 16px 24px;
  background: linear-gradient(135deg, #8b5cf6, #6d28d9);
  color: white;
  border: none;
  border-radius: 14px;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 4px;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(139, 92, 246, 0.4);
}

.submit-btn:active:not(:disabled) {
  transform: translateY(0);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-icon {
  font-size: 18px;
}

/* Status */
.status-badge {
  font-size: 13px;
  padding: 6px 14px;
  border-radius: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.dot.animate {
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.status-badge.pending {
  background: #fef3c7;
  color: #d97706;
}
.status-badge.pending .dot { background: #f59e0b; }

.status-badge.processing {
  background: #dbeafe;
  color: #2563eb;
}
.status-badge.processing .dot { background: #3b82f6; }

.status-badge.success {
  background: #d1fae5;
  color: #059669;
}
.status-badge.success .dot { background: #10b981; }

.status-badge.failed {
  background: #fee2e2;
  color: #dc2626;
}
.status-badge.failed .dot { background: #ef4444; }

/* Progress Bar */
.progress-bar {
  width: 100%;
  height: 10px;
  background: #f3f4f6;
  border-radius: 6px;
  overflow: hidden;
  margin-bottom: 20px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #8b5cf6, #6d28d9);
  border-radius: 6px;
  transition: width 0.5s ease;
}

/* Result Content */
.result-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.result-text {
  padding: 20px;
  background: linear-gradient(135deg, #f9fafb, #f3f4f6);
  border-radius: 16px;
  font-size: 15px;
  line-height: 1.8;
  color: #374151;
  white-space: pre-wrap;
  border: 1px solid #e5e7eb;
}

.result-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.action-btn {
  padding: 12px 24px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
  border: none;
  transition: all 0.2s;
}

.action-btn.primary {
  background: linear-gradient(135deg, #8b5cf6, #6d28d9);
  color: white;
}

.action-btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(139, 92, 246, 0.35);
}

.action-btn.secondary {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #e5e7eb;
}

.action-btn.secondary:hover {
  background: #e8eaf0;
  transform: translateY(-2px);
}

.btn-icon-svg {
  width: 18px;
  height: 18px;
}

/* Audio Player */
.audio-player {
  padding: 20px;
  background: linear-gradient(135deg, #f0f5ff, #f5f0ff);
  border-radius: 16px;
  border: 1px solid #e8e4ff;
}

.audio-control {
  width: 100%;
  height: 48px;
  border-radius: 12px;
}

.audio-control:focus {
  outline: none;
}

/* Error */
.error-msg {
  padding: 16px 20px;
  background: #fef2f2;
  border-radius: 14px;
  color: #dc2626;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 10px;
  border: 1px solid #fecaca;
}

.error-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

/* History Filter */
.history-filter {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  padding: 0 4px;
}

.filter-btn {
  padding: 6px 16px;
  border-radius: 20px;
  border: 1px solid #e5e7eb;
  background: white;
  font-size: 12px;
  font-weight: 500;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-btn:hover {
  border-color: #8b5cf6;
  color: #8b5cf6;
}

.filter-btn.active {
  background: #8b5cf6;
  border-color: #8b5cf6;
  color: white;
}

/* History List */
.history-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  overflow-y: auto;
  flex: 1;
  min-height: 0;
  padding-right: 4px;
}

.history-list::-webkit-scrollbar { width: 6px; }
.history-list::-webkit-scrollbar-track { background: #f3f4f6; border-radius: 3px; }
.history-list::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 3px; }
.history-list::-webkit-scrollbar-thumb:hover { background: #9ca3af; }

.history-item {
  display: flex;
  align-items: center;
  padding: 14px 16px;
  background: #f9fafb;
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid transparent;
  gap: 12px;
}

.history-item:hover {
  background: #f3f4f6;
  transform: translateX(4px);
}

.history-item.active {
  background: linear-gradient(135deg, #f0f5ff, #e8e4ff);
  border-color: #8b5cf6;
}

.history-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.history-icon.pending { background: #fef3c7; color: #f59e0b; }
.history-icon.processing { background: #dbeafe; color: #3b82f6; }
.history-icon.success { background: #d1fae5; color: #10b981; }
.history-icon.failed { background: #fee2e2; color: #ef4444; }

.item-icon-svg {
  width: 20px;
  height: 20px;
}

.history-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
  overflow: hidden;
}

.history-type {
  font-size: 13px;
  color: #374151;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.history-time {
  font-size: 11px;
  color: #9ca3af;
}

.history-status {
  font-size: 11px;
  padding: 5px 12px;
  border-radius: 10px;
  flex-shrink: 0;
  font-weight: 600;
}

.history-status.pending { background: #fef3c7; color: #d97706; }
.history-status.processing { background: #dbeafe; color: #2563eb; }
.history-status.success { background: #d1fae5; color: #059669; }
.history-status.failed { background: #fee2e2; color: #dc2626; }

.empty-hint {
  text-align: center;
  padding: 48px 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.empty-icon {
  width: 64px;
  height: 64px;
  color: #d1d5db;
  margin-bottom: 8px;
}

.empty-hint p {
  font-size: 15px;
  color: #6b7280;
  margin: 0;
  font-weight: 500;
}

.empty-hint span {
  font-size: 13px;
  color: #9ca3af;
}

@media (max-width: 1200px) {
  .main-content {
    flex-direction: column;
  }
  .left-panel {
    min-width: auto;
  }
  .right-panel {
    max-width: none;
  }
}
</style>
