<template>
  <div class="avatar-page">
    <div class="main-content">
      <div class="left-panel">
        <!-- 输入卡片 -->
        <div class="input-card">
          <div class="card-header">
            <div class="header-title">
              <svg viewBox="0 0 24 24" class="header-icon" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                <circle cx="12" cy="7" r="4"></circle>
              </svg>
              <h3>AI 数字人生成</h3>
            </div>
            <span class="badge">视频驱动</span>
          </div>

          <!-- 上传人物参考图 -->
          <div class="form-group">
            <label>人物参考图</label>
            <div class="upload-area" @click="triggerUpload" @dragover.prevent @drop.prevent="handleDrop">
              <input
                ref="fileInput"
                type="file"
                accept="image/*"
                style="display: none"
                @change="handleFileSelect"
              />
              <template v-if="!referenceImage">
                <svg viewBox="0 0 24 24" class="upload-icon" fill="none" stroke="currentColor" stroke-width="1.5">
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                  <circle cx="8.5" cy="8.5" r="1.5"></circle>
                  <polyline points="21,15 16,10 5,21"></polyline>
                </svg>
                <p class="upload-text">点击或拖拽上传人物照片</p>
                <p class="upload-hint">支持 JPG/PNG，建议正面半身照</p>
              </template>
              <div v-else class="preview-container">
                <img :src="referenceImage" class="preview-img" alt="参考图" />
                <button class="remove-btn" @click.stop="removeImage">✕</button>
              </div>
            </div>
          </div>

          <!-- 驱动文本 -->
          <div class="form-group">
            <label>驱动文本（数字人要说的话）</label>
            <textarea
              v-model="form.text"
              placeholder="请输入数字人要说的话，例如：大家好，欢迎来到AI超市平台，我们致力于为企业提供全方位的AI解决方案..."
              rows="5"
              :disabled="submitting"
            ></textarea>
            <span class="char-count">{{ form.text.length }} / 1000</span>
          </div>

          <!-- 辅助参数 -->
          <div class="form-row">
            <div class="form-group flex-1">
              <label>语音类型</label>
              <select v-model="form.voice" :disabled="submitting">
                <option value="female">女声 - 温柔</option>
                <option value="male">男声 - 沉稳</option>
                <option value="female_bright">女声 - 明亮</option>
                <option value="male_warm">男声 - 温暖</option>
              </select>
            </div>
            <div class="form-group flex-1">
              <label>语速</label>
              <select v-model="form.speed" :disabled="submitting">
                <option value="0.8">慢速 (0.8x)</option>
                <option value="1.0">标准 (1.0x)</option>
                <option value="1.2">快速 (1.2x)</option>
              </select>
            </div>
            <div class="form-group flex-1">
              <label>分辨率</label>
              <select v-model="form.resolution" :disabled="submitting">
                <option value="720p">720p (1280x720)</option>
                <option value="1080p">1080p (1920x1080)</option>
              </select>
            </div>
          </div>

          <button
            class="submit-btn"
            :disabled="submitting || !form.text.trim() || !referenceImage"
            @click="handleSubmit"
          >
            <span class="btn-icon">🎬</span>
            <span v-if="!submitting">生成数字人</span>
            <span v-else>生成中...</span>
          </button>
        </div>

        <!-- 结果展示卡片 -->
        <div class="result-card" v-if="showResult">
          <div class="card-header">
            <div class="header-title">
              <svg viewBox="0 0 24 24" class="header-icon" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="23 7 16 12 23 17 23 7"></polygon>
                <rect x="1" y="5" width="15" height="14" rx="2" ry="2"></rect>
              </svg>
              <h3>生成结果</h3>
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

          <!-- 视频播放器 -->
          <div class="video-container" v-if="taskStatus === 2 && resultVideoUrl">
            <video
              ref="videoPlayer"
              :src="resultVideoUrl"
              controls
              autoplay
              class="video-player"
              @loadedmetadata="onVideoLoaded"
            ></video>
            <div class="video-actions">
              <button class="action-btn" @click="handleDownload">
                <svg viewBox="0 0 24 24" class="btn-icon-svg" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                  <polyline points="7 10 12 15 17 10"></polyline>
                  <line x1="12" y1="15" x2="12" y2="3"></line>
                </svg>
                下载视频
              </button>
              <button class="action-btn secondary" @click="handleCopyLink">
                <svg viewBox="0 0 24 24" class="btn-icon-svg" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path>
                  <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path>
                </svg>
                复制链接
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

      <!-- 右侧历史记录 -->
      <div class="right-panel">
        <div class="history-card">
          <div class="card-header">
            <div class="header-title">
              <svg viewBox="0 0 24 24" class="header-icon" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <polyline points="12,6 12,12 16,14"></polyline>
              </svg>
              <h3>生成记录</h3>
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
                  <polygon points="23 7 16 12 23 17 23 7"></polygon>
                  <rect x="1" y="5" width="15" height="14" rx="2" ry="2"></rect>
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
              <p>暂无生成记录</p>
              <span>开始您的第一次数字人生成吧</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { createTask, getTaskDetail, getTaskResult, getUserTasks } from '@/api/task'
