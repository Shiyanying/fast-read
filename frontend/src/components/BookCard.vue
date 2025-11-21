<template>
  <div class="book-card-wrapper" @click="$emit('open')">
    <div class="book-card" :class="{ 'book-card-hover': isHovered }" 
         @mouseenter="isHovered = true"
         @mouseleave="isHovered = false">
      <!-- 书脊 -->
      <div class="book-spine">
        <div class="spine-text">{{ truncatedTitle }}</div>
      </div>
      
      <!-- 封面 -->
      <div class="book-cover">
        <div class="cover-content">
          <h3 class="book-title">{{ title }}</h3>
          <div class="book-meta">
            <div class="meta-item">
              <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
              </svg>
              <span>{{ pages }} 页</span>
            </div>
            <div class="meta-item" v-if="progress">
              <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              <span>{{ progress }}%</span>
            </div>
          </div>
        </div>
        
        <!-- 书页装饰 -->
        <div class="book-pages-decoration">
          <div class="page-layer" v-for="i in 5" :key="i" :style="{ right: `-${i * 2}px`, top: `${i}px` }"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  pages: {
    type: Number,
    default: 0
  },
  progress: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['open'])
const isHovered = ref(false)

const truncatedTitle = computed(() => {
  if (props.title.length > 20) {
    return props.title.substring(0, 18) + '...'
  }
  return props.title
})
</script>

<style scoped>
.book-card-wrapper {
  perspective: 1200px;
  cursor: pointer;
  padding: 8px;
}

.book-card {
  position: relative;
  width: 200px;
  height: 280px;
  transform-style: preserve-3d;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.book-card-hover {
  transform: translateY(-12px) rotateY(8deg);
}

/* 书脊 */
.book-spine {
  position: absolute;
  left: 0;
  top: 0;
  width: 40px;
  height: 100%;
  background: linear-gradient(to right, #8B4513, #654321);
  transform-origin: left center;
  transform: rotateY(-90deg);
  box-shadow: inset -2px 0 8px rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0 4px 4px 0;
}

.spine-text {
  writing-mode: vertical-rl;
  color: #FDF5E6;
  font-size: 14px;
  font-weight: 600;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
  letter-spacing: 2px;
}

/* 封面 */
.book-cover {
  position: absolute;
  left: 40px;
  top: 0;
  width: calc(100% - 40px);
  height: 100%;
  background: linear-gradient(135deg, #FDF5E6 0%, #F5E6D3 100%);
  border-radius: 0 8px 8px 0;
  box-shadow: 
    2px 4px 12px rgba(0, 0, 0, 0.2),
    inset 0 0 40px rgba(139, 69, 19, 0.05);
  border: 2px solid #D4A574;
  border-left: none;
  overflow: hidden;
}

.cover-content {
  padding: 24px 16px;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  position: relative;
  z-index: 2;
}

.book-title {
  font-size: 18px;
  font-weight: 700;
  color: #2C1810;
  line-height: 1.4;
  margin: 0;
  text-align: center;
  word-wrap: break-word;
  text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.5);
}

.book-meta {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #5D4E3C;
  font-size: 13px;
  font-weight: 500;
}

.icon {
  width: 18px;
  height: 18px;
  color: #8B4513;
}

/* 书页装饰 */
.book-pages-decoration {
  position: absolute;
  right: 0;
  top: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.page-layer {
  position: absolute;
  width: calc(100% - 10px);
  height: calc(100% - 8px);
  background: linear-gradient(to right, #FFFEF7 0%, #FFF8DC 100%);
  border-radius: 0 6px 6px 0;
  box-shadow: 1px 1px 3px rgba(0, 0, 0, 0.15);
  z-index: -1;
}

/* 纸张纹理效果 */
.book-cover::before {
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
      rgba(139, 69, 19, 0.02) 2px,
      rgba(139, 69, 19, 0.02) 4px
    );
  pointer-events: none;
}

/* 悬停阴影效果 */
.book-card-hover .book-cover {
  box-shadow: 
    4px 8px 24px rgba(0, 0, 0, 0.3),
    0 0 60px rgba(212, 175, 116, 0.4),
    inset 0 0 40px rgba(139, 69, 19, 0.08);
}

.book-card-hover .book-spine {
  box-shadow: 
    inset -2px 0 8px rgba(0, 0, 0, 0.4),
    -2px 0 12px rgba(0, 0, 0, 0.3);
}

/* 响应式 */
@media (max-width: 768px) {
  .book-card {
    width: 160px;
    height: 220px;
  }
  
  .book-spine {
    width: 32px;
  }
  
  .book-cover {
    left: 32px;
    width: calc(100% - 32px);
  }
  
  .book-title {
    font-size: 16px;
  }
  
  .cover-content {
    padding: 16px 12px;
  }
}
</style>
