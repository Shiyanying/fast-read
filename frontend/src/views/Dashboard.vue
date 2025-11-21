<template>
  <div class="desk-scene">
    <!-- 墙面背景 -->
    <div class="wall-background"></div>
    
    <!-- 书桌 -->
    <div class="desk-surface">
      <!-- 顶部操作栏 -->
      <div class="desk-header">
        <div class="scene-title">
          <svg class="title-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
          </svg>
          <h1>我的书桌</h1>
        </div>
        
        <div class="desk-actions">
          <button class="desk-button vocabulary-button" @click="$router.push('/words')">
            <svg class="button-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
            </svg>
            <span>生词本</span>
          </button>
        </div>
      </div>
      
      <!-- 上传区域 -->
      <div class="upload-zone" v-if="documents.length === 0">
        <el-upload
          ref="uploadRef"
          :action="uploadUrl"
          :headers="uploadHeaders"
          :on-success="handleUploadSuccess"
          :on-error="handleUploadError"
          :before-upload="beforeUpload"
          :show-file-list="false"
          drag
          class="upload-dragger"
        >
          <div class="upload-content">
            <div class="upload-icon-wrapper">
              <svg class="upload-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
              </svg>
            </div>
            <h3 class="upload-title">上传您的第一本外刊</h3>
            <p class="upload-desc">拖拽或点击上传 TXT 文件</p>
            <p class="upload-hint">文件大小不超过 10MB</p>
          </div>
        </el-upload>
      </div>
      
      <!-- 书本展示区 -->
      <div class="books-shelf" v-else>
        <div class="shelf-header">
          <h2 class="shelf-title">
            <svg class="shelf-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
            </svg>
            我的藏书 ({{ documents.length }})
          </h2>
          
          <el-upload
            ref="uploadRef"
            :action="uploadUrl"
            :headers="uploadHeaders"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            :before-upload="beforeUpload"
            :show-file-list="false"
            class="add-book-upload"
          >
            <button class="desk-button add-book-button">
              <svg class="button-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
              </svg>
              <span>添加新书</span>
            </button>
          </el-upload>
        </div>
        
        <div class="books-grid">
          <div v-for="doc in documents" :key="doc.id" class="book-item">
            <BookCard
              :title="doc.title"
              :pages="doc.total_pages"
              :progress="doc.progress"
              @open="openDocument(doc.id)"
            />
            <button class="delete-book-button" @click.stop="handleDelete(doc.id)" title="删除">
              <svg class="delete-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage, ElMessageBox } from 'element-plus'
import BookCard from '@/components/BookCard.vue'
import api from '@/api'

const router = useRouter()
const authStore = useAuthStore()
const uploadRef = ref(null)
const documents = ref([])

