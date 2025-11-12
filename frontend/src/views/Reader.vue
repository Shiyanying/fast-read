<template>
  <div class="reader-container">
    <div class="reader-header">
      <el-button :icon="ArrowLeft" @click="$router.push('/')">返回</el-button>
      <h3 class="document-title">{{ documentTitle }}</h3>
      <div class="page-info">
        第 {{ currentPage }} / {{ totalPages }} 页
      </div>
    </div>
    
    <div class="reader-content">
      <div class="text-area" v-if="currentPageContent">
        <div
          class="text-content"
          v-html="highlightedContent"
          @click="handleWordClick"
        />
      </div>
      
      <el-empty v-else-if="totalPages > 0" description="加载中..." />
      <el-empty v-else description="文档没有内容或加载失败" />
    </div>
    
    <div class="reader-footer">
      <el-button
        :disabled="currentPage <= 1"
        :icon="ArrowLeft"
        @click="goToPreviousPage"
      >
        上一页
      </el-button>
      
      <el-input-number
        v-model="pageInput"
        :min="1"
        :max="Math.max(totalPages, 1)"
        :disabled="totalPages === 0"
        @change="goToPage"
        class="page-input"
      />
      
      <el-button
        :disabled="currentPage >= totalPages"
        @click="goToNextPage"
      >
        下一页
        <el-icon><ArrowRight /></el-icon>
      </el-button>
    </div>
    
    <!-- 单词释义侧边栏 -->
    <el-drawer
      v-model="drawerVisible"
      title="单词释义"
      :size="400"
      direction="rtl"
    >
      <div v-if="selectedWord" class="word-detail">
        <h3 class="word-title">{{ selectedWord.word }}</h3>
        <p v-if="selectedWord.phonetic" class="phonetic">
          {{ selectedWord.phonetic }}
        </p>
        <div class="meanings">
          <div
            v-for="(meaning, idx) in selectedWord.meanings"
            :key="idx"
            class="meaning-item"
          >
            <p class="part-of-speech">{{ meaning.partOfSpeech }}</p>
            <ul class="definitions">
              <li
                v-for="(def, defIdx) in meaning.definitions"
                :key="defIdx"
              >
                <p class="definition">{{ def.definition }}</p>
                <p v-if="def.example" class="example">
                  例: {{ def.example }}
                </p>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import { ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
import api from '@/api'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const documentId = ref(parseInt(route.params.documentId))
const documentTitle = ref('')
const totalPages = ref(0)
const currentPage = ref(1)
const pageInput = ref(1)
const currentPageContent = ref('')
const selectedWord = ref(null)
const drawerVisible = ref(false)
const clickedWords = ref(new Set())

// 将文本转换为可点击的单词元素
const highlightedContent = computed(() => {
  if (!currentPageContent.value) return ''
  
  let content = currentPageContent.value
  
  // 将换行符转换为特殊标记，稍后恢复
  content = content.replace(/\n/g, '\n')
  
  // 将文本按单词边界分割，但保留分隔符
  // 匹配单词：字母序列
  const wordRegex = /\b([a-zA-Z]+)\b/g
  const isHighlighted = (word) => clickedWords.value.has(word.toLowerCase())
  
  content = content.replace(wordRegex, (match, word) => {
    const wordLower = word.toLowerCase()
    const highlighted = isHighlighted(wordLower)
    const className = highlighted ? 'word-clickable word-highlight' : 'word-clickable'
    return `<span class="${className}" data-word="${wordLower}">${word}</span>`
  })
  
  // 将换行符转换为 <br>
  content = content.replace(/\n/g, '<br>')
  
  return content
})

async function fetchDocument() {
  try {
    console.log('Fetching document:', documentId.value)
    const response = await api.get(`/documents/${documentId.value}`)
    console.log('Document response:', response.data)
    documentTitle.value = response.data.title
    totalPages.value = response.data.total_pages || 0
    if (totalPages.value === 0) {
      ElMessage.warning('文档没有页面内容')
    }
  } catch (error) {
    console.error('获取文档信息失败:', error)
    const errorMsg = error.response?.data?.detail || error.message || '获取文档信息失败'
    ElMessage.error(errorMsg)
    // 如果文档不存在，返回上一页
    if (error.response?.status === 404) {
      setTimeout(() => {
        router.push('/')
      }, 2000)
    }
  }
}

async function fetchPage(pageNumber) {
  try {
    console.log('Fetching page:', pageNumber, 'of document:', documentId.value)
    const response = await api.get(
      `/documents/${documentId.value}/pages/${pageNumber}`
    )
    console.log('Page response:', response.data)
    currentPageContent.value = response.data.content || ''
    currentPage.value = pageNumber
    pageInput.value = pageNumber
    
    if (!currentPageContent.value) {
      ElMessage.warning('该页面没有内容')
    }
  } catch (error) {
    console.error('获取页面内容失败:', error)
    const errorMsg = error.response?.data?.detail || error.message || '获取页面内容失败'
    ElMessage.error(errorMsg)
    currentPageContent.value = ''
  }
}

async function handleWordClick(event) {
  // 获取点击的元素
  let target = event.target
  
  // 如果点击的是 mark 标签内的内容，向上查找包含 data-word 的元素
  while (target && !target.dataset?.word) {
    if (target.classList?.contains('word-clickable')) {
      break
    }
    target = target.parentElement
    // 防止无限循环
    if (target === event.currentTarget) {
      return
    }
  }
  
  // 获取单词
  const word = target?.dataset?.word
  if (!word) {
    // 如果没有找到，尝试从文本中提取
    const selection = window.getSelection()
    if (selection.rangeCount > 0) {
      const selectedText = selection.toString().trim()
      const wordMatch = selectedText.match(/\b[a-zA-Z]+\b/)
      if (wordMatch) {
        const extractedWord = wordMatch[0].toLowerCase()
        await lookupWord(extractedWord)
        return
      }
    }
    return
  }
  
  await lookupWord(word)
}

async function lookupWord(word) {
  if (!word) return
  
  console.log('Looking up word:', word)
  
  // 查询单词释义
  try {
    const response = await api.get('/words/lookup', {
      params: {
        word: word,
        document_id: documentId.value
      }
    })
    
    selectedWord.value = response.data
    drawerVisible.value = true
    
    // 记录已点击的单词
    clickedWords.value.add(word)
  } catch (error) {
    console.error('查询单词失败:', error)
    const errorMsg = error.response?.data?.detail || error.message || '查询单词失败'
    ElMessage.error(errorMsg)
  }
}

function goToPreviousPage() {
  if (currentPage.value > 1) {
    fetchPage(currentPage.value - 1)
  }
}

function goToNextPage() {
  if (currentPage.value < totalPages.value) {
    fetchPage(currentPage.value + 1)
  }
}

function goToPage(page) {
  if (page >= 1 && page <= totalPages.value) {
    fetchPage(page)
  }
}

watch(() => route.params.documentId, (newId) => {
  documentId.value = parseInt(newId)
  fetchDocument()
  const page = parseInt(route.query.page) || 1
  fetchPage(page)
})

onMounted(() => {
  fetchDocument()
  const page = parseInt(route.query.page) || 1
  fetchPage(page)
})
</script>

<style scoped>
.reader-container {
  max-width: 900px;
  margin: 0 auto;
  background: white;
  border-radius: 8px;
  padding: 24px;
  min-height: calc(100vh - 100px);
  display: flex;
  flex-direction: column;
}

.reader-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.document-title {
  flex: 1;
  margin: 0 16px;
  text-align: center;
  color: #333;
}

.page-info {
  color: #666;
  font-size: 14px;
}

.reader-content {
  flex: 1;
  margin-bottom: 24px;
}

.text-area {
  min-height: 500px;
  padding: 32px;
  background: #fafafa;
  border-radius: 8px;
  line-height: 2;
  font-size: 16px;
}

.text-content {
  color: #333;
  white-space: pre-wrap;
  word-wrap: break-word;
  user-select: text;
}

.word-clickable {
  cursor: pointer;
  transition: background-color 0.2s;
  padding: 2px 2px;
  border-radius: 3px;
  display: inline-block;
}

.word-clickable:hover {
  background-color: #e3f2fd;
}

.word-highlight {
  background-color: #fff3cd;
  padding: 2px 4px;
  border-radius: 3px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.word-highlight:hover {
  background-color: #ffc107;
}

.reader-footer {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  padding-top: 16px;
  border-top: 1px solid #e4e7ed;
}

.page-input {
  width: 100px;
}

.word-detail {
  padding: 16px;
}

.word-title {
  font-size: 24px;
  color: #333;
  margin-bottom: 8px;
}

.phonetic {
  color: #666;
  font-size: 14px;
  margin-bottom: 16px;
}

.meanings {
  margin-top: 16px;
}

.meaning-item {
  margin-bottom: 24px;
}

.part-of-speech {
  font-weight: 600;
  color: #667eea;
  margin-bottom: 8px;
  font-size: 16px;
}

.definitions {
  list-style: none;
  padding: 0;
}

.definitions li {
  margin-bottom: 12px;
  padding-left: 16px;
}

.definition {
  color: #333;
  margin-bottom: 4px;
}

.example {
  color: #999;
  font-style: italic;
  font-size: 14px;
  margin-top: 4px;
}
</style>

