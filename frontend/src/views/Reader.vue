<template>
  <div class="reader-container">
    <div class="reader-header">
      <el-button 
        :icon="ArrowLeft" 
        @click="$router.push('/')"
        class="back-button"
        circle
      />
      <h2 class="document-title">{{ documentTitle }}</h2>
      <div class="page-info">
        第 {{ currentPage }} / {{ totalPages }} 页
      </div>
    </div>
    
    <div class="reader-content">
      <div class="text-area" v-if="currentPageContent">
        <div
          class="text-content"
          v-html="highlightedContent"
          @click.stop="handleWordClick"
          @mouseover="handleWordHover"
          @mouseout="handleWordOut"
        />
      </div>
      
      <el-empty v-else-if="totalPages > 0" description="加载中..." />
      <el-empty v-else description="文档没有内容或加载失败" />
    </div>
    
    <!-- 简要释义预览弹窗 -->
    <transition name="word-preview">
      <div
        v-if="selectedWord && previewVisible && !detailVisible"
        class="word-preview"
        :style="previewStyle"
        @click.stop="showDetail"
      >
        <div class="preview-content">
          <div class="preview-header">
            <span class="preview-word">{{ selectedWord.word }}</span>
            <span class="preview-hint">点击查看详情</span>
          </div>
          <span class="preview-meaning">{{ previewText }}</span>
        </div>
        <div class="preview-arrow" :class="previewPosition === 'top' ? 'arrow-down' : 'arrow-up'"></div>
      </div>
    </transition>
    
    <!-- 详细释义弹窗 -->
    <transition name="word-detail-popover">
      <div
        v-if="selectedWord && detailVisible"
        class="word-detail-popover"
        :style="detailStyle"
        @click.stop
      >
        <div class="popover-header">
          <h3 class="word-title">{{ selectedWord.word }}</h3>
          <el-button
            text
            circle
            size="small"
            class="close-btn"
            @click="closePopover"
          >
            <el-icon><Close /></el-icon>
          </el-button>
        </div>
        <div class="popover-content">
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
      </div>
    </transition>
    
    <!-- 遮罩层（移动端详细弹窗） -->
    <div
      v-if="detailVisible && isMobile"
      class="popover-overlay"
      @click="closePopover"
    ></div>
    
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
    
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import { ArrowLeft, ArrowRight, Close } from '@element-plus/icons-vue'
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
const previewVisible = ref(false)
const detailVisible = ref(false)
const clickedWords = ref(new Set())
const isLoadingWord = ref(false)
const hoveredWord = ref(null)
const previewStyle = ref({})
const detailStyle = ref({})
const clickedElement = ref(null)
const previewPosition = ref('top') // 'top' 或 'bottom'，用于控制箭头方向

// 本地缓存单词释义（避免重复请求）
const wordCache = ref(new Map())
const pendingRequests = ref(new Map()) // 防止重复请求

// 检测移动端
const isMobile = computed(() => {
  return window.innerWidth <= 768
})

// 提取简要释义（第一个definition）
const previewText = computed(() => {
  if (!selectedWord.value || !selectedWord.value.meanings || selectedWord.value.meanings.length === 0) {
    return '暂无释义'
  }
  
  // 获取第一个meaning的第一个definition
  const firstMeaning = selectedWord.value.meanings[0]
  if (firstMeaning.definitions && firstMeaning.definitions.length > 0) {
    const firstDef = firstMeaning.definitions[0].definition
    // 限制长度，超过50字符截断
    if (firstDef.length > 50) {
      return firstDef.substring(0, 50) + '...'
    }
    return firstDef
  }
  
  return '暂无释义'
})

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
  const isHovered = (word) => hoveredWord.value === word.toLowerCase()
  
  content = content.replace(wordRegex, (match, word) => {
    const wordLower = word.toLowerCase()
    const highlighted = isHighlighted(wordLower)
    const hovered = isHovered(wordLower)
    let className = 'word-clickable'
    if (highlighted) className += ' word-highlight'
    if (hovered) className += ' word-hovered'
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

function handleWordHover(event) {
  let target = event.target
  
  // 向上查找包含 data-word 的元素
  while (target && !target.dataset?.word) {
    if (target.classList?.contains('word-clickable')) {
      break
    }
    target = target.parentElement
    if (target === event.currentTarget) {
      return
    }
  }
  
  const word = target?.dataset?.word
  if (word) {
    hoveredWord.value = word.toLowerCase()
  }
}

function handleWordOut(event) {
  hoveredWord.value = null
}

async function handleWordClick(event) {
  // 阻止事件冒泡，避免触发 handleClickOutside
  event.stopPropagation()
  
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
        await lookupWord(extractedWord, event)
        return
      }
    }
    return
  }
  
  clickedElement.value = target
  await lookupWord(word, event)
}

