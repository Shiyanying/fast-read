<template>
  <div class="main-layout">
    <!-- 导航栏 - 完全按照 readsmart_3.html -->
    <nav class="sticky top-0 z-50 bg-white/80 backdrop-blur-xl border-b border-gray-100">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <h1 class="text-2xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">ReadSmart</h1>
          <div class="flex items-center gap-2">
            <button 
              class="w-10 h-10 rounded-xl bg-gradient-to-br from-gray-900 to-gray-800 text-white flex items-center justify-center soft-shadow hover:from-gray-800 hover:to-gray-700 transition-all"
              @click="router.push('/words')"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
              </svg>
            </button>
            <el-dropdown @command="handleCommand" trigger="click" placement="bottom-end">
              <button class="w-10 h-10 rounded-xl bg-white border border-gray-200 text-gray-700 flex items-center justify-center soft-shadow hover:border-gray-300 hover:bg-gray-50 transition-all">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                </svg>
              </button>
              <template #dropdown>
                <el-dropdown-menu class="rs-dropdown">
                  <el-dropdown-item command="logout" class="dropdown-item">
                    <el-icon><SwitchButton /></el-icon>
                    <span>退出</span>
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </div>
    </nav>
    
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import { SwitchButton } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

function handleCommand(command) {
  if (command === 'logout') {
    authStore.logout()
    ElMessage.success('已退出')
    router.push('/login')
  }
}
</script>

<style scoped>
.main-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
}

/* Dropdown样式 */
:deep(.rs-dropdown) {
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1), 0 4px 8px rgba(0, 0, 0, 0.12);
  border: 1px solid #f5f5f5;
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
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

:deep(.dropdown-item:hover) {
  background-color: #fafafa;
}
</style>
