<template>
  <div class="copywriting-page">
    <div class="main-content">
      <div class="left-panel">
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
              v-model="form.prompt"
              placeholder="请输入您想要生成的文案主题或内容描述，例如：写一篇618大促活动推广文案，目标用户为25-35岁女性..."
              rows="7"
              :disabled="submitting"
            ></textarea>
            <span class="char-count">{{ form.prompt.length }} / 2000</span>
          </div>

          <div class="form-group">
            <label>补充要求（可选）</label>
            <textarea
              v-model="form.systemPrompt"
              placeholder="可指定文案风格、语气、字数要求等，例如：风格活泼、字数500字左右、加入emoji表情"
              rows="4"
              :disabled="submitting"
            ></textarea>
          </div>

          <button
            class="submit-btn"
            :disabled="submitting || !form.prompt.trim()"
            @click="handleSubmit"
          >
            <span class="btn-icon">🚀</span>
            <span v-if="!submitting">开始创作</span>
            <span v-else>生成中...</span>
          </button>
        </div>

        <div class="result-card" v-if="showResult">
          <div class="card-header">
            <div class="header-title">
              <svg viewBox="0 0 24 24" class="header-icon" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M9 11l3 3L22 4"></path>
                <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
              </svg>
              <h3>创作结果</h3>
            </div>
            <div class="status-group">
              <span v-if="taskStatus === 0" class="status-badge pending">
                <span class="dot"></span> 排队中
              </span>
              <span v-else-if="taskStatus === 1" class="status-badge processing">
                <span class="dot animate"></span> 生成中 {{ progress }}%
              </span>
              <span v-else-if="taskStatus === 2" class="status-badge success">
                <span class="dot"></span> 已完成
              </span>
              <span v-else-if="taskStatus === 3" class="status-badge failed">
                <span class="dot"></span> 失败
              </span>
            </div>
          </div>

          <div class="progress-bar" v-if="taskStatus === 0 || taskStatus === 1">
            <div class="progress-fill" :style="{ width: progress + '%' }"></div>
          </div>

          <div class="result-content" v-if="taskStatus === 2 && resultText">
            <div class="result-text">{{ resultText }}</div>
            <div class="result-actions">
              <button class="copy-btn" @click="handleCopy">
                <svg viewBox="0 0 24 24" class="btn-icon-svg" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                  <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                </svg>
                复制文案
              </button>
            </div>
          </div>

          <div class="error-msg" v-if="taskStatus === 3 && errorMsg">
            <svg viewBox="0 0 24 24" class="error-icon" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="8" x2="12" y2="12"></line>
              <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
            <span>{{ errorMsg }}</span>
          </div>
        </div>
      </div>

      <div class="right-panel">
        <div class="history-card">
          <div class="card-header">
            <div class="header-title">
              <svg viewBox="0 0 24 24" class="header-icon" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <polyline points="12,6 12,12 16,14"></polyline>
              </svg>
              <h3>创作历史</h3>
            </div>
            <span class="count-badge">{{ historyList.length }}</span>
          </div>

          <div class="history-list">
            <div
              v-for="item in historyList"
              :key="item.taskId"
              class="history-item"
              :class="{ active: currentTaskId === item.taskId }"
              @click="viewHistory(item.taskId)"
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
                <span class="history-prompt">{{ item.preview }}</span>
                <span class="history-time">{{ item.time }}</span>
              </div>
              <span :class="['history-status', getStatusClass(item.status)]">
                {{ getStatusText(item.status) }}
              </span>
            </div>
            <div v-if="historyList.length === 0" class="empty-hint">
              <svg viewBox="0 0 24 24" class="empty-icon" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M9.172 16.172a4 4 0 0 1 5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0z"></path>
              </svg>
              <p>暂无创作记录</p>
              <span>开始您的第一次AI创作吧</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { createTask, getTaskDetail, getTaskResult, getUserTasks, TaskListItem } from '@/api/task'

const form = reactive({
  prompt: '',
  systemPrompt: ''
})

const submitting = ref(false)
const showResult = ref(false)
const currentTaskId = ref<number | null>(null)

const taskStatus = ref(0)
const progress = ref(0)
const errorMsg = ref('')
const resultText = ref('')

let eventSource: EventSource | null = null

