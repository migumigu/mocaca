<template>
  <div 
    class="player-container"
    @touchstart="handleTouchStart"
    @touchend="handleTouchEnd"
  >
    <div class="back-button" @click="goBack">
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M19 12H5"></path>
        <path d="M12 19l-7-7 7-7"></path>
      </svg>
    </div>
    
    <transition name="slide">
      <div 
        v-if="!isTransitioning" 
        class="video-wrapper"
        :key="currentVideo.id"
      >
        <video 
          ref="videoRef"
          :src="currentVideo.url"
          class="video-element"
          playsinline
          webkit-playsinline
          x5-playsinline
          autoplay
          @click="togglePlay"
          @loadstart="isLoading = true"
          @canplay="isLoading = false"
        ></video>
        
        <div class="video-info">
          <div class="video-title">{{ removeFileExtension(currentVideo.filename) }}</div>
        </div>
        
        <!-- 加载指示器 -->
        <div v-if="isLoading" class="loading-indicator">
          <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <path d="M12 6v6l4 2"></path>
          </svg>
        </div>
        
        <!-- 播放按钮，仅在视频暂停且不在加载时显示 -->
        <div v-if="!isPlaying && !isLoading" class="play-button" @click.stop="playVideo">
          <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="white">
            <path d="M8 5v14l11-7z"/>
          </svg>
        </div>
      </div>
    </transition>
    
    <!-- 滑动提示 -->
    <div class="swipe-hint">
      <div class="swipe-arrow up">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 19V5M5 12l7-7 7 7"/>
        </svg>
      </div>
      <div class="swipe-arrow down">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 5v14M5 12l7 7 7-7"/>
        </svg>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

