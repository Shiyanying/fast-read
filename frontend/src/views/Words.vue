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
import { ref, onMounted } from 'vue'
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
})
</script>

<style scoped>
.words-container {
  max-width: 1200px;
  margin: 0 auto;
}

.words-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 24px 28px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.back-button {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  transition: all 0.3s;
}

.back-button:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateX(-2px);
}

.words-header h2 {
  margin: 0;
  color: white;
  font-size: 24px;
  font-weight: 600;
}

.word-count {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.words-list {
  display: grid;
  gap: 16px;
}

.word-card {
  cursor: pointer;
  transition: all 0.3s;
  border-radius: 12px;
  border: 1px solid #e4e7ed;
}

.word-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.15);
  border-color: #667eea;
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
  color: #333;
  margin: 0;
  cursor: pointer;
  transition: color 0.2s;
}

.word-title:hover {
  color: #667eea;
}

.detail-icon {
  color: #909399;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 18px;
}

.detail-icon:hover {
  color: #667eea;
  transform: scale(1.1);
}

.word-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  color: #666;
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
  padding: 16px 0;
}

.detail-header {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.phonetic {
  font-size: 16px;
  color: #666;
  margin-bottom: 12px;
}

.detail-meta {
  display: flex;
  gap: 8px;
}

.contexts-section h4 {
  margin-bottom: 16px;
  color: #333;
}

.context-item {
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.2s;
  border-left: 3px solid transparent;
}

.context-item:hover {
  background-color: #e4e7ed;
  border-left-color: #667eea;
  transform: translateX(4px);
}

.context-doc {
  font-size: 12px;
  color: #667eea;
  margin-bottom: 8px;
  font-weight: 500;
}

.context-text {
  color: #333;
  line-height: 1.6;
}
</style>

