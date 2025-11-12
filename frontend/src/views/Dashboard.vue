<template>
  <div class="dashboard">
    <div class="upload-section">
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
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持 .txt, .pdf, .epub 格式，文件大小不超过 10MB
          </div>
        </template>
      </el-upload>
    </div>
    
    <div class="library-section">
      <h3 class="section-title">我的外刊库</h3>
      
      <el-input
        v-model="searchKeyword"
        placeholder="搜索文档..."
        class="search-input"
        clearable
        @input="handleSearch"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      
      <el-row :gutter="20" class="document-grid">
        <el-col
          v-for="doc in filteredDocuments"
          :key="doc.id"
          :xs="24"
          :sm="12"
          :md="8"
          :lg="6"
        >
          <el-card
            class="document-card"
            shadow="hover"
            @click="openDocument(doc.id)"
          >
            <template #header>
              <div class="card-header">
                <span class="doc-title">{{ doc.title }}</span>
                <el-button
                  type="danger"
                  :icon="Delete"
                  circle
                  size="small"
                  @click.stop="handleDelete(doc.id)"
                />
              </div>
            </template>
            <div class="card-content">
              <p class="doc-meta">
                <el-icon><Document /></el-icon>
                {{ doc.filename }}
              </p>
              <p class="doc-meta">
                <el-icon><Calendar /></el-icon>
                {{ formatDate(doc.created_at) }}
              </p>
              <p class="doc-meta">
                <el-icon><Files /></el-icon>
                {{ doc.total_pages }} 页
              </p>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <el-empty v-if="filteredDocuments.length === 0" description="暂无文档" />
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
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
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
  max-width: 1200px;
  margin: 0 auto;
}

.upload-section {
  margin-bottom: 32px;
}

.upload-area {
  width: 100%;
}

.el-upload__tip {
  color: #999;
  font-size: 12px;
  margin-top: 8px;
}

.library-section {
  background: white;
  padding: 24px;
  border-radius: 8px;
}

.section-title {
  margin-bottom: 20px;
  color: #333;
  font-size: 20px;
}

.search-input {
  margin-bottom: 20px;
  max-width: 400px;
}

.document-grid {
  margin-top: 20px;
}

.document-card {
  margin-bottom: 20px;
  cursor: pointer;
  transition: transform 0.3s;
}

.document-card:hover {
  transform: translateY(-4px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.doc-title {
  font-weight: 500;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}

.card-content {
  padding-top: 12px;
}

.doc-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #666;
  font-size: 14px;
  margin-bottom: 8px;
}
</style>

