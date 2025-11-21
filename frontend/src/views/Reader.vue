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
          ref="textContentRef"
          v-html="currentPageContent"
          @mousedown="handleMouseDown"
          @mouseup="handleMouseUp"
          @touchstart="handleTouchStart"
          @touchend="handleTouchEnd"
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
    
    <!-- Translation Modal -->
    <TranslationModal
      :visible="showTranslationModal"
      :selected-text="selectedTextForSave"
      @close="showTranslationModal = false"
      @save="handleSaveTranslation"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import { ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
import TranslationModal from '@/components/TranslationModal.vue'
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
const textContentRef = ref(null)

// Text selection states
const showTranslationModal = ref(false)
const selectedTextForSave = ref('')
const selectionStart = ref(null)
const selectionPosition = ref(null)
const longPressTimer = ref(null)
const isLongPress = ref(false)

async function fetchDocument() {
  try {
    const response = await api.get(`/documents/${documentId.value}`)
    documentTitle.value = response.data.title
    totalPages.value = response.data.total_pages || 0
    if (totalPages.value === 0) {
      ElMessage.warning('文档没有页面内容')
    }
  } catch (error) {
    console.error('获取文档信息失败:', error)
    const errorMsg = error.response?.data?.detail || error.message || '获取文档信息失败'
    ElMessage.error(errorMsg)
    if (error.response?.status === 404) {
      setTimeout(() => {
        router.push('/')
      }, 2000)
    }
  }
}

async function fetchPage(pageNumber) {
  try {
    const response = await api.get(
      `/documents/${documentId.value}/pages/${pageNumber}`
    )
    // 直接使用纯文本，不做单词高亮处理
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

// PC端鼠标选择
function handleMouseDown(event) {
  // 只响应右键
  if (event.button !== 2) return
  
  event.preventDefault()
  isLongPress.value = false
  selectionStart.value = { x: event.clientX, y: event.clientY }
  
  // 清除现有选择
  window.getSelection().removeAllRanges()
}

function handleMouseUp(event) {
  if (event.button !== 2) return
  
  event.preventDefault()
  processTextSelection()
}

// 移动端触摸选择
function handleTouchStart(event) {
  const touch = event.touches[0]
  selectionStart.value = { x: touch.clientX, y: touch.clientY }
  isLongPress.value = false
  
  // 长按检测
  longPressTimer.value = setTimeout(() => {
    isLongPress.value = true
  }, 500) // 500ms判定为长按
}

function handleTouchEnd(event) {
  clearTimeout(longPressTimer.value)
  
  if (isLongPress.value) {
    event.preventDefault()
    processTextSelection()
  }
}

// 处理文本选择
function processTextSelection() {
  const selection = window.getSelection()
  const selectedText = selection.toString().trim()
  
  if (selectedText) {
    // 计算选中文本在页面中的大概位置
    const range = selection.getRangeAt(0)
    const textBeforeSelection = textContentRef.value.textContent.substring(
      0,
      getTextOffsetInContainer(textContentRef.value, range.startContainer, range.startOffset)
    )
    
    selectedTextForSave.value = selectedText
    selectionPosition.value = textBeforeSelection.length
    showTranslationModal.value = true
  }
}

// 获取文本在容器中的偏移量
function getTextOffsetInContainer(container, node, offset) {
  let textOffset = 0
  const walker = document.createTreeWalker(
    container,
    NodeFilter.SHOW_TEXT,
    null,
    false
  )
  
  let currentNode = walker.nextNode()
  while (currentNode) {
    if (currentNode === node) {
      return textOffset + offset
    }
    textOffset += currentNode.textContent.length
    currentNode = walker.nextNode()
  }
  
  return textOffset
}

// 保存翻译到生词本
async function handleSaveTranslation(translation) {
  try {
    await api.post('/words/save-selection', {
      selected_text: selectedTextForSave.value,
      user_translation: translation,
      document_id: documentId.value,
      page_number: currentPage.value,
      position_in_page: selectionPosition.value
    })
    
    ElMessage.success('已添加到生词本')
  } catch (error) {
    console.error('保存失败:', error)
    const errorMsg = error.response?.data?.detail || error.message || '保存失败'
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

// 禁用右键菜单
function handleContextMenu(event) {
  event.preventDefault()
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
  
  // 添加右键菜单禁用
  document.addEventListener('contextmenu', handleContextMenu)
})

onUnmounted(() => {
  document.removeEventListener('contextmenu', handleContextMenu)
  if (longPressTimer.value) {
    clearTimeout(longPressTimer.value)
  }
})
</script>

<style scoped>
.reader-container {
  max-width: 1280px;
  margin: 0 auto;
  background: linear-gradient(135deg, #FFFEF7 0%, #FFF8DC 100%);
  border-radius: var(--rs-radius-xl);
  border: 2px solid #D4A574;
  box-shadow: 
    0 10px 40px rgba(139, 69, 19, 0.2),
    inset 0 0 60px rgba(212, 175, 116, 0.05);
  padding: 40px;
  min-height: calc(100vh - 160px);
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

/* 纸张纹理效果 */
.reader-container::before {
  content: '';
  position: absolute;
 top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    repeating-linear-gradient(
      0deg,
      transparent,
      transparent 2px,
      rgba(139, 69, 19, 0.015) 2px,
      rgba(139, 69, 19, 0.015) 4px
    ),
    repeating-linear-gradient(
      90deg,
      transparent,
      transparent 2px,
      rgba(139, 69, 19, 0.01) 2px,
      rgba(139, 69, 19, 0.01) 4px
    );
  pointer-events: none;
  opacity: 0.6;
}

.reader-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 2px solid rgba(212, 175, 116, 0.3);
  gap: 16px;
  position: relative;
  z-index: 1;
}

.back-button {
  flex-shrink: 0;
  background: linear-gradient(135deg, #D4AF37 0%, #C19A2E 100%);
  border: none;
  color: #2C1810;
  box-shadow: 0 2px 8px rgba(212, 175, 55, 0.3);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.back-button:hover {
  transform: translateX(-4px);
  box-shadow: 0 4px 12px rgba(212, 175, 55, 0.4);
}

.document-title {
  flex: 1;
  margin: 0;
  text-align: center;
  font-size: 22px;
  font-weight: 700;
  color: #2C1810;
  letter-spacing: 0.5px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.8);
}

.page-info {
  flex-shrink: 0;
  color: #5D4E3C;
  font-size: 14px;
  font-weight: 600;
  padding: 10px 20px;
  background: rgba(212, 175, 116, 0.15);
  border-radius: var(--rs-radius-md);
  border: 1px solid #D4A574;
  box-shadow: inset 0 1px 3px rgba(212, 175, 116, 0.2);
}

.reader-content {
  flex: 1;
  margin-bottom: 32px;
  position: relative;
  z-index: 1;
}

.text-area {
  min-height: 600px;
  padding: 56px 64px;
  background: #FFFEF7;
  border-radius: var(--rs-radius-lg);
  border: 1px solid #E8DCC8;
  box-shadow: 
    inset 2px 2px 8px rgba(139, 69, 19, 0.08),
    inset -2px -2px 8px rgba(255, 255, 255, 0.5),
    0 4px 16px rgba(139, 69, 19, 0.1);
  line-height: 1.9;
  font-size: 18px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

/* 页面边缘阴影效果 */
.text-area::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  box-shadow: 
    inset 20px 0 30px -20px rgba(139, 69, 19, 0.1),
    inset -20px 0 30px -20px rgba(139, 69, 19, 0.1);
  pointer-events: none;
}

.text-area:hover {
  box-shadow: 
    inset 2px 2px 10px rgba(139, 69, 19, 0.12),
    inset -2px -2px 10px rgba(255, 255, 255, 0.6),
    0 6px 20px rgba(139, 69, 19, 0.15);
}

.text-content {
  color: #2C1810;
  white-space: pre-wrap;
  word-wrap: break-word;
  user-select: text;
  font-family: Georgia, 'Times New Roman', serif;
  position: relative;
  z-index: 1;
  text-shadow: 0 1px 1px rgba(255, 255, 255, 0.5);
}

.text-content::selection {
  background: #fef08a;
  color: #2C1810;
}

.reader-footer {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  padding-top: 24px;
  border-top: 2px solid rgba(212, 175, 116, 0.3);
  position: relative;
  z-index: 1;
}

:deep(.reader-footer .el-button) {
  background: linear-gradient(135deg, #D4AF37 0%, #C19A2E 100%);
  border: none;
  color: #2C1810;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(212, 175, 55, 0.3);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

:deep(.reader-footer .el-button:hover) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(212, 175, 55, 0.4);
}

:deep(.reader-footer .el-button:disabled) {
  background: rgba(212, 175, 116, 0.3);
  color: #8B7355;
}

.page-input {
  width: 120px;
}

:deep(.page-input .el-input-number__decrease),
:deep(.page-input .el-input-number__increase) {
  background: rgba(212, 175, 116, 0.2);
  border-color: #D4A574;
  color: #2C1810;
}

:deep(.page-input .el-input__wrapper) {
  background: rgba(255, 254, 247, 0.9);
  border-color: #D4A574;
  box-shadow: inset 0 1px 3px rgba(139, 69, 19, 0.1);
}

/* Responsive */
@media (max-width: 768px) {
  .reader-container {
    padding: 24px;
    border-radius: var(--rs-radius-md);
  }
  
  .text-area {
    padding: 32px 24px;
    min-height: 400px;
    font-size: 16px;
  }
  
  .document-title {
    font-size: 18px;
  }
  
  .reader-footer {
    flex-wrap: wrap;
    gap: 12px;
  }
  
  .page-input {
    width: 100px;
  }
}
</style>