function calculatePreviewPosition(element) {
  if (!element) return {}
  
  const rect = element.getBoundingClientRect()
  const viewportWidth = window.innerWidth
  const viewportHeight = window.innerHeight
  
  // 预览弹窗尺寸
  const previewWidth = 280
  const previewHeight = 60 // 估算高度
  
  // 计算位置：在单词上方居中
  let left = rect.left + rect.width / 2 - previewWidth / 2
  let top = rect.top - previewHeight - 12 // 在单词上方12px
  
  // 水平边界检测和调整
  if (left < 16) left = 16
  if (left + previewWidth > viewportWidth - 16) {
    left = viewportWidth - previewWidth - 16
  }
  
  // 判断预览位置
  let position = 'top'
  
  // 如果上方空间不足，显示在下方
  if (top < 16) {
    top = rect.bottom + 12
    position = 'bottom'
    // 如果下方也不够，显示在单词旁边
    if (top + previewHeight > viewportHeight - 16) {
      // 优先显示在右侧
      left = rect.right + 12
      top = rect.top
      position = 'right'
      // 如果右侧不够，显示在左侧
      if (left + previewWidth > viewportWidth - 16) {
        left = rect.left - previewWidth - 12
        position = 'left'
      }
    }
  }
  
  // 更新位置状态
  previewPosition.value = position
  
  return {
    left: `${left}px`,
    top: `${top}px`
  }
}

function calculateDetailPosition(element) {
  if (!element) return {}
  
  const rect = element.getBoundingClientRect()
  const viewportWidth = window.innerWidth
  const viewportHeight = window.innerHeight
  
  // 弹窗尺寸
  const popoverWidth = isMobile.value ? Math.min(viewportWidth - 32, 360) : 360
  const popoverHeight = 400 // 估算高度
  
  // 移动端特殊处理：居中显示
  if (isMobile.value) {
    return {
      left: '50%',
      top: '50%',
      transform: 'translate(-50%, -50%)',
      maxWidth: `${popoverWidth}px`,
      width: `${popoverWidth}px`
    }
  }
  
  // 桌面端：根据单词位置动态定位，优先显示在右侧
  let left = rect.right + 16 // 在单词右侧16px
  let top = rect.top
  
  // 如果右侧空间不足，显示在左侧
  if (left + popoverWidth > viewportWidth - 16) {
    left = rect.left - popoverWidth - 16
  }
  
  // 如果左侧也不够，居中显示
  if (left < 16) {
    left = (viewportWidth - popoverWidth) / 2
    top = rect.top - popoverHeight / 2 + rect.height / 2
  }
  
  // 垂直边界检测
  if (top < 16) top = 16
  if (top + popoverHeight > viewportHeight - 16) {
    top = viewportHeight - popoverHeight - 16
  }
  
  return {
    left: `${left}px`,
    top: `${top}px`,
    maxWidth: `${popoverWidth}px`
  }
}

function showDetail() {
  detailVisible.value = true
  if (clickedElement.value) {
    detailStyle.value = calculateDetailPosition(clickedElement.value)
  }
}

function closePopover() {
  previewVisible.value = false
  detailVisible.value = false
  selectedWord.value = null
  hoveredWord.value = null
  clickedElement.value = null
}

