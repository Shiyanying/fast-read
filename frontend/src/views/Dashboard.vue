<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- 标签页 -->
    <div class="flex gap-1 mb-8">
      <button class="px-6 py-3 text-sm font-semibold text-gray-900 bg-white rounded-xl soft-shadow border border-gray-100">外刊库</button>
      <button class="px-6 py-3 text-sm font-medium text-gray-500 hover:text-gray-900 hover:bg-white rounded-xl transition-colors" @click="router.push('/words')">生词本</button>
    </div>

    <!-- 上传卡片 -->
    <div class="bg-white rounded-2xl soft-shadow-lg border border-gray-100 mb-8 card-lift">
      <el-upload
        ref="uploadRef"
        :action="uploadUrl"
        :headers="uploadHeaders"
        :on-success="handleUploadSuccess"
        :on-error="handleUploadError"
        :before-upload="beforeUpload"
        :show-file-list="false"
        drag
        class="upload-area"
      >
        <div class="flex flex-col items-center justify-center py-10 border-2 border-dashed border-gray-200 rounded-xl hover:border-gray-300 hover:bg-gray-50/50 transition-all cursor-pointer">
          <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-gray-900 to-gray-800 flex items-center justify-center mb-4 soft-shadow">
            <el-icon class="w-8 h-8 text-white"><upload-filled /></el-icon>
          </div>
          <p class="text-lg font-semibold text-gray-900 mb-1">拖拽文件到此处上传</p>
          <p class="text-sm text-gray-500">或 <span class="text-gray-900 font-semibold">点击选择文件</span></p>
          <p class="text-xs text-gray-400 mt-3">支持 .txt, .pdf, .epub 格式，文件大小不超过 10MB</p>
        </div>
      </el-upload>
    </div>

    <!-- 文档网格 -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mb-12" v-if="filteredDocuments.length > 0">
      <div
        v-for="doc in filteredDocuments"
        :key="doc.id"
        class="bg-white rounded-2xl soft-shadow-lg border border-gray-100 p-6 card-lift cursor-pointer"
        @click="openDocument(doc.id)"
      >
        <div class="flex items-start justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-900 flex-1 pr-2">{{ doc.title }}</h3>
          <button 
            class="w-8 h-8 rounded-lg hover:bg-gray-100 flex items-center justify-center transition-colors flex-shrink-0"
            @click.stop="handleDelete(doc.id)"
          >
            <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
            </svg>
          </button>
        </div>
        <div class="space-y-2.5 text-sm text-gray-600">
          <div class="flex items-center gap-2">
            <div class="w-4 h-4 rounded bg-gray-200"></div>
            <span>{{ doc.filename }}</span>
          </div>
          <div class="flex items-center gap-2">
            <div class="w-4 h-4 rounded bg-gray-200"></div>
            <span>{{ formatDate(doc.created_at) }}</span>
          </div>
          <div class="flex items-center gap-2">
            <div class="w-4 h-4 rounded bg-gray-200"></div>
            <span>{{ doc.total_pages }} 页</span>
          </div>
        </div>
      </div>
    </div>
    
    <div class="empty-state" v-else>
      <el-empty description="暂无文档">
        <template #image>
          <div class="empty-icon">📚</div>
        </template>
      </el-empty>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import api from '@/api'

const router = useRouter()
const authStore = useAuthStore()
const uploadRef = ref(null)
const documents = ref([])
const searchKeyword = ref('')

const uploadUrl = '/api/v1/documents/upload'
const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${authStore.token}`
}))

const filteredDocuments = computed(() => {
  if (!searchKeyword.value) {
    return documents.value
  }
  const keyword = searchKeyword.value.toLowerCase()
  return documents.value.filter(doc =>
    doc.title.toLowerCase().includes(keyword) ||
    doc.filename.toLowerCase().includes(keyword)
  )
})

async function fetchDocuments() {
  try {
    const response = await api.get('/documents/')
    documents.value = response.data.documents
  } catch (error) {
    ElMessage.error('获取文档列表失败')
  }
}

function beforeUpload(file) {
  const validTypes = ['text/plain', 'application/pdf', 'application/epub+zip']
  const isValidType = validTypes.includes(file.type) ||
    file.name.endsWith('.txt') ||
    file.name.endsWith('.pdf') ||
    file.name.endsWith('.epub')
  
  if (!isValidType) {
    ElMessage.error('只支持 .txt, .pdf, .epub 格式的文件')
    return false
  }
  
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过 10MB')
    return false
  }
  
  return true
}

function handleUploadSuccess(response) {
  ElMessage.success('上传成功')
  fetchDocuments()
}

function handleUploadError() {
  ElMessage.error('上传失败')
}

function openDocument(documentId) {
  router.push(`/reader/${documentId}`)
}

async function handleDelete(documentId) {
  try {
    await ElMessageBox.confirm('确定要删除这个文档吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await api.delete(`/documents/${documentId}`)
    ElMessage.success('删除成功')
    fetchDocuments()
  } catch (error) {
    if (error === 'cancel' || error?.toString().includes('cancel')) {
      return
    }
    const errorMessage = error?.response?.data?.detail || error?.message || '删除失败'
    ElMessage.error(errorMessage)
    console.error('删除文档失败:', error)
  }
}

function formatDate(dateString) {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

onMounted(() => {
  fetchDocuments()
})
</script>

<style scoped>
:deep(.el-upload-dragger) {
  background: transparent;
  border: none;
  padding: 0;
  width: 100%;
}

.upload-area {
  width: 100%;
}

.empty-state {
  padding: 80px 20px;
  text-align: center;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}
</style>
