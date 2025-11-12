<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <h1 class="title">ReadSmart</h1>
        <p class="subtitle">个性化英语外刊阅读平台</p>
      </div>
      
      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="rules"
        class="login-form"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="用户名"
            size="large"
            prefix-icon="User"
            class="apple-input"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="密码"
            size="large"
            prefix-icon="Lock"
            class="apple-input"
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            @click="handleLogin"
            class="login-button"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="footer">
        <span>还没有账号？</span>
        <el-link type="primary" @click="$router.push('/register')" class="link">
          立即注册
        </el-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()
const loginFormRef = ref(null)
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

async function handleLogin() {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      const result = await authStore.login(loginForm.username, loginForm.password)
      loading.value = false
      
      if (result.success) {
        ElMessage.success('登录成功')
        router.push('/')
      } else {
        ElMessage.error(result.message)
      }
    }
  })
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-box {
  width: 100%;
  max-width: 420px;
  padding: 48px 40px;
  background: var(--apple-card-background);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  border-radius: var(--apple-border-radius-lg);
  border: 0.5px solid rgba(255, 255, 255, 0.3);
  box-shadow: var(--apple-shadow-lg);
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.title {
  font-size: 36px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--apple-blue) 0%, #5856D6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 12px 0;
  letter-spacing: -1px;
}

.subtitle {
  font-size: 15px;
  color: var(--apple-text-secondary);
  margin: 0;
}

.login-form {
  margin-top: 32px;
}

:deep(.apple-input .el-input__wrapper) {
  border-radius: 12px;
  box-shadow: var(--apple-shadow-sm);
  border: 0.5px solid rgba(0, 0, 0, 0.08);
  transition: var(--apple-transition);
  padding: 12px 16px;
}

:deep(.apple-input .el-input__wrapper:hover) {
  box-shadow: var(--apple-shadow-md);
}

:deep(.apple-input .el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1);
}

.login-button {
  width: 100%;
  height: 48px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  background: linear-gradient(135deg, var(--apple-blue) 0%, #5856D6 100%);
  border: none;
  box-shadow: 0 4px 16px rgba(0, 122, 255, 0.3);
  transition: var(--apple-transition);
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 122, 255, 0.4);
}

.login-button:active {
  transform: translateY(0);
}

.footer {
  text-align: center;
  margin-top: 32px;
  color: var(--apple-text-secondary);
  font-size: 14px;
}

.link {
  font-weight: 500;
  margin-left: 4px;
}

:deep(.el-link__inner) {
  color: var(--apple-blue);
}

@media (max-width: 480px) {
  .login-container {
    padding: 16px;
  }
  
  .login-box {
    padding: 32px 24px;
    max-width: 100%;
  }
  
  .title {
    font-size: 28px;
  }
  
  .subtitle {
    font-size: 14px;
  }
  
  .login-form {
    margin-top: 24px;
  }
  
  :deep(.el-input__wrapper) {
    padding: 10px 14px;
  }
  
  .login-button {
    height: 44px;
    font-size: 15px;
  }
}
</style>