async function lookupWord(word, event) {
  if (!word) return
  
  const wordLower = word.toLowerCase()
  
  // 检查本地缓存
  if (wordCache.value.has(wordLower)) {
    selectedWord.value = wordCache.value.get(wordLower)
    clickedWords.value.add(wordLower)
    // 计算预览弹窗位置
    if (clickedElement.value) {
      previewStyle.value = calculatePreviewPosition(clickedElement.value)
    }
    previewVisible.value = true
    detailVisible.value = false
    return
  }
  
  // 防止重复请求
  if (pendingRequests.value.has(wordLower)) {
    return
  }
  
  isLoadingWord.value = true
  pendingRequests.value.set(wordLower, true)
  
  try {
    const response = await api.get('/words/lookup', {
      params: {
        word: wordLower,
        document_id: documentId.value
      }
    })
    
    // 缓存结果
    wordCache.value.set(wordLower, response.data)
    selectedWord.value = response.data
    
    // 计算预览弹窗位置
    if (clickedElement.value) {
      previewStyle.value = calculatePreviewPosition(clickedElement.value)
    }
    previewVisible.value = true
    detailVisible.value = false
    
    // 记录已点击的单词
    clickedWords.value.add(wordLower)
  } catch (error) {
    console.error('查询单词失败:', error)
    const errorMsg = error.response?.data?.detail || error.message || '查询单词失败'
    ElMessage.error(errorMsg)
  } finally {
    isLoadingWord.value = false
    pendingRequests.value.delete(wordLower)
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

// 点击外部关闭弹窗
function handleClickOutside(event) {
  if (previewVisible.value || detailVisible.value) {
    // 如果点击的不是弹窗本身，也不是单词元素，则关闭
    const isPreview = event.target.closest('.word-preview')
    const isDetail = event.target.closest('.word-detail-popover')
    const isWord = event.target.closest('.word-clickable')
    if (!isPreview && !isDetail && !isWord) {
      // 如果详细弹窗已打开，只关闭预览
      if (detailVisible.value) {
        previewVisible.value = false
      } else {
        closePopover()
      }
    }
  }
}

// 滚动时更新预览位置或关闭预览（但保留详细弹窗）
function handleScroll() {
  if (previewVisible.value && clickedElement.value) {
    // 更新预览位置
    previewStyle.value = calculatePreviewPosition(clickedElement.value)
  }
  // 详细弹窗在滚动时不关闭，保持打开状态
}

onMounted(() => {
  fetchDocument()
  const page = parseInt(route.query.page) || 1
  fetchPage(page)
  
  // 添加全局事件监听
  document.addEventListener('click', handleClickOutside)
  window.addEventListener('scroll', handleScroll, true)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  window.removeEventListener('scroll', handleScroll, true)
})
</script>

<style scoped>
.reader-container {
  max-width: 1000px;
  margin: 0 auto;
  background: var(--apple-card-background);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  border-radius: var(--apple-border-radius-lg);
  border: 0.5px solid rgba(0, 0, 0, 0.08);
  box-shadow: var(--apple-shadow-md);
  padding: 32px;
  min-height: calc(100vh - 160px);
  display: flex;
  flex-direction: column;
}

.reader-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  padding-bottom: 20px;
  border-bottom: 0.5px solid rgba(0, 0, 0, 0.08);
  gap: 16px;
}

.back-button {
  flex-shrink: 0;
  border-radius: 50%;
  box-shadow: var(--apple-shadow-sm);
  transition: var(--apple-transition);
}

.back-button:hover {
  transform: translateX(-2px);
  box-shadow: var(--apple-shadow-md);
}

.document-title {
  flex: 1;
  margin: 0;
  text-align: center;
  font-size: 22px;
  font-weight: 600;
  color: var(--apple-text-primary);
  letter-spacing: -0.5px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.page-info {
  flex-shrink: 0;
  color: var(--apple-text-secondary);
  font-size: 14px;
  font-weight: 500;
  padding: 6px 14px;
  background: var(--apple-gray-1);
  border-radius: 20px;
}

.reader-content {
  flex: 1;
  margin-bottom: 32px;
}

.text-area {
  min-height: 600px;
  padding: 48px 56px;
  background: white;
  border-radius: var(--apple-border-radius);
  border: 0.5px solid rgba(0, 0, 0, 0.08);
  box-shadow: var(--apple-shadow-sm);
  line-height: 2;
  font-size: 18px;
  transition: var(--apple-transition);
}

.text-area:hover {
  box-shadow: var(--apple-shadow-md);
}

.text-content {
  color: var(--apple-text-primary);
  white-space: pre-wrap;
  word-wrap: break-word;
  user-select: text;
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Segoe UI', Roboto, sans-serif;
}

.word-clickable {
  cursor: pointer;
  transition: var(--apple-transition);
  padding: 2px 4px;
  border-radius: 6px;
  display: inline-block;
  margin: 0 1px;
  position: relative;
}

.word-clickable:hover,
.word-hovered {
  background-color: rgba(0, 122, 255, 0.15);
  box-shadow: 0 0 0 2px rgba(0, 122, 255, 0.3);
  transform: scale(1.02);
}

.word-highlight {
  background: linear-gradient(135deg, rgba(255, 204, 0, 0.2) 0%, rgba(255, 149, 0, 0.2) 100%);
  padding: 2px 6px;
  border-radius: 6px;
  cursor: pointer;
  transition: var(--apple-transition);
  font-weight: 500;
}

.word-highlight:hover,
.word-highlight.word-hovered {
  background: linear-gradient(135deg, rgba(255, 204, 0, 0.3) 0%, rgba(255, 149, 0, 0.3) 100%);
  box-shadow: 0 0 0 2px rgba(255, 149, 0, 0.4);
  transform: scale(1.02);
}

.reader-footer {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  padding-top: 24px;
  border-top: 0.5px solid rgba(0, 0, 0, 0.08);
}

:deep(.el-button) {
  border-radius: 12px;
  font-weight: 500;
  transition: var(--apple-transition);
}

:deep(.el-button:hover:not(:disabled)) {
  transform: translateY(-2px);
  box-shadow: var(--apple-shadow-md);
}

.page-input {
  width: 100px;
}

:deep(.el-input-number) {
  border-radius: 12px;
}

:deep(.el-input-number .el-input__wrapper) {
  border-radius: 12px;
  box-shadow: var(--apple-shadow-sm);
}

.word-detail {
  padding: 24px 0;
}

.word-title {
  font-size: 32px;
  font-weight: 700;
  color: var(--apple-text-primary);
  margin-bottom: 12px;
  letter-spacing: -0.5px;
}

.phonetic {
  color: var(--apple-text-secondary);
  font-size: 16px;
  margin-bottom: 24px;
  font-style: italic;
}

.meanings {
  margin-top: 24px;
}

.meaning-item {
  margin-bottom: 32px;
  padding: 20px;
  background: var(--apple-gray-1);
  border-radius: var(--apple-border-radius);
  border-left: 4px solid var(--apple-blue);
}

.part-of-speech {
  font-weight: 600;
  color: var(--apple-blue);
  margin-bottom: 12px;
  font-size: 16px;
  text-transform: capitalize;
}

.definitions {
  list-style: none;
  padding: 0;
  margin: 0;
}

.definitions li {
  margin-bottom: 16px;
  padding-left: 0;
}

.definition {
  color: var(--apple-text-primary);
  margin-bottom: 8px;
  font-size: 15px;
  line-height: 1.6;
}

.example {
  color: var(--apple-text-secondary);
  font-style: italic;
  font-size: 14px;
  margin-top: 8px;
  padding-left: 16px;
  border-left: 2px solid var(--apple-gray-3);
}

/* 简要预览弹窗样式 */
.word-preview {
  position: fixed;
  z-index: 1000;
  background: var(--apple-card-background);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  border-radius: 12px;
  border: 0.5px solid rgba(0, 0, 0, 0.08);
  box-shadow: var(--apple-shadow-lg);
  padding: 14px 16px;
  max-width: 300px;
  min-width: 200px;
  cursor: pointer;
  transition: var(--apple-transition);
  pointer-events: auto;
}

.word-preview:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  border-color: rgba(0, 122, 255, 0.2);
}

.word-preview-enter-active,
.word-preview-leave-active {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.word-preview-enter-from {
  opacity: 0;
  transform: translateY(8px) scale(0.95);
}

.word-preview-leave-to {
  opacity: 0;
  transform: translateY(8px) scale(0.95);
}

.preview-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.preview-word {
  font-weight: 600;
  font-size: 15px;
  color: var(--apple-text-primary);
  flex-shrink: 0;
}

.preview-hint {
  font-size: 11px;
  color: var(--apple-blue);
  opacity: 0.7;
  white-space: nowrap;
}

.preview-meaning {
  font-size: 14px;
  color: var(--apple-text-secondary);
  line-height: 1.5;
  word-break: break-word;
}

.preview-arrow {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
}

.preview-arrow.arrow-down {
  bottom: -6px;
  border-left: 6px solid transparent;
  border-right: 6px solid transparent;
  border-top: 6px solid var(--apple-card-background);
}

.preview-arrow.arrow-up {
  top: -6px;
  border-left: 6px solid transparent;
  border-right: 6px solid transparent;
  border-bottom: 6px solid var(--apple-card-background);
}

/* 详细弹窗样式 */
.word-detail-popover {
  position: fixed;
  z-index: 1001;
  background: var(--apple-card-background);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  border-radius: var(--apple-border-radius-lg);
  border: 0.5px solid rgba(0, 0, 0, 0.08);
  box-shadow: var(--apple-shadow-lg);
  max-width: 360px;
  max-height: 500px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  width: 360px;
}

.word-detail-popover-enter-active,
.word-detail-popover-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.word-detail-popover-enter-from {
  opacity: 0;
  transform: scale(0.9) translateY(-10px);
}

.word-detail-popover-leave-to {
  opacity: 0;
  transform: scale(0.9) translateY(-10px);
}

.popover-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 0.5px solid rgba(0, 0, 0, 0.08);
  flex-shrink: 0;
}

.popover-header .word-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--apple-text-primary);
  margin: 0;
  letter-spacing: -0.3px;
}

