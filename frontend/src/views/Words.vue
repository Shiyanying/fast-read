<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- 生词本卡片 -->
    <div class="bg-white rounded-2xl soft-shadow-lg border border-gray-100">
      <div class="p-6 border-b border-gray-100">
        <div class="flex items-center justify-between flex-wrap gap-4">
          <h2 class="text-2xl font-bold text-gray-900">生词本</h2>
          <div class="flex items-center gap-3">
            <el-select
              v-model="sortBy"
              @change="fetchWords"
              class="select-input"
            >
              <el-option label="点击时间" value="last_clicked_at" />
              <el-option label="点击次数" value="click_count" />
              <el-option label="字母顺序" value="word" />
            </el-select>
            
            <el-select
              v-model="masteryStatus"
              clearable
              @change="fetchWords"
              class="select-input"
            >
              <el-option label="全部状态" value="" />
              <el-option label="生词" value="生词" />
              <el-option label="熟悉" value="熟悉" />
              <el-option label="已掌握" value="已掌握" />
            </el-select>
          </div>
        </div>
      </div>
      
      <div class="p-6">
        <div class="space-y-3" v-if="words.length > 0">
          <div
            v-for="word in words"
            :key="word.id"
            class="flex items-center justify-between p-4 rounded-xl border border-gray-100 hover:border-gray-200 hover:bg-gray-50/50 transition-all cursor-pointer card-lift"
            @click="showWordDetail(word.word)"
          >
            <div class="flex-1">
              <div class="flex items-center gap-3 mb-2">
                <h3 class="text-xl font-semibold text-gray-900">{{ word.word }}</h3>
                <span 
                  class="px-2.5 py-1 text-xs font-semibold rounded-lg"
                  :class="getStatusClass(word.mastery_status)"
                >
                  {{ word.mastery_status }}
                </span>
              </div>
              <div class="flex items-center gap-4 text-sm text-gray-500">
                <span>点击 {{ word.click_count }} 次</span>
                <span>{{ formatDate(word.last_clicked_at) }}</span>
              </div>
            </div>
            <el-select
              :model-value="word.mastery_status"
              @change="updateWordStatus(word.word, $event)"
              @click.stop
              class="status-select"
            >
              <el-option label="生词" value="生词" />
              <el-option label="熟悉" value="熟悉" />
              <el-option label="已掌握" value="已掌握" />
            </el-select>
          </div>
        </div>
        
        <el-empty v-else description="暂无生词，快去阅读文档收集单词吧！">
          <el-button type="primary" @click="router.push('/')">
            返回主页
          </el-button>
        </el-empty>
      </div>
    </div>
    
    <!-- 单词详情对话框 -->
    <el-dialog
      v-model="detailVisible"
      :title="selectedWordDetail?.word"
      width="800px"
      :close-on-click-modal="!isMobile"
      :close-on-press-escape="true"
    >
      <div v-if="selectedWordDetail" class="word-detail-content">
        <div class="detail-header">
          <p v-if="selectedWordDetail.phonetic" class="phonetic">
            {{ selectedWordDetail.phonetic }}
          </p>
          <div class="detail-meta">
            <el-tag>点击 {{ selectedWordDetail.click_count }} 次</el-tag>
            <el-tag :type="getStatusType(selectedWordDetail.mastery_status)">
              {{ selectedWordDetail.mastery_status }}
            </el-tag>
          </div>
        </div>
        
        <div class="contexts-section">
          <h4>出现上下文</h4>
          <div
            v-for="(context, idx) in selectedWordDetail.contexts"
            :key="idx"
            class="context-item"
            @click="goToContext(context)"
          >
            <p class="context-doc">
              《{{ context.document_title }}》 - 第 {{ context.page_number }} 页
            </p>
            <p class="context-text">{{ context.context }}</p>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/api'

const router = useRouter()

const words = ref([])
const sortBy = ref('last_clicked_at')
const masteryStatus = ref('')
const detailVisible = ref(false)
const selectedWordDetail = ref(null)

