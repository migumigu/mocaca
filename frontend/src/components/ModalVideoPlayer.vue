<template>
  <transition name="modal">
    <div 
      v-if="visible" 
      class="modal-player-container"
      @touchstart="handleTouchStart"
      @touchmove="handleTouchMove"
      @touchend="handleTouchEnd"
    >
      <!-- 返回按钮 -->
      <div class="back-button" @click="close">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M19 12H5"></path>
          <path d="M12 19l-7-7 7-7"></path>
        </svg>
      </div>
      
      <!-- 视频播放区域 -->
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
            @loadstart="handleVideoLoadStart"
            @loadedmetadata="handleVideoLoadedMetadata"
            @canplay="handleVideoCanPlay"
            @ended="handleVideoEnded"
          ></video>
          
          <!-- 视频信息 -->
          <div class="video-info">
            <div class="video-title">{{ currentVideo.filename ? removeFileExtension(currentVideo.filename) : '' }}</div>
            <div class="video-counter" v-if="currentVideoIndex !== -1 && totalVideos > 0">
              {{ currentVideoIndex + 1 }} / {{ totalVideos }}
            </div>
          </div>
          
          <!-- 加载指示器 -->
          <div v-if="isLoading" class="loading-indicator">
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"></circle>
              <path d="M12 6v6l4 2"></path>
            </svg>
          </div>
          
          <!-- 播放按钮 -->
          <div v-if="!isPlaying && !isLoading" class="play-button" @click.stop="playVideo">
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="white">
              <path d="M8 5v14l11-7z"/>
            </svg>
          </div>
          
          <!-- 关闭按钮 -->
          <div class="close-button" @click="close">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M18 6L6 18"></path>
              <path d="M6 6l12 12"></path>
            </svg>
          </div>
          
          <!-- 右侧操作栏 -->
          <div class="right-action-bar">
            <!-- 收藏按钮 -->
            <div class="action-button" @click.stop="toggleFavorite">
              <div class="action-icon">
                <svg v-if="isFavorited" class="favorite-icon filled" width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
                </svg>
                <svg v-else class="favorite-icon outline" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
                </svg>
            </div>
          </div>
          
          <!-- 讨厌按钮 -->
          <div class="action-button" @click.stop="toggleDislike">
            <div class="action-icon">
              <svg v-if="isDisliked" class="dislike-icon filled" width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
                <path d="M7 8L17 16" stroke="white" stroke-width="2" stroke-linecap="round"/>
                <path d="M17 8L7 16" stroke="white" stroke-width="2" stroke-linecap="round"/>
                <path d="M12 8L12 16" stroke="white" stroke-width="2" stroke-linecap="round"/>
              </svg>
              <svg v-else class="dislike-icon outline" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
                <path d="M7 8L17 16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                <path d="M17 8L7 16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                <path d="M12 8L12 16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </div>
          </div>
        </div>
        
          <!-- 快进进度条 -->
          <div v-if="showSeekBar" class="seek-bar-overlay">
            <div class="seek-bar-container">
              <div class="seek-bar">
                <div class="seek-progress" :style="{ width: seekProgress + '%' }"></div>
              </div>
              <div class="seek-time">
                <span>{{ formatTime(seekCurrentTime) }}</span>
                <span class="seek-duration">{{ formatTime(videoDuration) }}</span>
              </div>
              <div class="seek-amount">
                <span v-if="seekAmount > 0">+{{ seekAmount }}秒</span>
                <span v-else-if="seekAmount < 0">{{ seekAmount }}秒</span>
              </div>
            </div>
          </div>

          <!-- 发现页面刷新提示 -->
          <div v-if="playlistType === 'random' && showRefreshPrompt" class="refresh-prompt">
            <div class="refresh-content">
              <div class="refresh-text">已到达当前随机列表末尾</div>
              <button class="refresh-button" @click.stop="generateNewRandomList">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M23 4v6h-6"></path>
                  <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
                </svg>
                生成新随机列表
              </button>
            </div>
            </div>
        </div>
      </transition>
    </div>
  </transition>
</template>

<script>
import { ref, watch, nextTick } from 'vue'

