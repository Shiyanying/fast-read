<template>
  <div class="words-container">
    <div class="words-header">
      <div class="header-left">
        <el-button
          type="primary"
          :icon="ArrowLeft"
          circle
          @click="goToDashboard"
          class="back-button"
        />
        <h2>我的生词本</h2>
        <el-tag v-if="words.length > 0" type="info" size="large" class="word-count">
          共 {{ words.length }} 个单词
        </el-tag>
      </div>
      <div class="header-actions">
        <el-select
          v-model="sortBy"
          placeholder="排序方式"
          @change="fetchWords"
          style="width: 150px; margin-right: 12px;"
        >
          <el-option label="点击时间" value="last_clicked_at" />
          <el-option label="点击次数" value="click_count" />
          <el-option label="字母顺序" value="word" />
        </el-select>
        
        <el-select
          v-model="masteryStatus"
          placeholder="掌握状态"
          clearable
          @change="fetchWords"
          style="width: 150px;"
        >
          <el-option label="生词" value="生词" />
          <el-option label="熟悉" value="熟悉" />
          <el-option label="已掌握" value="已掌握" />
        </el-select>
      </div>
    </div>
    
    <div class="words-list">
      <el-card
        v-for="word in words"
        :key="word.id"
        class="word-card"
        shadow="hover"
      >
        <div class="word-header">
          <div class="word-info">
            <div class="word-title-wrapper">
              <h3 class="word-title" @click="showWordDetail(word.word)">
                {{ word.word }}
              </h3>
              <el-icon class="detail-icon" @click="showWordDetail(word.word)">
                <View />
              </el-icon>
            </div>
            <div class="word-meta">
              <el-tag size="small" :type="getStatusType(word.mastery_status)" effect="dark">
                {{ word.mastery_status }}
              </el-tag>
              <span class="click-count">
                <el-icon><Pointer /></el-icon>
                点击 {{ word.click_count }} 次
              </span>
              <span class="click-time">
                <el-icon><Clock /></el-icon>
                {{ formatDate(word.last_clicked_at) }}
              </span>
            </div>
          </div>
          <div class="word-actions">
            <el-select
              :model-value="word.mastery_status"
              @change="updateWordStatus(word.word, $event)"
              size="small"
              style="width: 120px;"
            >
              <el-option label="生词" value="生词" />
              <el-option label="熟悉" value="熟悉" />
              <el-option label="已掌握" value="已掌握" />
            </el-select>
          </div>
        </div>
      </el-card>
      
      <el-empty v-if="words.length === 0" description="暂无生词，快去阅读文档收集单词吧！">
        <el-button type="primary" :icon="ArrowLeft" @click="goToDashboard">
          返回主页
        </el-button>
      </el-empty>
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
import { ArrowLeft, View, Pointer, Clock } from '@element-plus/icons-vue'
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

function formatDate(dateString) {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

function goToDashboard() {
  router.push('/')
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
.words-container {
  max-width: 1400px;
  margin: 0 auto;
}

.words-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  background: var(--apple-card-background);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  padding: 24px 32px;
  border-radius: var(--apple-border-radius-lg);
  border: 0.5px solid rgba(0, 0, 0, 0.08);
  box-shadow: var(--apple-shadow-md);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.back-button {
  border-radius: 50%;
  box-shadow: var(--apple-shadow-sm);
  transition: var(--apple-transition);
}

.back-button:hover {
  transform: translateX(-2px);
  box-shadow: var(--apple-shadow-md);
}

.words-header h2 {
  margin: 0;
  color: var(--apple-text-primary);
  font-size: 28px;
  font-weight: 700;
  letter-spacing: -0.5px;
}

.word-count {
  background: var(--apple-gray-1);
  border: 0.5px solid rgba(0, 0, 0, 0.08);
  color: var(--apple-text-primary);
  font-weight: 500;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.words-list {
  display: grid;
  gap: 20px;
}

.word-card {
  cursor: pointer;
  transition: var(--apple-transition);
  border-radius: var(--apple-border-radius);
  border: 0.5px solid rgba(0, 0, 0, 0.08);
  box-shadow: var(--apple-shadow-sm);
  background: var(--apple-card-background);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
}

.word-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--apple-shadow-lg);
  border-color: rgba(0, 122, 255, 0.2);
}

.word-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.word-info {
  flex: 1;
}

.word-title-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.word-title {
  font-size: 22px;
  font-weight: 600;
  color: var(--apple-text-primary);
  margin: 0;
  cursor: pointer;
  transition: var(--apple-transition);
  letter-spacing: -0.3px;
}

.word-title:hover {
  color: var(--apple-blue);
}

.detail-icon {
  color: var(--apple-gray-4);
  cursor: pointer;
  transition: var(--apple-transition);
  font-size: 18px;
}

.detail-icon:hover {
  color: var(--apple-blue);
  transform: scale(1.1);
}

.word-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  color: var(--apple-text-secondary);
  font-size: 14px;
  flex-wrap: wrap;
}

