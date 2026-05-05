import request from '@/utils/request'

export interface CreateTaskRequest {
  taskType: string
  params: Record<string, any>
}

export interface TaskResponse {
  taskId: number
  taskStatus: number
}

export interface TaskDetailResponse {
  taskId: number
  taskType: string
  taskStatus: number
  progress: number
  errorMsg: string | null
  createdAt: string
  finishedAt: string | null
}

export interface ResourceItem {
  resourceType: string
  resourceUrl: string
  contentText: string | null
  coverUrl: string | null
  duration: number | null
}

export interface TaskResultResponse {
  taskId: number
  taskStatus: number
  resources: ResourceItem[]
}

export interface TaskListItem {
  taskId: number
  taskType: string
  taskStatus: number
  progress: number
  createdAt: string
  finishedAt: string | null
}

export interface ApiResponse<T> {
  code: number
  msg: string
  data: T
}

export const createTask = (data: CreateTaskRequest): Promise<ApiResponse<TaskResponse>> => {
  return request.post<any, ApiResponse<TaskResponse>>('/api/task/create', data)
}

export const getTaskDetail = (taskId: number): Promise<ApiResponse<TaskDetailResponse>> => {
  return request.get<any, ApiResponse<TaskDetailResponse>>(`/api/task/${taskId}`)
}

export const getTaskResult = (taskId: number): Promise<ApiResponse<TaskResultResponse>> => {
  return request.get<any, ApiResponse<TaskResultResponse>>(`/api/task/${taskId}/result`)
}

export const getUserTasks = (): Promise<ApiResponse<TaskListItem[]>> => {
  return request.get<any, ApiResponse<TaskListItem[]>>('/api/task/list')
}

export interface AvatarItem {
  id: string
  name: string
  thumbnail: string
  videos: string[]
}

export const listAvatars = (): Promise<ApiResponse<AvatarItem[]>> => {
  return request.get<any, ApiResponse<AvatarItem[]>>('/api/avatar/list')
}

export interface UploadAudioResult {
  url: string
  fileName: string
  size: number
}

export const uploadAudio = (file: File): Promise<ApiResponse<UploadAudioResult>> => {
  const formData = new FormData()
  formData.append('file', file)
  return request.post<any, ApiResponse<UploadAudioResult>>('/api/upload/audio', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}



