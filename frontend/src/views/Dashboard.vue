<template>
  <div class="dashboard">
    <div class="upload-section">
      <div class="upload-card">
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
          <div class="upload-content">
            <div class="upload-icon-wrapper">
              <el-icon class="upload-icon"><upload-filled /></el-icon>
            </div>
            <div class="upload-text">
              <p class="upload-title">拖拽文件到此处上传</p>
              <p class="upload-subtitle">或 <span class="upload-link">点击选择文件</span></p>
            </div>
            <p class="upload-tip">
              支持 .txt, .pdf, .epub 格式，文件大小不超过 10MB
            </p>
          </div>
        </el-upload>
      </div>
    </div>
    
    <div class="library-section">
      <div class="section-header">
        <h2 class="section-title">我的外刊库</h2>
        <div class="search-wrapper">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索文档..."
            class="search-input"
            clearable
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon class="search-icon"><Search /></el-icon>
            </template>
          </el-input>
        </div>
      </div>
      
      <div class="document-grid" v-if="filteredDocuments.length > 0">
        <div
          v-for="doc in filteredDocuments"
          :key="doc.id"
          class="document-card"
          @click="openDocument(doc.id)"
        >
          <div class="card-header">
            <h3 class="doc-title">{{ doc.title }}</h3>
            <el-button
              type="danger"
              :icon="Delete"
              circle
              size="small"
              class="delete-btn"
              @click.stop="handleDelete(doc.id)"
            />
          </div>
          <div class="card-content">
            <div class="doc-meta">
              <el-icon class="meta-icon"><Document /></el-icon>
              <span class="meta-text">{{ doc.filename }}</span>
            </div>
            <div class="doc-meta">
              <el-icon class="meta-icon"><Calendar /></el-icon>
              <span class="meta-text">{{ formatDate(doc.created_at) }}</span>
            </div>
            <div class="doc-meta">
              <el-icon class="meta-icon"><Files /></el-icon>
              <span class="meta-text">{{ doc.total_pages }} 页</span>
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  UploadFilled, Search, Delete, Document, Calendar, Files
} from '@element-plus/icons-vue'
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

function handleSearch() {
  // 搜索逻辑已在 computed 中处理
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
    // 用户取消操作时不显示错误
    if (error === 'cancel' || error?.toString().includes('cancel')) {
      return
    }
    
    // 显示详细的错误信息
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
.dashboard {
  max-width: 1400px;
  margin: 0 auto;
}

.upload-section {
  margin-bottom: 40px;
}

.upload-card {
  background: var(--apple-card-background);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  border-radius: var(--apple-border-radius-lg);
  border: 0.5px solid rgba(0, 0, 0, 0.08);
  box-shadow: var(--apple-shadow-md);
  overflow: hidden;
  transition: var(--apple-transition);
}

.upload-card:hover {
  box-shadow: var(--apple-shadow-lg);
  transform: translateY(-2px);
}

.upload-area {
  width: 100%;
}

:deep(.el-upload-dragger) {
  background: transparent;
  border: none;
  padding: 60px 40px;
  width: 100%;
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.upload-icon-wrapper {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--apple-blue) 0%, #5856D6 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 16px rgba(0, 122, 255, 0.2);
}

.upload-icon {
  font-size: 36px;
  color: white;
}

.upload-text {
  text-align: center;
}

.upload-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--apple-text-primary);
  margin: 0 0 8px 0;
}

.upload-subtitle {
  font-size: 15px;
  color: var(--apple-text-secondary);
  margin: 0;
}

.upload-link {
  color: var(--apple-blue);
  font-weight: 500;
  cursor: pointer;
}

.upload-tip {
  font-size: 13px;
  color: var(--apple-text-secondary);
  margin: 0;
  margin-top: 8px;
}

.library-section {
  background: var(--apple-card-background);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  border-radius: var(--apple-border-radius-lg);
  border: 0.5px solid rgba(0, 0, 0, 0.08);
  box-shadow: var(--apple-shadow-md);
  padding: 32px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  flex-wrap: wrap;
  gap: 20px;
}

.section-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--apple-text-primary);
  margin: 0;
  letter-spacing: -0.5px;
}

.search-wrapper {
  flex: 1;
  max-width: 400px;
}

.search-input {
  width: 100%;
}

:deep(.el-input__wrapper) {
  border-radius: 20px;
  box-shadow: var(--apple-shadow-sm);
  border: 0.5px solid rgba(0, 0, 0, 0.08);
  transition: var(--apple-transition);
}

:deep(.el-input__wrapper:hover) {
  box-shadow: var(--apple-shadow-md);
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1);
}

.search-icon {
  color: var(--apple-gray-4);
}

.document-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
}

.document-card {
  background: white;
  border-radius: var(--apple-border-radius);
  border: 0.5px solid rgba(0, 0, 0, 0.08);
  padding: 24px;
  cursor: pointer;
  transition: var(--apple-transition);
  box-shadow: var(--apple-shadow-sm);
}

.document-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--apple-shadow-lg);
  border-color: rgba(0, 122, 255, 0.2);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  gap: 12px;
}

.doc-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--apple-text-primary);
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  line-height: 1.4;
  flex: 1;
}

.delete-btn {
  flex-shrink: 0;
  opacity: 0.6;
  transition: var(--apple-transition);
}

.delete-btn:hover {
  opacity: 1;
  transform: scale(1.1);
}

.card-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.doc-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--apple-text-secondary);
  font-size: 14px;
}

.meta-icon {
  font-size: 16px;
  color: var(--apple-gray-4);
}

.meta-text {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.empty-state {
  padding: 80px 20px;
  text-align: center;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

@media (max-width: 768px) {
  .dashboard {
    padding: 0;
  }
  
  .upload-section {
    margin-bottom: 24px;
  }
  
  .upload-card {
    border-radius: var(--apple-border-radius);
  }
  
  .upload-content {
    padding: 32px 16px;
    gap: 12px;
  }
  
  .upload-icon-wrapper {
    width: 64px;
    height: 64px;
  }
  
  .upload-icon {
    font-size: 28px;
  }
  
  .upload-title {
    font-size: 18px;
  }
  
  .upload-subtitle {
    font-size: 14px;
  }
  
  .upload-tip {
    font-size: 12px;
  }
  
  .library-section {
    padding: 20px 16px;
    border-radius: var(--apple-border-radius);
  }
  
  .section-header {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
    margin-bottom: 24px;
  }
  
  .section-title {
    font-size: 22px;
  }
  
  .search-wrapper {
    max-width: 100%;
  }
  
  .document-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .document-card {
    padding: 20px;
  }
  
  .doc-title {
    font-size: 16px;
  }
  
  .doc-meta {
    font-size: 13px;
    gap: 8px;
  }
  
  .meta-icon {
    font-size: 14px;
  }
}
</style>