.close-btn {
  color: var(--apple-gray-4);
  transition: var(--apple-transition);
}

.close-btn:hover {
  color: var(--apple-text-primary);
  background-color: var(--apple-gray-1);
}

.popover-content {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
  max-height: calc(500px - 60px);
}

.popover-content .phonetic {
  color: var(--apple-text-secondary);
  font-size: 15px;
  margin-bottom: 16px;
  font-style: italic;
}

.popover-content .meanings {
  margin-top: 16px;
}

.popover-content .meaning-item {
  margin-bottom: 20px;
  padding: 16px;
  background: var(--apple-gray-1);
  border-radius: var(--apple-border-radius);
  border-left: 4px solid var(--apple-blue);
}

.popover-content .part-of-speech {
  font-weight: 600;
  color: var(--apple-blue);
  margin-bottom: 10px;
  font-size: 15px;
  text-transform: capitalize;
}

.popover-content .definitions {
  list-style: none;
  padding: 0;
  margin: 0;
}

.popover-content .definitions li {
  margin-bottom: 12px;
}

.popover-content .definition {
  color: var(--apple-text-primary);
  margin-bottom: 6px;
  font-size: 14px;
  line-height: 1.5;
}

.popover-content .example {
  color: var(--apple-text-secondary);
  font-style: italic;
  font-size: 13px;
  margin-top: 6px;
  padding-left: 12px;
  border-left: 2px solid var(--apple-gray-3);
}