const uploadUrl = '/api/v1/documents/upload'
const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${authStore.token}`
}))

async function fetchDocuments() {
  try {
    const response = await api.get('/documents/')
    documents.value = response.data.documents
  } catch (error) {
    ElMessage.error('获取文档列表失败')
  }
}

function beforeUpload(file) {
  const isValidType = file.type === 'text/plain' || file.name.endsWith('.txt')
  
  if (!isValidType) {
    ElMessage.error('仅支持 .txt 格式的文件')
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
    await ElMessageBox.confirm('确定要删除这本书吗？', '确认删除', {
      confirmButtonText: '删除',
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
  }
}

onMounted(() => {
  fetchDocuments()
})
</script>

<style scoped>
.desk-scene {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  position: relative;
  background: linear-gradient(180deg, #E8D5C4 0%, #D4C4B0 100%);
}

.wall-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 25vh;
  background: linear-gradient(180deg, #F5E6D3 0%, #E8D5C4 100%);
  box-shadow: inset 0 -10px 30px rgba(0, 0, 0, 0.05);
}

.desk-surface {
  position: relative;
  flex: 1;
  margin-top: 20vh;
  padding: 40px 60px;
  background: linear-gradient(180deg, #8B7355 0%, #6B5344 100%);
  border-radius: 40px 40px 0 0;
  box-shadow: 
    0 -10px 40px rgba(0, 0, 0, 0.3),
    inset 0 2px 10px rgba(255, 255, 255, 0.1);
}

.desk-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
  gap: 20px;
}

.scene-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.title-icon {
  width: 32px;
  height: 32px;
  color: #D4AF37;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
}

.scene-title h1 {
  margin: 0;
  font-size: 32px;
  font-weight: 700;
  color: #FDF5E6;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
  letter-spacing: -0.5px;
}

.desk-actions {
  display: flex;
  gap: 16px;
}

.desk-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: linear-gradient(135deg, #D4AF37 0%, #C19A2E 100%);
  border: none;
  border-radius: 16px;
  color: #2C1810;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 
    0 4px 12px rgba(212, 175, 55, 0.3),
    inset 0 1px 2px rgba(255, 255, 255, 0.3);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.desk-button:hover {
  transform: translateY(-2px);
  box-shadow: 
    0 6px 16px rgba(212, 175, 55, 0.4),
    inset 0 1px 2px rgba(255, 255, 255, 0.4);
}

.button-icon {
  width: 20px;
  height: 20px;
}

/* 上传区域 */
.upload-zone {
  max-width: 600px;
  margin: 80px auto;
}

:deep(.upload-dragger) {
  border: none;
  background: transparent;
}

:deep(.el-upload-dragger) {
  background: rgba(253, 245, 230, 0.9);
  border: 3px dashed #D4AF37;
  border-radius: 24px;
  padding: 60px 40px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  backdrop-filter: blur(10px);
}

:deep(.el-upload-dragger:hover) {
  background: rgba(253, 245, 230, 1);
  border-color: #C19A2E;
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(212, 175, 55, 0.3);
}

.upload-content {
  text-align: center;
}

.upload-icon-wrapper {
  width: 80px;
  height: 80px;
  margin: 0 auto 24px;
  background: linear-gradient(135deg, #D4AF37 0%, #C19A2E 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 16px rgba(212, 175, 55, 0.4);
}

.upload-icon {
  width: 40px;
  height: 40px;
  color: #2C1810;
}

.upload-title {
  font-size: 24px;
  font-weight: 700;
  color: #2C1810;
  margin: 0 0 12px 0;
}

.upload-desc {
  font-size: 16px;
  color: #5D4E3C;
  margin: 0 0 8px 0;
}

.upload-hint {
  font-size: 14px;
  color: #8B7355;
  margin: 0;
}

/* 书架 */
.books-shelf {
  min-height: 400px;
}

.shelf-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  padding-bottom: 20px;
  border-bottom: 2px solid rgba(212, 175, 55, 0.3);
}

.shelf-title {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #FDF5E6;
  text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.5);
}

.shelf-icon {
  width: 28px;
  height: 28px;
  color: #D4AF37;
}

.books-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 40px 32px;
  padding: 20px 0;
}

.book-item {
  position: relative;
  display: flex;
  justify-content: center;
}

.delete-book-button {
  position: absolute;
  top: -8px;
  right: 8px;
  width: 32px;
  height: 32px;
  background: rgba(192, 64, 0, 0.9);
  border: none;
  border-radius: 50%;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  z-index: 10;
}

.book-item:hover .delete-book-button {
  opacity: 1;
}

.delete-book-button:hover {
  background: rgba(192, 64, 0, 1);
  transform: scale(1.1);
}

.delete-icon {
  width: 18px;
  height: 18px;
}

/* 响应式 */
@media (max-width: 1024px) {
  .desk-surface {
    padding: 32px 40px;
  }
  
  .books-grid {
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 32px 24px;
  }
}

@media (max-width: 768px) {
  .desk-surface {
    padding: 24px 20px;
    border-radius: 24px 24px 0 0;
  }
  
  .desk-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .scene-title h1 {
    font-size: 24px;
  }
  
  .desk-actions {
    width: 100%;
    justify-content: stretch;
  }
  
  .desk-button {
    flex: 1;
    justify-content: center;
  }
  
  .books-grid {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 24px 16px;
  }
  
  .upload-zone {
    margin: 40px auto;
  }
  
  :deep(.el-upload-dragger) {
    padding: 40px 24px;
  }
}
</style>