export default {
  name: 'ModalVideoPlayer',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    video: {
      type: Object,
      default: () => ({})
    },
    playlistType: {
      type: String,
      default: 'latest'
    },
    playlistSeed: {
      type: [String, Number],
      default: null
    },
    playlistVideos: {
      type: Array,
      default: () => []
    },
    currentIndex: {
      type: Number,
      default: -1
    },
    fromPage: {
      type: String,
      default: ''
    }
  },
  emits: ['close', 'video-change', 'list-refresh'],
  setup(props, { emit }) {
    const videoRef = ref(null)
    const isPlaying = ref(false)
    const isLoading = ref(true)
    const isTransitioning = ref(false)
    const touchStartY = ref(0)
    const touchEndY = ref(0)
    const touchStartX = ref(0)
    const touchCurrentX = ref(0)
    const swipeThreshold = 100
    
    // 长按2倍速相关状态
    const longPressTimer = ref(null)
    const isLongPressing = ref(false)
    const originalPlaybackRate = ref(1)
    
    // 进度条快进相关状态
    const showSeekBar = ref(false)
    const seekStartTime = ref(0)
    const seekCurrentTime = ref(0)
    const seekAmount = ref(0)
    const seekProgress = ref(0)
    const videoDuration = ref(0)
    const isSeeking = ref(false)
    
    // 播放列表相关状态
    const currentVideo = ref({})
    const currentVideoIndex = ref(-1)
    const totalVideos = ref(0)
    const playlistVideos = ref([])
    const playlistType = ref('latest')
    const playlistSeed = ref(null)
    
    // 用户行为状态
    const isFavorited = ref(false)
    const isDisliked = ref(false)
    const showRefreshPrompt = ref(false)
    
    // 获取基础URL
    const getBaseUrl = () => {
      return import.meta.env.DEV 
        ? '/api' 
        : `${window.location.protocol}//${window.location.hostname}:5003/api`
    }
    
    // 初始化播放器
    const initPlayer = async () => {
      if (!props.video || !props.video.id) return
      
      currentVideo.value = { ...props.video }
      currentVideoIndex.value = props.currentIndex
      playlistVideos.value = [...props.playlistVideos]
      playlistType.value = props.playlistType
      playlistSeed.value = props.playlistSeed
      totalVideos.value = props.playlistVideos.length
      
      // 设置视频URL - 使用正确的API路径
      currentVideo.value.url = `${getBaseUrl()}/videos/file/${encodeURIComponent(currentVideo.value.filename)}`
      
      console.log('模态框播放器初始化:', {
        video: currentVideo.value,
        index: currentVideoIndex.value,
        total: totalVideos.value,
        playlistType: playlistType.value
      })
      
      // 检查用户行为状态
      await checkFavoriteStatus()
      await checkDislikeStatus()
      
      // 自动播放
      await nextTick()
      playVideo()
    }
    
    // 播放视频
    const playVideo = async () => {
      if (!videoRef.value) {
        console.log('videoRef为null，无法播放')
        return false
      }
      
      console.log('开始播放视频，当前视频状态:', {
        paused: videoRef.value.paused,
        readyState: videoRef.value.readyState,
        currentTime: videoRef.value.currentTime,
        ended: videoRef.value.ended,
        muted: videoRef.value.muted
      })
      
      try {
        const playPromise = videoRef.value.play()
        
        // 处理播放Promise
        await playPromise.catch(async (error) => {
          console.log('第一次播放失败，尝试延迟播放:', error)
          // 延迟后重试播放
          await new Promise(resolve => setTimeout(resolve, 500))
          if (videoRef.value) {
            return videoRef.value.play()
          }
          throw error
        })
        
        console.log('播放命令已发送，等待播放状态确认...')
        
        // 添加播放状态验证
        const playSuccess = await new Promise((resolve) => {
          let attempts = 0
          const maxAttempts = 15
          
          const checkPlayState = () => {
            if (!videoRef.value) {
              console.log('videoRef为null，停止播放状态检查')
              resolve(false)
              return
            }
            
            attempts++
            console.log(`播放状态检查第${attempts}次:`, {
              paused: videoRef.value.paused,
              readyState: videoRef.value.readyState,
              currentTime: videoRef.value.currentTime
            })
            
            // 只要视频不在暂停状态就认为播放成功
            if (!videoRef.value.paused) {
              console.log('视频确认开始播放')
              isPlaying.value = true
              resolve(true)
            } else if (attempts >= maxAttempts) {
              console.log('播放状态检查超时，视频可能被浏览器阻止')
              // 即使超时也返回false而不是reject，避免阻塞流程
              resolve(false)
            } else {
              setTimeout(checkPlayState, 200)
            }
          }
          checkPlayState()
        })
        
        if (playSuccess) {
          console.log('视频播放成功，当前播放状态:', isPlaying.value)
        } else {
          console.log('视频播放可能被浏览器阻止')
          isPlaying.value = false
        }
        
        return playSuccess
      } catch (error) {
        console.error('视频播放失败:', error)
        isPlaying.value = false
        return false
      }
    }
    
    // 暂停视频
    const pauseVideo = () => {
      if (!videoRef.value) return
      videoRef.value.pause()
      isPlaying.value = false
    }
    
    // 切换播放状态
    const togglePlay = () => {
      if (isPlaying.value) {
        pauseVideo()
      } else {
        playVideo()
      }
    }
    
    // 视频加载开始
    const handleVideoLoadStart = () => {
      console.log('=== 视频加载开始 ===')
      console.log('视频元素尺寸:', {
        width: videoRef.value?.offsetWidth,
        height: videoRef.value?.offsetHeight,
        clientWidth: videoRef.value?.clientWidth,
        clientHeight: videoRef.value?.clientHeight,
        videoWidth: videoRef.value?.videoWidth,
        videoHeight: videoRef.value?.videoHeight
      })
      isLoading.value = true
    }

    // 视频元数据加载完成
    const handleVideoLoadedMetadata = () => {
      console.log('=== 视频元数据加载完成 ===')
      console.log('视频原始尺寸:', {
        videoWidth: videoRef.value?.videoWidth,
        videoHeight: videoRef.value?.videoHeight,
        duration: videoRef.value?.duration
      })
      console.log('视频元素当前尺寸:', {
        offsetWidth: videoRef.value?.offsetWidth,
        offsetHeight: videoRef.value?.offsetHeight,
        clientWidth: videoRef.value?.clientWidth,
        clientHeight: videoRef.value?.clientHeight
      })
    }

    // 视频可以播放
    const handleVideoCanPlay = () => {
      console.log('=== 视频可以播放 ===')
      console.log('视频元素最终尺寸:', {
        offsetWidth: videoRef.value?.offsetWidth,
        offsetHeight: videoRef.value?.offsetHeight,
        clientWidth: videoRef.value?.clientWidth,
        clientHeight: videoRef.value?.clientHeight,
        videoWidth: videoRef.value?.videoWidth,
        videoHeight: videoRef.value?.videoHeight
      })
      isLoading.value = false
    }

    // 视频结束处理
    const handleVideoEnded = () => {
      console.log('=== 视频播放完成，自动切换到下一个视频 ===')
      console.log('视频结束时间:', videoRef.value?.currentTime, '视频总时长:', videoRef.value?.duration)
      isPlaying.value = false
      loadNextVideo()
    }
    
    // 加载下一个视频
    const loadNextVideo = () => {
      if (isTransitioning.value) {
        console.log('正在切换中，跳过重复切换')
        return
      }
      
      const nextIndex = currentVideoIndex.value + 1
      console.log('=== 加载下一个视频 ===', {
        currentIndex: currentVideoIndex.value,
        nextIndex: nextIndex,
        playlistLength: playlistVideos.value.length,
        isTransitioning: isTransitioning.value,
        source: '视频播放完成或向上滑动'
      })
      
      if (nextIndex < playlistVideos.value.length) {
        switchVideo(nextIndex)
      } else {
        console.log('已到达播放列表末尾，无法继续切换')
        // 边界处理
        if (playlistType.value === 'random' && nextIndex === 200) {
          showRefreshPrompt.value = true
          setTimeout(() => {
            showRefreshPrompt.value = false
          }, 3000)
        }
      }
    }
    
    // 加载上一个视频
    const loadPrevVideo = () => {
      if (isTransitioning.value) {
        console.log('正在切换中，跳过重复切换')
        return
      }
      
      const prevIndex = currentVideoIndex.value - 1
      console.log('=== 加载上一个视频 ===', {
        currentIndex: currentVideoIndex.value,
        prevIndex: prevIndex,
        isTransitioning: isTransitioning.value,
        source: '向下滑动'
      })
      
      if (prevIndex >= 0) {
        switchVideo(prevIndex)
      } else {
        console.log('已到达播放列表开头，无法继续切换')
      }
    }
    
    // 切换视频
    const switchVideo = async (newIndex) => {
      if (newIndex < 0 || newIndex >= playlistVideos.value.length) {
        console.warn('无效的视频索引:', newIndex)
        return
      }
      
      isTransitioning.value = true
      currentVideoIndex.value = newIndex
      currentVideo.value = { ...playlistVideos.value[newIndex] }
      currentVideo.value.url = `${getBaseUrl()}/videos/file/${encodeURIComponent(currentVideo.value.filename)}`
      
      console.log('=== 切换视频 ===', {
        from: props.currentIndex,
        to: newIndex,
        video: currentVideo.value,
        isTransitioning: isTransitioning.value
      })
      
      // 通知父组件视频切换
      emit('video-change', {
        video: currentVideo.value,
        index: newIndex
      })
      
      // 检查新视频的用户行为状态
      await checkFavoriteStatus()
      await checkDislikeStatus()
      
      // 立即设置视频源并尝试播放
      await nextTick()
      if (videoRef.value) {
        console.log('设置新视频源:', currentVideo.value.url)
        videoRef.value.src = currentVideo.value.url
        videoRef.value.load() // 强制加载新源
        videoRef.value.preload = 'auto' // 预加载
        
        // 检查视频的readyState
        console.log('视频加载状态:', {
          readyState: videoRef.value.readyState,
          HAVE_NOTHING: videoRef.value.HAVE_NOTHING,
          HAVE_METADATA: videoRef.value.HAVE_METADATA,
          HAVE_CURRENT_DATA: videoRef.value.HAVE_CURRENT_DATA,
          HAVE_FUTURE_DATA: videoRef.value.HAVE_FUTURE_DATA,
          HAVE_ENOUGH_DATA: videoRef.value.HAVE_ENOUGH_DATA
        })
      }
      
      // 等待视频加载完成后再尝试播放
      const waitForVideoReady = () => {
        return new Promise((resolve) => {
          if (!videoRef.value) {
            console.log('videoRef为null，跳过等待')
            resolve()
            return
          }
          
          if (videoRef.value.readyState >= videoRef.value.HAVE_ENOUGH_DATA) {
            console.log('视频已准备好，立即播放')
            resolve()
            return
          }
          
          console.log('等待视频加载完成...')
          const onCanPlay = () => {
            console.log('视频canplay事件触发，开始播放')
            if (videoRef.value) {
              videoRef.value.removeEventListener('canplay', onCanPlay)
            }
            resolve()
          }
          
          if (videoRef.value) {
            videoRef.value.addEventListener('canplay', onCanPlay)
          }
          
          // 超时保护
          setTimeout(() => {
            console.log('视频加载超时，强制尝试播放')
            if (videoRef.value) {
              videoRef.value.removeEventListener('canplay', onCanPlay)
            }
            resolve()
          }, 3000)
        })
      }
      
      try {
        await waitForVideoReady()
        const playSuccess = await playVideo()
        
        if (playSuccess) {
          console.log('切换视频后播放成功，重置isTransitioning状态')
          isTransitioning.value = false
        } else {
          console.log('播放失败，但重置isTransitioning状态避免阻塞')
          isTransitioning.value = false
        }
      } catch (error) {
        console.log('切换视频播放失败:', error)
        isTransitioning.value = false
      }
    }
    
    // 触摸事件处理
    const handleTouchStart = (event) => {
      touchStartY.value = event.touches[0].clientY
      touchStartX.value = event.touches[0].clientX
      touchCurrentX.value = touchStartX.value
      
      console.log('=== 触摸开始 ===', {
        startY: touchStartY.value,
        startX: touchStartX.value
      })
      
      // 开始长按计时器（2倍速播放）
      longPressTimer.value = setTimeout(() => {
        if (videoRef.value && !isLongPressing.value) {
          isLongPressing.value = true
          originalPlaybackRate.value = videoRef.value.playbackRate
          videoRef.value.playbackRate = 2.0 // 2倍速播放
          console.log('长按2倍速播放激活')
        }
      }, 500) // 长按500ms触发
      
      // 初始化进度条快进状态
      if (videoRef.value) {
        seekStartTime.value = videoRef.value.currentTime
        seekCurrentTime.value = seekStartTime.value
        videoDuration.value = videoRef.value.duration || 0
        isSeeking.value = false
      }
    }
    
    const handleTouchMove = (event) => {
      if (!event.touches.length) return
      
      touchCurrentX.value = event.touches[0].clientX
      const deltaX = touchCurrentX.value - touchStartX.value
      const deltaY = event.touches[0].clientY - touchStartY.value
      
      console.log('=== 触摸移动 ===', {
        currentX: touchCurrentX.value,
        currentY: event.touches[0].clientY,
        deltaX: deltaX,
        deltaY: deltaY,
        isSeeking: isSeeking.value
      })
      
      // 水平滑动超过阈值，开始进度条快进
      if (Math.abs(deltaX) > 20 && videoRef.value) {
        // 取消长按计时器
        if (longPressTimer.value) {
          clearTimeout(longPressTimer.value)
          longPressTimer.value = null
          console.log('取消长按计时器')
        }
        
        // 停止长按2倍速
        if (isLongPressing.value) {
          isLongPressing.value = false
          videoRef.value.playbackRate = originalPlaybackRate.value
          console.log('停止长按2倍速')
        }
        
        // 开始进度条快进
        if (!isSeeking.value) {
          isSeeking.value = true
          showSeekBar.value = true
          console.log('开始进度条快进')
        }
        
        // 计算快进量（每10像素对应1秒）
        const seekSeconds = Math.round(deltaX / 10)
        seekAmount.value = seekSeconds
        seekCurrentTime.value = Math.max(0, Math.min(videoDuration.value, seekStartTime.value + seekSeconds))
        seekProgress.value = (seekCurrentTime.value / videoDuration.value) * 100
        
        console.log('进度条快进:', {
          seekSeconds: seekSeconds,
          currentTime: seekCurrentTime.value,
          progress: seekProgress.value
        })
      }
    }
    
    const handleTouchEnd = (event) => {
      touchEndY.value = event.changedTouches[0].clientY
      const swipeDistance = touchEndY.value - touchStartY.value
      
      console.log('=== 触摸结束 ===', {
        endY: touchEndY.value,
        startY: touchStartY.value,
        swipeDistance: swipeDistance,
        swipeThreshold: swipeThreshold,
        isSeeking: isSeeking.value,
        isLongPressing: isLongPressing.value
      })
      
      // 取消长按计时器
      if (longPressTimer.value) {
        clearTimeout(longPressTimer.value)
        longPressTimer.value = null
        console.log('取消长按计时器')
      }
      
      // 恢复长按2倍速
      if (isLongPressing.value) {
        isLongPressing.value = false
        if (videoRef.value) {
          videoRef.value.playbackRate = originalPlaybackRate.value
        }
        console.log('恢复长按2倍速')
      }
      
      // 处理进度条快进
      if (isSeeking.value && videoRef.value) {
        console.log('应用进度条快进:', {
          seekCurrentTime: seekCurrentTime.value,
          seekAmount: seekAmount.value
        })
        
        // 应用快进
        videoRef.value.currentTime = seekCurrentTime.value
        showSeekBar.value = false
        isSeeking.value = false
        
        // 如果视频暂停，播放视频
        if (videoRef.value.paused) {
          console.log('视频暂停，重新播放')
          playVideo()
        }
      }
      
      // 处理垂直滑动切换视频（只在没有进行进度条快进时）
      if (!isSeeking.value && Math.abs(swipeDistance) > swipeThreshold) {
        console.log('检测到垂直滑动，距离:', swipeDistance, '阈值:', swipeThreshold)
        
        // 修正滑动方向判断：向上滑动（手指向上移动）应该是负数，向下滑动（手指向下移动）应该是正数
        if (swipeDistance < 0) {
          // 向上滑动（手指向上移动），加载下一个视频
          console.log('向上滑动，加载下一个视频')
          loadNextVideo()
        } else {
          // 向下滑动（手指向下移动），加载前一个视频
          console.log('向下滑动，加载前一个视频')
          loadPrevVideo()
        }
      } else if (!isSeeking.value) {
        console.log('滑动距离不足或正在进行进度条快进，不切换视频')
      }
    }
    
    // 检查收藏状态
    const checkFavoriteStatus = async () => {
      const savedUser = localStorage.getItem('currentUser')
      if (!savedUser) return
      
      const user = JSON.parse(savedUser)
      const videoId = currentVideo.value.id
      
      try {
        const res = await fetch(`${getBaseUrl()}/favorites/check?user_id=${user.id}&video_id=${videoId}`)
        if (res.ok) {
          const data = await res.json()
          isFavorited.value = data.is_favorited
        }
      } catch (error) {
        console.error('检查收藏状态失败:', error)
      }
    }
    
    // 检查讨厌状态
    const checkDislikeStatus = async () => {
      const savedUser = localStorage.getItem('currentUser')
      if (!savedUser) return
      
      const user = JSON.parse(savedUser)
      const videoId = currentVideo.value.id
      
      try {
        const res = await fetch(`${getBaseUrl()}/dislikes/check?user_id=${user.id}&video_id=${videoId}`)
        if (res.ok) {
          const data = await res.json()
          isDisliked.value = data.is_disliked
        }
      } catch (error) {
        console.error('检查讨厌状态失败:', error)
      }
    }
    
    // 切换收藏
    const toggleFavorite = async () => {
      const savedUser = localStorage.getItem('currentUser')
      if (!savedUser) {
        alert('请先登录后再收藏')
        return
      }
      
      const user = JSON.parse(savedUser)
      const videoId = currentVideo.value.id
      
      try {
        if (isFavorited.value) {
          // 取消收藏
          await fetch(`${getBaseUrl()}/favorites?user_id=${user.id}&video_id=${videoId}`, {
            method: 'DELETE'
          })
          isFavorited.value = false
        } else {
          // 添加收藏
          await fetch(`${getBaseUrl()}/favorites`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: user.id, video_id: videoId })
          })
          isFavorited.value = true
        }
      } catch (error) {
        console.error('收藏操作失败:', error)
      }
    }
    
    // 切换讨厌
    const toggleDislike = async () => {
      const savedUser = localStorage.getItem('currentUser')
      if (!savedUser) {
        alert('请先登录后再操作')
        return
      }
      
      const user = JSON.parse(savedUser)
      const videoId = currentVideo.value.id
      
      try {
        if (isDisliked.value) {
          // 取消讨厌
          await fetch(`${getBaseUrl()}/dislikes?user_id=${user.id}&video_id=${videoId}`, {
            method: 'DELETE'
          })
          isDisliked.value = false
        } else {
          // 添加讨厌
          await fetch(`${getBaseUrl()}/dislikes`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: user.id, video_id: videoId })
          })
          isDisliked.value = true
        }
      } catch (error) {
        console.error('讨厌操作失败:', error)
      }
    }
    
    // 生成新随机列表
    const generateNewRandomList = () => {
      emit('list-refresh')
    }
    
    // 关闭模态框
    const close = () => {
      pauseVideo()
      emit('close')
    }
    
    // 去除文件扩展名
    const removeFileExtension = (filename) => {
      if (!filename) return ''
      const baseName = filename.split('/').pop().split('\\').pop()
      return baseName.replace(/\.[^/.]+$/, "")
    }

    // 格式化时间显示（秒 → 分:秒）
    const formatTime = (seconds) => {
      if (!seconds || isNaN(seconds)) return '00:00'
      const mins = Math.floor(seconds / 60)
      const secs = Math.floor(seconds % 60)
      return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
    }
    
    // 监听visible变化
    watch(() => props.visible, (newVal) => {
      if (newVal) {
        initPlayer()
      }
    })
    
    // 监听视频变化
    watch(() => props.video, (newVideo) => {
      if (newVideo && props.visible) {
        currentVideo.value = { ...newVideo }
        currentVideo.value.url = `${getBaseUrl()}/videos/file/${encodeURIComponent(newVideo.filename)}`
        console.log('视频变化监听:', currentVideo.value)
        checkFavoriteStatus()
        checkDislikeStatus()
        playVideo()
      }
    })
    
    // 监听播放列表变化
    watch(() => props.playlistVideos, (newVideos) => {
      if (newVideos && props.visible) {
        playlistVideos.value = [...newVideos]
        totalVideos.value = newVideos.length
        console.log('播放列表变化，总视频数:', totalVideos.value)
      }
    })
    
    // 监听当前索引变化
    watch(() => props.currentIndex, (newIndex) => {
      if (newIndex !== -1 && props.visible) {
        currentVideoIndex.value = newIndex
        console.log('当前索引变化:', newIndex)
      }
    })
    
    return {
      videoRef,
      isPlaying,
      isLoading,
      isTransitioning,
      currentVideo,
      currentVideoIndex,
      totalVideos,
      playlistType,
      isFavorited,
      isDisliked,
      showRefreshPrompt,
      showSeekBar,
      seekCurrentTime,
      videoDuration,
      seekProgress,
      seekAmount,
      playVideo,
      pauseVideo,
      togglePlay,
      handleTouchStart,
      handleTouchMove,
      handleTouchEnd,
      loadNextVideo,
      loadPrevVideo,
      toggleFavorite,
      toggleDislike,
      generateNewRandomList,
      close,
      removeFileExtension,
      handleVideoEnded,
      formatTime
    }
  }
}
</script>

