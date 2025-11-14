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
        <el-form-item prop="password" :error="passwordError">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入访问密码"
            size="large"
            prefix-icon="Lock"
            class="apple-input"
            :class="{ 'input-error': passwordError }"
            @keyup.enter="handleLogin"
            @input="clearError"
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
            进入
          </el-button>
        </el-form-item>
      </el-form>
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
const passwordError = ref('')

const loginForm = reactive({
  password: ''
})

const rules = {
  password: [
    { required: true, message: '请输入访问密码', trigger: 'blur' }
  ]
}

function clearError() {
  passwordError.value = ''
}

async function handleLogin() {
  if (!loginFormRef.value) return
  
  clearError()
  
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      const result = await authStore.login(loginForm.password)
      loading.value = false
      
      if (result.success) {
        ElMessage.success('验证成功')
        router.push('/')
      } else {
        passwordError.value = result.message || '密码错误，请重新输入'
        ElMessage.error(result.message || '密码错误')
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
  background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
  padding: 20px;
}

.login-box {
  width: 100%;
  max-width: 420px;
  padding: 48px 40px;
  background: var(--rs-white);
  border-radius: var(--rs-radius-2xl);
  border: 1px solid var(--rs-gray-100);
  box-shadow: var(--rs-shadow-lg);
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.title {
  font-size: 36px;
  font-weight: 700;
  background: linear-gradient(to right, var(--rs-gray-900), var(--rs-gray-700));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 12px 0;
  letter-spacing: -1px;
}

.subtitle {
  font-size: 15px;
  color: var(--rs-gray-500);
  margin: 0;
}

.login-form {
  margin-top: 32px;
}

:deep(.apple-input .el-input__wrapper) {
  border-radius: var(--rs-radius-xl);
  box-shadow: var(--rs-shadow-sm);
  border: 1px solid var(--rs-gray-200);
  transition: var(--rs-transition);
  padding: 12px 16px;
}

:deep(.apple-input .el-input__wrapper:hover) {
  box-shadow: var(--rs-shadow-md);
  border-color: var(--rs-gray-300);
}

:deep(.apple-input .el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px rgba(26, 26, 26, 0.1);
  border-color: var(--rs-gray-900);
}

:deep(.input-error .el-input__wrapper) {
  border-color: #f56565;
  box-shadow: 0 0 0 2px rgba(245, 101, 101, 0.1);
}

:deep(.input-error .el-input__wrapper.is-focus) {
  border-color: #f56565;
  box-shadow: 0 0 0 2px rgba(245, 101, 101, 0.2);
}

:deep(.el-form-item__error) {
  color: #f56565;
  font-size: 13px;
  margin-top: 6px;
}

.login-button {
  width: 100%;
  height: 48px;
  border-radius: var(--rs-radius-xl);
  font-size: 16px;
  font-weight: 600;
  background: linear-gradient(to bottom right, var(--rs-gray-900), var(--rs-gray-800));
  border: none;
  box-shadow: var(--rs-shadow-sm);
  transition: var(--rs-transition);
  color: white;
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: var(--rs-shadow-md);
  background: linear-gradient(to bottom right, var(--rs-gray-800), var(--rs-gray-700));
}

.login-button:active {
  transform: translateY(0);
}

.footer {
  text-align: center;
  margin-top: 32px;
  color: var(--rs-gray-500);
  font-size: 14px;
}

.link {
  font-weight: 500;
  margin-left: 4px;
}

:deep(.el-link__inner) {
  color: var(--rs-gray-700);
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
