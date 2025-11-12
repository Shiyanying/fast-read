<template>
  <div class="main-layout">
    <header class="header">
      <div class="header-content">
        <div class="header-left">
          <h1 class="logo">ReadSmart</h1>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand" trigger="click" placement="bottom-end">
            <div class="user-info">
              <el-avatar :size="36" :icon="UserFilled" class="user-avatar" />
              <span class="username">{{ authStore.user?.username }}</span>
              <el-icon class="dropdown-icon"><arrow-down /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu class="apple-dropdown">
                <el-dropdown-item command="words" class="dropdown-item">
                  <el-icon><Collection /></el-icon>
                  <span>我的生词本</span>
                </el-dropdown-item>
                <el-dropdown-item divided command="logout" class="dropdown-item">
                  <el-icon><SwitchButton /></el-icon>
                  <span>退出登录</span>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </header>
    
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import { UserFilled, ArrowDown, Collection, SwitchButton } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

function handleCommand(command) {
  if (command === 'logout') {
    authStore.logout()
    ElMessage.success('已退出登录')
    router.push('/login')
  } else if (command === 'words') {
    router.push('/words')
  }
}
</script>

<style scoped>
.main-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  border-bottom: 0.5px solid rgba(0, 0, 0, 0.08);
  box-shadow: var(--apple-shadow-sm);
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 32px;
  height: 64px;
}

.logo {
  margin: 0;
  color: var(--apple-text-primary);
  font-size: 22px;
  font-weight: 600;
  letter-spacing: -0.5px;
  background: linear-gradient(135deg, var(--apple-blue) 0%, #5856D6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 20px;
  transition: var(--apple-transition);
}

.user-info:hover {
  background-color: var(--apple-gray-1);
}

.user-avatar {
  border: 1.5px solid var(--apple-gray-2);
}

.username {
  font-size: 15px;
  font-weight: 500;
  color: var(--apple-text-primary);
}

.dropdown-icon {
  font-size: 12px;
  color: var(--apple-gray-4);
  transition: var(--apple-transition);
}

.user-info:hover .dropdown-icon {
  color: var(--apple-text-primary);
}

.main-content {
  flex: 1;
  background: var(--apple-background);
  padding: 32px;
}

/* Apple-style dropdown */
:deep(.apple-dropdown) {
  border-radius: var(--apple-border-radius);
  box-shadow: var(--apple-shadow-lg);
  border: 0.5px solid rgba(0, 0, 0, 0.08);
  padding: 8px;
  margin-top: 8px;
}

:deep(.dropdown-item) {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 15px;
  transition: var(--apple-transition);
}

:deep(.dropdown-item:hover) {
  background-color: var(--apple-gray-1);
}

@media (max-width: 768px) {
  .header-content {
    padding: 12px 16px;
    height: 56px;
  }
  
  .logo {
    font-size: 20px;
  }
  
  .main-content {
    padding: 16px 12px;
  }
  
  .username {
    display: none;
  }
  
  .user-avatar {
    width: 32px;
    height: 32px;
  }
}
</style>

