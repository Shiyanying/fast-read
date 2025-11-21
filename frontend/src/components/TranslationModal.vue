<template>
  <transition name="modal-fade">
    <div v-if="visible" class="modal-overlay" @click.self="handleClose">
      <div class="translation-modal" @click.stop>
        <div class="modal-header">
          <h3 class="modal-title">添加到生词本</h3>
          <button class="close-btn" @click="handleClose">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
        
        <div class="modal-body">
          <div class="selected-text-section">
            <label class="label">选中的文本</label>
            <div class="selected-text">{{ selectedText }}</div>
          </div>
          
          <div class="translation-section">
            <label class="label" for="translation-input">中文翻译 *</label>
            <textarea
              id="translation-input"
              v-model="translation"
              class="translation-input"
              placeholder="请输入中文翻译..."
              rows="3"
              :autofocus="true"
              @keydown.enter.ctrl="handleSave"
            ></textarea>
            <div class="hint-text">提示: Ctrl+Enter 快速保存</div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="handleClose">取消</button>
          <button 
            class="btn btn-primary" 
            @click="handleSave"
            :disabled="!translation.trim()"
          >
            保存
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  selectedText: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['close', 'save'])

const translation = ref('')

watch(() => props.visible, (newVal) => {
  if (newVal) {
    translation.value = ''
    // Focus the textarea after modal opens
    setTimeout(() => {
      document.getElementById('translation-input')?.focus()
    }, 100)
  }
})

function handleClose() {
  translation.value = ''
  emit('close')
}

function handleSave() {
  if (translation.value.trim()) {
    emit('save', translation.value.trim())
    handleClose()
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.translation-modal {
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  animation: modal-slide-up 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes modal-slide-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px 28px;
  border-bottom: 1px solid #e5e5e5;
}

.modal-title {
  font-size: 20px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0;
}

.close-btn {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  border: none;
  background: transparent;
  color: #737373;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.close-btn:hover {
  background: #f5f5f5;
  color: #1a1a1a;
}

.modal-body {
  padding: 28px;
  overflow-y: auto;
  flex: 1;
}

.selected-text-section {
  margin-bottom: 24px;
}

.translation-section {
  margin-bottom: 8px;
}

.label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 8px;
}

.selected-text {
  padding: 16px;
  background: linear-gradient(135deg, #fef9c3 0%, #fef08a 100%);
  border-radius: 12px;
  font-size: 16px;
  line-height: 1.6;
  color: #2d2d2d;
  border: 2px solid #fef08a;
}

.translation-input {
  width: 100%;
  padding: 14px 16px;
  border: 2px solid #e5e5e5;
  border-radius: 12px;
  font-size: 15px;
  line-height: 1.6;
  color: #1a1a1a;
  resize: vertical;
  min-height: 80px;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Segoe UI', Roboto, sans-serif;
}

.translation-input:focus {
  outline: none;
  border-color: #2d2d2d;
  box-shadow: 0 0 0 3px rgba(45, 45, 45, 0.1);
}

.translation-input::placeholder {
  color: #a3a3a3;
}

.hint-text {
  margin-top: 8px;
  font-size: 12px;
  color: #737373;
}

.modal-footer {
  padding: 20px 28px;
  border-top: 1px solid #e5e5e5;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.btn {
  padding: 12px 24px;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  min-width: 90px;
}

.btn-secondary {
  background: #f5f5f5;
  color: #525252;
}

.btn-secondary:hover {
  background: #e5e5e5;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.btn-primary {
  background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

/* Mobile responsive */
@media (max-width: 768px) {
  .translation-modal {
    width: 95%;
    max-width: none;
    margin: 20px;
  }
  
  .modal-header,
  .modal-body,
  .modal-footer {
    padding: 20px;
  }
  
  .modal-title {
    font-size: 18px;
  }
}
</style>