import type { TaskListItem } from '@/api/task'

const form = reactive({
  text: '',
  voice: 'female',
  speed: '1.0',
  resolution: '720p'
})

const fileInput = ref<HTMLInputElement | null>(null)
const referenceImage = ref<string>('')
const referenceFile = ref<File | null>(null)

const submitting = ref(false)
const showResult = ref(false)
const currentTaskId = ref<number | null>(null)

const taskStatus = ref(0)
const progress = ref(0)
const errorMsg = ref('')
const resultVideoUrl = ref('')

let eventSource: EventSource | null = null

const getToken = () => {
  return localStorage.getItem('token') || ''
}

// ========== 图片上传 ==========
const triggerUpload = () => {
  fileInput.value?.click()
}

const handleFileSelect = (e: Event) => {
  const target = e.target as HTMLInputElement
  if (target.files && target.files[0]) {
    validateAndSetFile(target.files[0])
  }
}

const handleDrop = (e: DragEvent) => {
  if (e.dataTransfer?.files && e.dataTransfer.files[0]) {
    validateAndSetFile(e.dataTransfer.files[0])
  }
}

const validateAndSetFile = (file: File) => {
  if (!file.type.startsWith('image/')) {
    alert('请上传图片文件')
    return
  }
  if (file.size > 10 * 1024 * 1024) {
    alert('图片大小不能超过 10MB')
    return
  }
  referenceFile.value = file
  const reader = new FileReader()
  reader.onload = (e) => {
    referenceImage.value = e.target?.result as string
  }
  reader.readAsDataURL(file)
}

const removeImage = () => {
  referenceImage.value = ''
  referenceFile.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

// ========== 历史记录 ==========
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
      const tasks = res.data.filter((t: TaskListItem) => t.taskType === 'avatar_generate')
      historyList.value = tasks.map((t: TaskListItem) => ({
        taskId: t.taskId,
        preview: '数字人 - 任务 #' + t.taskId,
        time: new Date(t.createdAt).toLocaleString(),
        status: t.taskStatus
      }))
    }
  } catch (e) {
    console.error('加载历史记录失败:', e)
  }
}