/* 移动端遮罩层 */
.popover-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(2px);
  z-index: 999;
}

@media (max-width: 768px) {
  .reader-container {
    padding: 16px 12px;
    border-radius: var(--apple-border-radius);
    margin: 0;
    min-height: calc(100vh - 64px);
    border: 0.5px solid rgba(0, 0, 0, 0.08);
  }
  
  .reader-header {
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 20px;
    padding-bottom: 16px;
  }
  
  .back-button {
    width: 36px;
    height: 36px;
  }
  
  .document-title {
    font-size: 16px;
    flex: 1;
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  
  .page-info {
    width: 100%;
    text-align: center;
    margin-top: 8px;
    font-size: 12px;
    padding: 4px 12px;
  }
  
  .reader-content {
    margin-bottom: 20px;
  }
  
  .text-area {
    padding: 24px 16px;
    font-size: 16px;
    line-height: 1.8;
    min-height: 400px;
    border: 0.5px solid rgba(0, 0, 0, 0.08);
  }
  
  .text-content {
    font-size: 16px;
  }
  
  .word-clickable {
    padding: 1px 2px;
    margin: 0;
  }
  
  .reader-footer {
    flex-wrap: wrap;
    gap: 12px;
    padding-top: 16px;
  }
  
  .reader-footer .el-button {
    flex: 1;
    min-width: 80px;
    font-size: 14px;
  }
  
  .page-input {
    width: 80px;
  }
  
  .word-preview {
    max-width: calc(100vw - 32px);
    min-width: 200px;
    padding: 12px 14px;
  }
  
  .preview-header {
    flex-wrap: wrap;
    gap: 4px;
  }
  
  .preview-word {
    font-size: 14px;
  }
  
  .preview-hint {
    font-size: 10px;
  }
  
  .preview-meaning {
    font-size: 13px;
  }
  
  .word-detail-popover {
    width: calc(100vw - 32px) !important;
    max-width: none !important;
    max-height: 70vh;
    left: 50% !important;
    top: 50% !important;
    transform: translate(-50%, -50%) !important;
  }
  
  .popover-header {
    padding: 12px 16px;
  }
  
  .popover-header .word-title {
    font-size: 18px;
  }
  
  .popover-content {
    padding: 16px;
    max-height: calc(70vh - 50px);
  }
  
  .popover-content .meaning-item {
    padding: 12px;
    margin-bottom: 16px;
  }
  
  .popover-content .definition {
    font-size: 13px;
  }
  
  .popover-content .example {
    font-size: 12px;
  }
}
</style>