const getToken = () => {
  return localStorage.getItem('token') || ''
}

interface HistoryItem {
  taskId: number
  preview: string
  time: string
  status: number
}

const historyList = ref<HistoryItem[]>([])

const loadHistory = async () => {
  try {
    const res = await getUserTasks()
    if (res.code === 0) {
      const tasks = res.data.filter((t: TaskListItem) => t.taskType === 'text2text')
      historyList.value = tasks.map((t: TaskListItem) => ({
        taskId: t.taskId,
        preview: t.taskType + ' - 任务 #' + t.taskId,
        time: new Date(t.createdAt).toLocaleString(),
        status: t.taskStatus
      }))
    }
  } catch (e) {
    console.error('加载历史记录失败:', e)
  }
}

const handleSubmit = async () => {
  if (!form.prompt.trim()) return

  submitting.value = true
  showResult.value = true
  taskStatus.value = 0
  progress.value = 0
  errorMsg.value = ''
  resultText.value = ''

  try {
    const res = await createTask({
      taskType: 'text2text',
      params: {
        prompt: form.prompt.trim(),
        system_prompt: form.systemPrompt.trim() || undefined
      }
    })

    if (res.code === 0) {
      currentTaskId.value = res.data.taskId
      startSse(res.data.taskId)
      await loadHistory()
    } else {
      throw new Error(res.msg || '创建任务失败')
    }
  } catch (e: any) {
    taskStatus.value = 3
    errorMsg.value = e.message || '网络错误'
    submitting.value = false
  }
}

const startSse = (taskId: number) => {
  closeSse()

  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080'
  const token = getToken()
  const url = `${baseUrl}/api/task/${taskId}/subscribe?token=${encodeURIComponent(token)}`

  eventSource = new EventSource(url)

  eventSource.addEventListener('heartbeat', () => {
  })

  eventSource.addEventListener('task-completed', (e: MessageEvent) => {
    console.log('[SSE] 任务完成通知:', e.data)
    submitting.value = false
    taskStatus.value = 2
    if (currentTaskId.value) {
      fetchResult(currentTaskId.value)
    }
    closeSse()
    loadHistory()
  })

  eventSource.addEventListener('task-failed', (e: MessageEvent) => {
    console.log('[SSE] 任务失败通知:', e.data)
    try {
      const data = JSON.parse(e.data)
      submitting.value = false
      taskStatus.value = 3
      errorMsg.value = data.errorMsg || '生成失败'
    } catch {
      errorMsg.value = '生成失败'
    }
    closeSse()
    loadHistory()
  })

  eventSource.onerror = () => {
    console.warn('[SSE] 连接异常，降级到轮询')
    closeSse()
    startPolling(taskId)
  }
}

const closeSse = () => {
  if (eventSource) {
    eventSource.close()
    eventSource = null
  }
}

let pollingTimer: ReturnType<typeof setInterval> | null = null

const startPolling = (taskId: number) => {
  pollingTimer = setInterval(async () => {
    try {
      const res = await getTaskDetail(taskId)
      if (res.code === 0) {
        const data = res.data
        taskStatus.value = data.taskStatus
        progress.value = data.progress

        if (data.taskStatus === 2) {
          if (pollingTimer) {
            clearInterval(pollingTimer)
            pollingTimer = null
          }
          submitting.value = false
          await fetchResult(taskId)
          loadHistory()
        } else if (data.taskStatus === 3) {
          if (pollingTimer) {
            clearInterval(pollingTimer)
            pollingTimer = null
          }
          submitting.value = false
          errorMsg.value = data.errorMsg || '生成失败'
          loadHistory()
        }
      }
    } catch (e: any) {
      console.error('轮询失败:', e)
    }
  }, 2000)
}

const fetchResult = async (taskId: number) => {
  try {
    const res = await getTaskResult(taskId)
    if (res.code === 0) {
      const resources = res.data.resources
      const firstResource = resources && resources.length > 0 ? resources[0] : null
      if (firstResource) {
        resultText.value = firstResource.contentText || firstResource.resourceUrl
      }
    }
  } catch (e: any) {
    console.error('获取结果失败:', e)
  }
}

