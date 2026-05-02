import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const token = ref<string>(localStorage.getItem('token') || '')
  const userId = ref<number>(Number(localStorage.getItem('userId') || 0))
  const username = ref<string>(localStorage.getItem('username') || '')

  const setUserInfo = (tokenVal: string, userIdVal: number, usernameVal: string) => {
    token.value = tokenVal
    userId.value = userIdVal
    username.value = usernameVal
    localStorage.setItem('token', tokenVal)
    localStorage.setItem('userId', String(userIdVal))
    localStorage.setItem('username', usernameVal)
  }

  const logout = () => {
    token.value = ''
    userId.value = 0
    username.value = ''
    localStorage.removeItem('token')
    localStorage.removeItem('userId')
    localStorage.removeItem('username')
  }

  const isLoggedIn = () => {
    return !!token.value
  }

  return {
    token,
    userId,
    username,
    setUserInfo,
    logout,
    isLoggedIn
  }
})