// 检测移动端
const windowWidth = ref(window.innerWidth)
const isMobile = computed(() => {
  return windowWidth.value <= 768
})

// 监听窗口大小变化
function handleResize() {
  windowWidth.value = window.innerWidth
}

async function fetchWords() {
  try {
    const params = {
      sort_by: sortBy.value,
      order: sortBy.value === 'word' ? 'asc' : 'desc',
      limit: 100
    }
    if (masteryStatus.value) {
      params.mastery_status = masteryStatus.value
    }
    
    const response = await api.get('/words/', { params })
    words.value = response.data.words
  } catch (error) {
    ElMessage.error('获取生词列表失败')
  }
}

async function showWordDetail(word) {
  try {
    const response = await api.get(`/words/${word}`)
    selectedWordDetail.value = response.data
    detailVisible.value = true
  } catch (error) {
    ElMessage.error('获取单词详情失败')
  }
}

async function updateWordStatus(word, status) {
  try {
    await api.patch(`/words/${word}/status?mastery_status=${status}`)
    ElMessage.success('更新成功')
    fetchWords()
  } catch (error) {
    ElMessage.error('更新失败')
  }
}

function goToContext(context) {
  detailVisible.value = false
  router.push(`/reader/${context.document_id}?page=${context.page_number}`)
}

function getStatusType(status) {
  const map = {
    '生词': 'danger',
    '熟悉': 'warning',
    '已掌握': 'success'
  }
  return map[status] || ''
}

function getStatusClass(status) {
  const map = {
    '生词': 'bg-red-50 text-red-700',
    '熟悉': 'bg-yellow-50 text-yellow-700',
    '已掌握': 'bg-green-50 text-green-700'
  }
  return map[status] || ''
}

function formatDate(dateString) {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

onMounted(() => {
  fetchWords()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
:deep(.select-input) {
  width: auto;
  min-width: 150px;
}

:deep(.select-input .el-input__wrapper) {
  padding: 10px 16px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e5e5;
  font-size: 14px;
}

:deep(.select-input .el-input__wrapper:hover) {
  border-color: #d4d4d4;
}

:deep(.select-input .el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px rgba(26, 26, 26, 0.1);
  border-color: #1a1a1a;
}

:deep(.status-select) {
  width: auto;
  min-width: 120px;
}

:deep(.status-select .el-input__wrapper) {
  padding: 8px 12px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e5e5;
  font-size: 14px;
}

:deep(.status-select .el-input__wrapper:hover) {
  border-color: #d4d4d4;
}

:deep(.status-select .el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px rgba(26, 26, 26, 0.1);
  border-color: #1a1a1a;
}

.word-detail-content {
  padding: 24px 0;
}

.detail-header {
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid #f5f5f5;
}

.phonetic {
  font-size: 16px;
  color: #737373;
  margin-bottom: 16px;
  font-style: italic;
}

.detail-meta {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.contexts-section h4 {
  margin-bottom: 20px;
  color: #1a1a1a;
  font-size: 20px;
  font-weight: 600;
  letter-spacing: -0.3px;
}

.context-item {
  padding: 20px;
  background: #fafafa;
  border-radius: 16px;
  margin-bottom: 16px;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid #f5f5f5;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.06);
}

.context-item:hover {
  background-color: white;
  border-color: #e5e5e5;
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06), 0 2px 4px rgba(0, 0, 0, 0.08);
}

.context-doc {
  font-size: 13px;
  color: #4a4a4a;
  margin-bottom: 10px;
  font-weight: 600;
}

.context-text {
  color: #1a1a1a;
  line-height: 1.7;
  font-size: 15px;
}

:deep(.el-dialog) {
  border-radius: 20px;
}

:deep(.el-dialog__header) {
  padding: 24px 24px 0;
  border-bottom: 1px solid #f5f5f5;
  margin-bottom: 24px;
}

:deep(.el-dialog__body) {
  padding: 24px;
}
</style>
