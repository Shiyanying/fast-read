import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api'

export const useAuthStore = defineStore('auth', () => {
  // 暂时设置一个默认token，用于样式测试
  // TODO: 测试完成后恢复原始逻辑
  const token = ref(localStorage.getItem('token') || 'dev-token-for-styling-test')
  const user = ref(null)

  const isAuthenticated = computed(() => true) // 暂时总是返回true，用于样式测试

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