<style scoped>
.modal-player-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: #000;
  z-index: 10000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.video-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
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
  margin-bottom: 4px;
  word-break: break-all;
}

.video-counter {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.8);
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
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
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.close-button {
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

.right-action-bar {
  position: absolute;
  right: 16px;
  bottom: 120px;
  z-index: 20;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.action-button {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
}

.action-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.3s;
}

.action-button:hover .action-icon {
  background: rgba(0, 0, 0, 0.7);
}

.favorite-icon, .dislike-icon {
  width: 24px;
  height: 24px;
  transition: all 0.3s ease;
}

.favorite-icon.filled {
  color: #ff6b81;
}

.favorite-icon.outline {
  color: rgba(255, 255, 255, 0.8);
}

.dislike-icon.filled {
  color: #00ff00;
}

.dislike-icon.outline {
  color: rgba(255, 255, 255, 0.8);
}

.refresh-prompt {
  position: absolute;
  bottom: 100px;
  left: 0;
  right: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10;
}

.refresh-content {
  background: rgba(0, 0, 0, 0.8);
  padding: 16px 24px;
  border-radius: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.refresh-text {
  color: white;
  font-size: 14px;
  font-weight: 500;
}

.refresh-button {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 20px;
  padding: 8px 16px;
  color: white;
  font-size: 14px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
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

/* 进度条快进样式 */
.seek-bar-overlay {
  position: absolute;
  bottom: 100px;
  left: 0;
  right: 0;
  z-index: 25;
  background: rgba(0, 0, 0, 0.8);
  padding: 16px;
}

.seek-bar-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: center;
}

.seek-bar {
  width: 100%;
  height: 4px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 2px;
  position: relative;
  overflow: hidden;
}

.seek-progress {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  background: #ff6b81;
  border-radius: 2px;
  transition: width 0.1s ease;
}

.seek-time {
  display: flex;
  justify-content: space-between;
  width: 100%;
  color: white;
  font-size: 0.9rem;
}

.seek-duration {
  color: rgba(255, 255, 255, 0.7);
}

.seek-amount {
  color: #ff6b81;
  font-size: 1rem;
  font-weight: bold;
  margin-top: 4px;
}
</style>