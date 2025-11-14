import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(null)

  const isAuthenticated = computed(() => !!token.value)

  async function login(password) {
    try {
      const response = await api.post('/auth/login', {
        password
      })
      token.value = response.data.access_token
      localStorage.setItem('token', token.value)
      return { success: true }
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.detail || '密码错误'
      }
    }
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
  }

  return {
    token,
    user,
    isAuthenticated,
    login,
    logout
  }
})