const viewHistory = async (taskId: number) => {
  if (taskId === currentTaskId.value) return

  showResult.value = true
  currentTaskId.value = taskId
  taskStatus.value = 0
  progress.value = 0
  errorMsg.value = ''
  resultText.value = ''

  try {
    const res = await getTaskDetail(taskId)
    if (res.code === 0) {
      const data = res.data
      taskStatus.value = data.taskStatus
      progress.value = data.progress

      if (data.taskStatus === 2) {
        await fetchResult(taskId)
      } else if (data.taskStatus === 3) {
        errorMsg.value = data.errorMsg || '生成失败'
      } else if (data.taskStatus === 0 || data.taskStatus === 1) {
        startPolling(taskId)
      }
    }
  } catch (e: any) {
    taskStatus.value = 3
    errorMsg.value = e.message || '查询失败'
  }
}

const handleCopy = async () => {
  try {
    await navigator.clipboard.writeText(resultText.value)
    alert('✅ 文案已复制到剪贴板')
  } catch {
    const textarea = document.createElement('textarea')
    textarea.value = resultText.value
    document.body.appendChild(textarea)
    textarea.select()
    document.execCommand('copy')
    document.body.removeChild(textarea)
    alert('✅ 文案已复制到剪贴板')
  }
}

const getStatusClass = (status: number) => {
  const map: Record<number, string> = {
    0: 'pending',
    1: 'processing',
    2: 'success',
    3: 'failed'
  }
  return map[status] || ''
}

const getStatusText = (status: number) => {
  const map: Record<number, string> = {
    0: '排队中',
    1: '生成中',
    2: '已完成',
    3: '失败'
  }
  return map[status] || '未知'
}

onMounted(() => {
  loadHistory()
})

onUnmounted(() => {
  closeSse()
  if (pollingTimer) {
    clearInterval(pollingTimer)
    pollingTimer = null
  }
})
</script>

<style scoped>
.copywriting-page {
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

.char-count {
  display: block;
  text-align: right;
  font-size: 12px;
  color: #9ca3af;
  margin-top: 8px;
  font-weight: 500;
}

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

.status-group {
  display: flex;
  align-items: center;
}

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

.status-badge.pending .dot {
  background: #f59e0b;
}

.status-badge.processing {
  background: #dbeafe;
  color: #2563eb;
}

.status-badge.processing .dot {
  background: #3b82f6;
}

.status-badge.success {
  background: #d1fae5;
  color: #059669;
}

.status-badge.success .dot {
  background: #10b981;
}

.status-badge.failed {
  background: #fee2e2;
  color: #dc2626;
}

.status-badge.failed .dot {
  background: #ef4444;
}

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
  justify-content: flex-end;
}

.copy-btn {
  padding: 12px 24px;
  background: linear-gradient(135deg, #8b5cf6, #6d28d9);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.copy-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(139, 92, 246, 0.35);
}

.btn-icon-svg {
  width: 18px;
  height: 18px;
}

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

.history-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  overflow-y: auto;
  flex: 1;
  min-height: 0;
  padding-right: 4px;
}

.history-list::-webkit-scrollbar {
  width: 6px;
}

.history-list::-webkit-scrollbar-track {
  background: #f3f4f6;
  border-radius: 3px;
}

.history-list::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 3px;
}

.history-list::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #f9fafb;
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid transparent;
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

.history-icon.pending {
  background: #fef3c7;
  color: #f59e0b;
}

.history-icon.processing {
  background: #dbeafe;
  color: #3b82f6;
}

.history-icon.success {
  background: #d1fae5;
  color: #10b981;
}

.history-icon.failed {
  background: #fee2e2;
  color: #ef4444;
}

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
  margin: 0 14px;
}

.history-prompt {
  font-size: 14px;
  color: #374151;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-weight: 500;
}

.history-time {
  font-size: 12px;
  color: #9ca3af;
}

.history-status {
  font-size: 12px;
  padding: 5px 12px;
  border-radius: 10px;
  flex-shrink: 0;
  font-weight: 600;
}

.history-status.pending {
  background: #fef3c7;
  color: #d97706;
}

.history-status.processing {
  background: #dbeafe;
  color: #2563eb;
}

.history-status.success {
  background: #d1fae5;
  color: #059669;
}

.history-status.failed {
  background: #fee2e2;
  color: #dc2626;
}

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
</style>
