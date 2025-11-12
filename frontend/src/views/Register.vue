<template>
  <div class="register-container">
    <div class="register-box">
      <div class="register-header">
        <h1 class="title">注册 ReadSmart</h1>
        <p class="subtitle">开始您的英语学习之旅</p>
      </div>
      
      <el-form
        ref="registerFormRef"
        :model="registerForm"
        :rules="rules"
        class="register-form"
      >
        <el-form-item prop="username">
          <el-input
            v-model="registerForm.username"
            placeholder="用户名"
            size="large"
            prefix-icon="User"
            class="apple-input"
          />
        </el-form-item>
        
        <el-form-item prop="email">
          <el-input
            v-model="registerForm.email"
            placeholder="邮箱"
            size="large"
            prefix-icon="Message"
            class="apple-input"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="密码"
            size="large"
            prefix-icon="Lock"
            class="apple-input"
          />
        </el-form-item>
        
        <el-form-item prop="confirmPassword">
          <el-input
            v-model="registerForm.confirmPassword"
            type="password"
            placeholder="确认密码"
            size="large"
            prefix-icon="Lock"
            class="apple-input"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            @click="handleRegister"
            class="register-button"
          >
            注册
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="footer">
        <span>已有账号？</span>
        <el-link type="primary" @click="$router.push('/login')" class="link">
          立即登录
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
const registerFormRef = ref(null)
const loading = ref(false)

const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度为3-20个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

async function handleRegister() {
  if (!registerFormRef.value) return
  
  await registerFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      const result = await authStore.register(
        registerForm.username,
        registerForm.email,
        registerForm.password
      )
      loading.value = false
      
      if (result.success) {
        ElMessage.success('注册成功，请登录')
        router.push('/login')
      } else {
        ElMessage.error(result.message)
      }
    }
  })
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.register-box {
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

.register-header {
  text-align: center;
  margin-bottom: 40px;
}

.title {
  font-size: 32px;
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

.register-form {
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

.register-button {
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

.register-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 122, 255, 0.4);
}

.register-button:active {
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
  .register-container {
    padding: 16px;
  }
  
  .register-box {
    padding: 32px 24px;
    max-width: 100%;
  }
  
  .title {
    font-size: 24px;
  }
  
  .subtitle {
    font-size: 14px;
  }
  
  .register-form {
    margin-top: 24px;
  }
  
  :deep(.el-input__wrapper) {
    padding: 10px 14px;
  }
  
  .register-button {
    height: 44px;
    font-size: 15px;
  }
}
</style>
