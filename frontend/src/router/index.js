import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue')
      },
      {
        path: 'reader/:documentId',
        name: 'Reader',
        component: () => import('@/views/Reader.vue')
      },
      {
        path: 'words',
        name: 'Words',
        component: () => import('@/views/Words.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫 - 暂时禁用认证检查，方便样式测试
router.beforeEach((to, from, next) => {
  // 暂时允许所有页面直接访问，用于样式测试
  // TODO: 测试完成后恢复认证检查
  next()
  
  // 原始认证逻辑（已注释）
  // const authStore = useAuthStore()
  // const isAuthenticated = authStore.isAuthenticated
  // if (to.meta.requiresAuth && !isAuthenticated) {
  //   next({ name: 'Login' })
  // } else if (to.name === 'Login' && isAuthenticated) {
  //   next({ name: 'Dashboard' })
  // } else {
  //   next()
  // }
})

export default router