.click-count,
.click-time {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
}

.word-actions {
  display: flex;
  align-items: center;
}

.word-detail-content {
  padding: 24px 0;
}

.detail-header {
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 0.5px solid rgba(0, 0, 0, 0.08);
}

.phonetic {
  font-size: 16px;
  color: var(--apple-text-secondary);
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
  color: var(--apple-text-primary);
  font-size: 20px;
  font-weight: 600;
  letter-spacing: -0.3px;
}

.context-item {
  padding: 20px;
  background: var(--apple-gray-1);
  border-radius: var(--apple-border-radius);
  margin-bottom: 16px;
  cursor: pointer;
  transition: var(--apple-transition);
  border-left: 4px solid transparent;
  box-shadow: var(--apple-shadow-sm);
}

.context-item:hover {
  background-color: white;
  border-left-color: var(--apple-blue);
  transform: translateX(4px);
  box-shadow: var(--apple-shadow-md);
}

.context-doc {
  font-size: 13px;
  color: var(--apple-blue);
  margin-bottom: 10px;
  font-weight: 600;
}

.context-text {
  color: var(--apple-text-primary);
  line-height: 1.7;
  font-size: 15px;
}

@media (max-width: 768px) {
  .words-container {
    padding: 0;
  }
  
  .words-header {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
    padding: 20px 16px;
    margin-bottom: 24px;
  }
  
  .header-left {
    flex-wrap: wrap;
    gap: 12px;
  }
  
  .words-header h2 {
    font-size: 22px;
  }
  
  .header-actions {
    flex-direction: column;
    width: 100%;
    gap: 12px;
  }
  
  .header-actions .el-select {
    width: 100% !important;
    margin-right: 0 !important;
  }
  
  .words-list {
    gap: 16px;
  }
  
  .word-card {
    padding: 16px;
  }
  
  .word-header {
    flex-direction: column;
    gap: 12px;
  }
  
  .word-title-wrapper {
    margin-bottom: 8px;
  }
  
  .word-title {
    font-size: 20px;
  }
  
  .word-meta {
    flex-wrap: wrap;
    gap: 12px;
    font-size: 13px;
  }
  
  .word-actions {
    width: 100%;
  }
  
  .word-actions .el-select {
    width: 100% !important;
  }
  
  :deep(.el-dialog) {
    width: 95% !important;
    margin: 0 auto;
  }
  
  .word-detail-content {
    padding: 16px 0;
  }
  
  .detail-header {
    margin-bottom: 24px;
    padding-bottom: 16px;
  }
  
  .contexts-section h4 {
    font-size: 18px;
    margin-bottom: 16px;
  }
  
  .context-item {
    padding: 16px;
    margin-bottom: 12px;
  }
  
  .context-doc {
    font-size: 12px;
  }
  
  .context-text {
    font-size: 14px;
  }
}
</style>

