import request from '@/utils/request'

export interface RegisterRequest {
  username: string
  email?: string
  password: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  token: string
  userId: number
}

export interface ApiResponse<T> {
  code: number
  msg: string
  data: T
}

export const register = (data: RegisterRequest) => {
  return request.post<ApiResponse<{ userId: number }>>('/api/auth/register', data)
}

export const login = (data: LoginRequest) => {
  return request.post<ApiResponse<LoginResponse>>('/api/auth/login', data)
}