export default {
  props: {
    id: {
      type: String,
      required: true
    }
  },
  setup(props) {
    const router = useRouter()
    const route = useRoute()
    const videoRef = ref(null)
    const isPlaying = ref(false)
    const isLoading = ref(true) // 默认为加载状态
    const currentVideo = ref({})
    const nextVideoId = ref(null)
    const prevVideoId = ref(null)
    const isTransitioning = ref(false)
    const touchStartY = ref(0)
    const touchEndY = ref(0)
    const swipeThreshold = 100 // 滑动阈值，超过这个值才触发切换

    // 获取当前视频信息
    const fetchVideoInfo = async (id) => {
      try {
        const res = await fetch(`/api/videos/${id}`)
        if (!res.ok) throw new Error(`HTTP错误! 状态码: ${res.status}`)
        
        const data = await res.json()
        currentVideo.value = {
          ...data,
          url: `/api/videos/file/${encodeURIComponent(data.filename)}`
        }
        nextVideoId.value = data.next_id
        
        // 获取前一个视频ID
        try {
          const prevRes = await fetch(`/api/videos/prev/${id}`)
          if (prevRes.ok) {
            const prevData = await prevRes.json()
            prevVideoId.value = prevData.id
          }
        } catch (error) {
          console.error('获取前一个视频失败:', error)
          prevVideoId.value = null
        }
      } catch (error) {
        console.error('获取视频信息失败:', error)
      }
    }

    // 监听路由参数变化，更新视频
    watch(() => route.params.id, async (newId) => {
      if (newId) {
        await fetchVideoInfo(newId)
        playVideo()
      }
    })
    
    // 监听视频元素引用变化
    watch(() => videoRef.value, (newVideoRef) => {
      if (newVideoRef) {
        setupVideoEventListeners()
      }
    })

    onMounted(async () => {
      await fetchVideoInfo(route.params.id)
      playVideo()
      // 设置视频事件监听器
      setTimeout(() => {
        setupVideoEventListeners()
      }, 100) // 短暂延迟确保视频元素已加载
    })

    const playVideo = async () => {
      if (!videoRef.value) return
      
      try {
        // 先取消静音，提高自动播放成功率
        videoRef.value.muted = false
        await videoRef.value.play().catch(() => {
          // 如果自动播放失败，尝试静音播放
          videoRef.value.muted = true
          return videoRef.value.play()
        })
        isPlaying.value = true
      } catch (error) {
        console.error('视频播放失败:', error)
        isPlaying.value = false
      }
    }
    
    // 监听视频播放状态
    const setupVideoEventListeners = () => {
      if (!videoRef.value) return
      
      videoRef.value.onplay = () => {
        isPlaying.value = true
      }
      
      videoRef.value.onpause = () => {
        isPlaying.value = false
      }
      
      videoRef.value.onended = () => {
        isPlaying.value = false
        // 视频结束后自动播放下一个
        if (nextVideoId.value) {
          loadNextVideo()
        }
      }
    }

    const pauseVideo = () => {
      if (!videoRef.value) return
      
      videoRef.value.pause()
      isPlaying.value = false
    }

    const togglePlay = () => {
      if (isPlaying.value) {
        pauseVideo()
      } else {
        playVideo()
      }
    }

    const goBack = () => {
      router.push('/')
    }

    // 处理触摸开始事件
    const handleTouchStart = (event) => {
      touchStartY.value = event.touches[0].clientY
    }

    // 处理触摸结束事件
    const handleTouchEnd = (event) => {
      touchEndY.value = event.changedTouches[0].clientY
      const swipeDistance = touchEndY.value - touchStartY.value
      
      // 判断滑动方向和距离
      if (Math.abs(swipeDistance) > swipeThreshold) {
        if (swipeDistance > 0) {
          // 向下滑动，加载前一个视频
          loadPrevVideo()
        } else {
          // 向上滑动，加载下一个视频
          loadNextVideo()
        }
      }
    }

    // 加载下一个视频
    const loadNextVideo = () => {
      if (nextVideoId.value && !isTransitioning.value) {
        isTransitioning.value = true
        // 设置滑动方向 - 向上滑动加载下一个（新视频从上方进入）
        document.documentElement.style.setProperty('--slide-direction', '100%')
        router.push({ name: 'Player', params: { id: nextVideoId.value } })
        setTimeout(() => {
          isTransitioning.value = false
        }, 500) // 动画过渡时间
      }
    }

    // 加载前一个视频
    const loadPrevVideo = () => {
      if (prevVideoId.value && !isTransitioning.value) {
        isTransitioning.value = true
        // 设置滑动方向 - 向下滑动加载前一个（新视频从下方进入）
        document.documentElement.style.setProperty('--slide-direction', '-100%')
        router.push({ name: 'Player', params: { id: prevVideoId.value } })
        setTimeout(() => {
          isTransitioning.value = false
        }, 500) // 动画过渡时间
      }
    }

    // 去除文件后缀名
    const removeFileExtension = (filename) => {
      return filename.replace(/\.[^/.]+$/, "")
    }

    return { 
      videoRef,
      isPlaying,
      isLoading,
      currentVideo,
      isTransitioning,
      playVideo,
      pauseVideo,
      togglePlay,
      goBack,
      handleTouchStart,
      handleTouchEnd,
      setupVideoEventListeners,
      removeFileExtension
    }
  }
}
</script>

<style scoped>
.player-container {
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  width: 100vw;
  background: #000;
  z-index: 1000;
  overflow: hidden;
}

.video-wrapper {
  position: relative;
  height: 100%;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.video-element {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.video-info {
  position: absolute;
  bottom: 80px;
  left: 0;
  right: 0;
  padding: 16px;
  color: white;
  z-index: 10;
}

.video-title {
  font-size: 1.2rem;
  font-weight: bold;
  text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.8);
  margin-bottom: 8px;
  word-break: break-all;
}

.play-button, .loading-indicator {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(0, 0, 0, 0.5);
  border-radius: 50%;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.loading-indicator svg {
  animation: spin 1.5s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.back-button {
  position: absolute;
  top: 16px;
  left: 16px;
  z-index: 20;
  background: rgba(0, 0, 0, 0.5);
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

/* 滑动动画 */
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.5s ease;
}

.slide-enter-from {
  transform: translateY(var(--slide-direction, 100%));
}

.slide-leave-to {
  transform: translateY(calc(var(--slide-direction, 100%) * -1));
}

/* 滑动提示样式 */
.swipe-hint {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  z-index: 15;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.swipe-arrow {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.7;
  animation: pulse 2s infinite;
}

.swipe-arrow.up {
  animation-delay: 0s;
}

.swipe-arrow.down {
  animation-delay: 1s;
}

@keyframes pulse {
  0% {
    opacity: 0.3;
    transform: scale(0.8);
  }
  50% {
    opacity: 0.7;
    transform: scale(1);
  }
  100% {
    opacity: 0.3;
    transform: scale(0.8);
  }
}
</style>