// ========== 提交任务 ==========
const handleSubmit = async () => {
  if (!form.text.trim() || !referenceImage.value) return

  submitting.value = true
  showResult.value = true
  taskStatus.value = 0
  progress.value = 0
  errorMsg.value = ''
  resultVideoUrl.value = ''

  try {
    const res = await createTask({
      taskType: 'avatar_generate',
      params: {
        text: form.text.trim(),
        voice: form.voice,
        speed: form.speed,
        resolution: form.resolution,
        referenceImage: referenceImage.value // base64 图片数据
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

// ========== SSE 推送 ==========
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

// ========== 获取结果 ==========
const fetchResult = async (taskId: number) => {
  try {
    const res = await getTaskResult(taskId)
    if (res.code === 0) {
      const resources = res.data.resources
      const videoResource = resources && resources.find(r => r.resourceType === 'video')
      if (videoResource) {
        resultVideoUrl.value = videoResource.resourceUrl
      }
    }
  } catch (e: any) {
    console.error('获取结果失败:', e)
  }
}

// ========== 查看历史 ==========
const viewHistory = async (taskId: number) => {
  if (taskId === currentTaskId.value) return

  showResult.value = true
  currentTaskId.value = taskId
  taskStatus.value = 0
  progress.value = 0
  errorMsg.value = ''
  resultVideoUrl.value = ''

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

// ========== 视频操作 ==========
const onVideoLoaded = () => {
  console.log('[Avatar] 视频加载完成')
}

const handleDownload = () => {
  if (!resultVideoUrl.value) return
  const a = document.createElement('a')
  a.href = resultVideoUrl.value
  a.download = `ai-avatar-${currentTaskId.value}.mp4`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
}

const handleCopyLink = async () => {
  if (!resultVideoUrl.value) return
  try {
    await navigator.clipboard.writeText(resultVideoUrl.value)
    alert('✅ 视频链接已复制到剪贴板')
  } catch {
    const textarea = document.createElement('textarea')
    textarea.value = resultVideoUrl.value
    document.body.appendChild(textarea)
    textarea.select()
    document.execCommand('copy')
    document.body.removeChild(textarea)
    alert('✅ 视频链接已复制到剪贴板')
  }
}

// ========== 状态工具 ==========
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
.avatar-page {
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

/* ===== 表单 ===== */
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
  font-size: 14px;
  color: #374151;
  background: white;
  transition: all 0.2s;
  cursor: pointer;
  box-sizing: border-box;
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

/* ===== 上传区域 ===== */
.upload-area {
  border: 2px dashed #d1d5db;
  border-radius: 16px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  background: #fafbff;
}

.upload-area:hover {
  border-color: #8b5cf6;
  background: #f5f3ff;
}

.upload-icon {
  width: 48px;
  height: 48px;
  color: #9ca3af;
  margin-bottom: 12px;
}

.upload-text {
  font-size: 15px;
  color: #374151;
  margin: 0 0 8px;
  font-weight: 500;
}

.upload-hint {
  font-size: 13px;
  color: #9ca3af;
  margin: 0;
}

.preview-container {
  position: relative;
  display: inline-block;
  max-width: 100%;
}

.preview-img {
  max-height: 200px;
  border-radius: 12px;
  object-fit: contain;
}

.remove-btn {
  position: absolute;
  top: -8px;
  right: -8px;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #ef4444;
  color: white;
  border: 2px solid white;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.remove-btn:hover {
  background: #dc2626;
  transform: scale(1.1);
}

/* ===== 提交按钮 ===== */
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

/* ===== 状态标签 ===== */
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

/* ===== 进度条 ===== */
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

/* ===== 视频播放器 ===== */
.video-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.video-player {
  width: 100%;
  border-radius: 14px;
  background: #000;
  max-height: 400px;
}

.video-actions {
  display: flex;
  gap: 12px;
}

.action-btn {
  flex: 1;
  padding: 12px 20px;
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
  justify-content: center;
  gap: 8px;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(139, 92, 246, 0.35);
}

.action-btn.secondary {
  background: #f3f4f6;
  color: #374151;
}

.action-btn.secondary:hover {
  background: #e5e7eb;
  box-shadow: none;
}

.btn-icon-svg {
  width: 18px;
  height: 18px;
}

/* ===== 错误信息 ===== */
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

/* ===== 历史记录 ===== */
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
</style>
