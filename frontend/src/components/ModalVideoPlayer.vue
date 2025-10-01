<template>
  <transition name="modal">
    <div v-if="visible" class="modal-player-container">
      
      <!-- 使用Vant Swipe组件实现垂直滑动切换视频 -->
      <van-swipe 
        ref="swipeRef"
        :vertical="true"
        :loop="false" 
        :touchable="true"
        :initial-swipe="currentIndex"
        :prevent="false"
        :stop-propagation="false"
        @change="onSwipeChange"
        @touchstart="handleSwipeTouchStart"
        @touchmove="handleSwipeTouchMove"
        @touchend="handleSwipeTouchEnd"
        @click="handleSwipeClick"
        class="swipe-container"
      >
        <van-swipe-item 
          v-for="(video, index) in playlistVideos" 
          :key="video.id"
          class="swipe-item"
        >
          <!-- 视频播放区域 - 只渲染当前播放的视频 -->
          <div class="video-wrapper">
            <video 
              v-if="index === currentIndex"
              :ref="el => videoRefs[index] = el"
              :src="getVideoUrl(video)"
              class="video-element"
              playsinline
              webkit-playsinline
              x5-playsinline
              autoplay
              @loadstart="handleVideoLoadStart"
              @loadedmetadata="handleVideoLoadedMetadata"
              @canplay="handleVideoCanPlay"
              @play="handleVideoPlay"
              @pause="handleVideoPause"
              @ended="handleVideoEnded"
              @timeupdate="handleTimeUpdate"
            ></video>
            
            <!-- 视频信息 -->
            <div class="video-info">
              <div class="video-title">{{ video.filename ? removeFileExtension(video.filename) : '' }}</div>
              <div class="video-counter" v-if="currentIndex !== -1 && totalVideos > 0">
                {{ index + 1 }} / {{ totalVideos }}
              </div>
            </div>
            
            <!-- 加载指示器 -->
            <div v-if="isLoading && index === currentIndex" class="loading-indicator">
              <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <path d="M12 6v6l4 2"></path>
              </svg>
            </div>
            
            <!-- 播放按钮 -->
            <div v-if="!isPlaying && !isLoading && index === currentIndex" class="play-button" @click.stop="playVideo">
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
            <div v-if="showSeekBar && index === currentIndex" class="seek-bar-overlay">
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
            <div v-if="playlistType === 'random' && showRefreshPrompt && index === currentIndex" class="refresh-prompt">
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
        </van-swipe-item>
      </van-swipe>
    </div>
  </transition>
</template>

<script>
import { ref, watch, nextTick, onMounted, toRefs } from 'vue'
import { Swipe, SwipeItem } from 'vant'

export default {
  name: 'ModalVideoPlayer',
  components: {
    [Swipe.name]: Swipe,
    [SwipeItem.name]: SwipeItem
  },
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
    // 使用toRefs保持响应性
    const { visible, video, playlistType, playlistSeed, playlistVideos, currentIndex, fromPage } = toRefs(props)
    const videoRefs = ref([]) // 修复：添加videoRefs变量定义
    const swipeRef = ref(null)
    const isPlaying = ref(false)
    const isLoading = ref(true)
    const touchStartX = ref(0)
    const touchStartY = ref(0)
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
    const totalVideos = ref(0)
    const isTransitioning = ref(false)
    
    // 获取当前视频的引用
    const getCurrentVideoRef = () => {
      if (currentIndex.value >= 0 && currentIndex.value < videoRefs.value.length) {
        return videoRefs.value[currentIndex.value]
      }
      return null
    }
    
    // 移除重复定义的响应式变量
    
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
    
    // 获取视频URL
    const getVideoUrl = (video) => {
      return `${getBaseUrl()}/videos/file/${encodeURIComponent(video.filename)}`
    }
    
    // 初始化播放器
    const initPlayer = async () => {
      if (!video.value || !video.value.id) return
      
      totalVideos.value = playlistVideos.value.length
      // 安全初始化videoRefs数组
      if (!videoRefs.value) {
        videoRefs.value = []
      }
      // 确保数组长度足够
      if (videoRefs.value.length < playlistVideos.value.length) {
        videoRefs.value.length = playlistVideos.value.length
      }
      
      console.log('模态框播放器初始化:', {
        video: video.value,
        index: currentIndex.value,
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
      let videoRef = getCurrentVideoRef()
      if (!videoRef) {
        console.log('videoRef为null，等待视频元素创建...')
        // 等待一段时间后重试
        await new Promise(resolve => setTimeout(resolve, 100))
        videoRef = getCurrentVideoRef()
        if (!videoRef) {
          console.log('videoRef仍然为null，无法播放')
          return false
        }
      }
      
      console.log('开始播放视频')
      
      try {
        const playPromise = videoRef.play()
        
        // 处理播放Promise
        await playPromise.catch(async (error) => {
          console.log('第一次播放失败，尝试延迟播放:', error)
          // 延迟后重试播放
          await new Promise(resolve => setTimeout(resolve, 500))
          const retryVideoRef = getCurrentVideoRef()
          if (retryVideoRef) {
            return retryVideoRef.play()
          }
          throw error
        })
        
        console.log('播放命令已发送，立即更新播放状态...')
        
        // 简化播放状态管理：直接设置播放状态为true
        isPlaying.value = true
        console.log('播放状态已设置为true')
        
        return true
      } catch (error) {
        console.error('视频播放失败:', error)
        isPlaying.value = false
        return false
      }
    }
    
    // 暂停视频
    const pauseVideo = () => {
      const videoRef = getCurrentVideoRef()
      if (!videoRef) {
        console.log('videoRef为null，无法暂停')
        return
      }
      videoRef.pause()
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
    
    // Swipe切换事件处理
    const onSwipeChange = (index) => {
      console.log('=== Swipe切换事件 ===', {
        fromIndex: currentIndex.value,
        toIndex: index,
        totalVideos: playlistVideos.value.length
      })
      
      if (index === currentIndex.value) return
      
      // 通知父组件视频切换
      emit('video-change', {
        video: playlistVideos.value[index],
        index: index
      })
      
      // 播放新视频
      playVideo()
      
      // 检查新视频的用户行为状态
      checkFavoriteStatus()
      checkDislikeStatus()
    }

    // 视频加载开始
    const handleVideoLoadStart = () => {
      console.log('=== 视频加载开始 ===')
      isLoading.value = true
    }

    // 视频元数据加载完成
    const handleVideoLoadedMetadata = () => {
      console.log('=== 视频元数据加载完成 ===')
    }

    // 视频可以播放
    const handleVideoCanPlay = () => {
      console.log('=== 视频可以播放 ===')
      isLoading.value = false
    }

    // 视频播放进度更新
    const handleTimeUpdate = () => {
      const videoRef = getCurrentVideoRef()
      // 确保加载状态正确更新
      if (videoRef && videoRef.readyState >= 3) {
        isLoading.value = false
      }
      
      // 实时更新播放状态
      if (videoRef) {
        isPlaying.value = !videoRef.paused
      }
    }

    // 视频播放开始
    const handleVideoPlay = () => {
      console.log('=== 视频开始播放 ===')
      isPlaying.value = true
    }

    // 视频暂停
    const handleVideoPause = () => {
      console.log('=== 视频暂停 ===')
      isPlaying.value = false
    }

    // 视频结束处理
    const handleVideoEnded = () => {
      console.log('=== 视频播放完成，自动切换到下一个视频 ===')
      isPlaying.value = false
      
      // 如果还有下一个视频，自动切换
      if (currentIndex.value < playlistVideos.value.length - 1) {
        // 使用Swipe组件切换到下一个视频
        if (swipeRef.value) {
          swipeRef.value.next()
        }
      }
    }
    

    
    // Swipe组件触摸事件处理 - 垂直滑动切换视频，水平滑动快进快退
    const handleSwipeTouchStart = (event) => {
      // 记录触摸起始位置
      touchStartX.value = event.touches[0].clientX
      touchStartY.value = event.touches[0].clientY
      
      console.log('=== Swipe触摸开始 ===', {
        startX: touchStartX.value,
        startY: touchStartY.value
      })
      
      // 开始长按计时器（2倍速播放）
      longPressTimer.value = setTimeout(() => {
        const videoRef = getCurrentVideoRef()
        if (videoRef && !isLongPressing.value) {
          isLongPressing.value = true
          originalPlaybackRate.value = videoRef.playbackRate
          videoRef.playbackRate = 2.0 // 2倍速播放
          console.log('长按2倍速播放激活')
        }
      }, 500) // 长按500ms触发
      
      // 初始化进度条快进状态
      const videoRef = getCurrentVideoRef()
      if (videoRef) {
        seekStartTime.value = videoRef.currentTime
        seekCurrentTime.value = seekStartTime.value
        videoDuration.value = videoRef.duration || 0
        isSeeking.value = false
      }
    }
    
    const handleSwipeTouchMove = (event) => {
      if (!event.touches.length) return
      
      const touchCurrentX = event.touches[0].clientX
      const touchCurrentY = event.touches[0].clientY
      const deltaX = touchCurrentX - touchStartX.value
      const deltaY = touchCurrentY - touchStartY.value
      
      console.log('=== Swipe触摸移动 ===', {
        currentX: touchCurrentX,
        currentY: touchCurrentY,
        deltaX: deltaX,
        deltaY: deltaY,
        isSeeking: isSeeking.value
      })
      
      // 只处理水平滑动（快进快退），垂直滑动由Swipe组件处理
      if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 20) {
        const videoRef = getCurrentVideoRef()
        if (!videoRef) return
        
        // 取消长按计时器
        if (longPressTimer.value) {
          clearTimeout(longPressTimer.value)
          longPressTimer.value = null
          console.log('取消长按计时器')
        }
        
        // 停止长按2倍速
        if (isLongPressing.value) {
          isLongPressing.value = false
          videoRef.playbackRate = originalPlaybackRate.value
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
    
    const handleSwipeTouchEnd = (event) => {
      console.log('=== Swipe触摸结束 ===', {
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
        const videoRef = getCurrentVideoRef()
        if (videoRef) {
          videoRef.playbackRate = originalPlaybackRate.value
        }
        console.log('恢复长按2倍速')
      }
      
      // 处理进度条快进
      if (isSeeking.value) {
        const videoRef = getCurrentVideoRef()
        if (videoRef) {
          console.log('应用进度条快进:', {
            seekCurrentTime: seekCurrentTime.value,
            seekAmount: seekAmount.value
          })
          
          // 应用快进
          videoRef.currentTime = seekCurrentTime.value
          showSeekBar.value = false
          isSeeking.value = false
          
          // 如果视频暂停，播放视频
          if (videoRef.paused) {
            console.log('视频暂停，重新播放')
            playVideo()
          }
        }
      }
    }
    
    const handleSwipeClick = (event) => {
      // 阻止事件冒泡
      event.stopPropagation()
      console.log('=== Swipe点击事件 ===')
      
      // 切换播放状态
      togglePlay()
    }
    

    
    // 检查收藏状态
    const checkFavoriteStatus = async () => {
      const savedUser = localStorage.getItem('currentUser')
      if (!savedUser) return
      
      const user = JSON.parse(savedUser)
      const video = playlistVideos.value[currentIndex.value]
      if (!video) return
      
      const videoId = video.id
      
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
      const video = playlistVideos.value[currentIndex.value]
      if (!video) return
      
      const videoId = video.id
      
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
      const video = playlistVideos.value[currentIndex.value]
      if (!video) return
      
      const videoId = video.id
      
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
      const video = playlistVideos.value[currentIndex.value]
      if (!video) return
      
      const videoId = video.id
      
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
    watch(() => visible.value, (newVal) => {
      if (newVal) {
        initPlayer()
      }
    })
    
    // 监听视频变化
    watch(() => video.value, (newVideo) => {
      if (newVideo && visible.value) {
        console.log('视频变化监听:', newVideo)
        checkFavoriteStatus()
        checkDislikeStatus()
        playVideo()
      }
    })
    
    // 监听播放列表变化
    watch(() => playlistVideos.value, (newVideos) => {
      if (newVideos && visible.value) {
        totalVideos.value = newVideos.length
        // 安全初始化videoRefs数组
        if (!videoRefs.value) {
          videoRefs.value = []
        }
        // 确保数组长度足够
        if (videoRefs.value.length < newVideos.length) {
          videoRefs.value.length = newVideos.length
        }
        console.log('播放列表变化，总视频数:', totalVideos.value, 'videoRefs长度:', videoRefs.value.length)
      }
    })
    
    // 监听当前索引变化
    watch(() => currentIndex.value, (newIndex) => {
      if (newIndex !== -1 && visible.value) {
        console.log('当前索引变化:', newIndex)
      }
    })
    
    // 监听模态框显示状态变化和播放列表数据变化
    watch([() => visible.value, () => playlistVideos.value], ([newVisible, newVideos], [oldVisible, oldVideos]) => {
      console.log('模态框和播放列表变化监听:', {
        visible: newVisible,
        playlistLength: newVideos ? newVideos.length : 0,
        oldVisible: oldVisible,
        oldPlaylistLength: oldVideos ? oldVideos.length : 0
      })
      
      if (newVisible && newVideos && newVideos.length > 0) {
        console.log('模态框已显示且播放列表数据就绪，初始化播放器')
        // 使用nextTick确保DOM已渲染
        nextTick(() => {
          initPlayer()
        })
      }
    }, { immediate: true })
    
    // 额外的数据就绪检查：组件创建后立即检查
    onMounted(() => {
      console.log('ModalVideoPlayer组件已挂载，检查数据状态:', {
        visible: visible.value,
        playlistLength: playlistVideos.value ? playlistVideos.value.length : 0,
        currentIndex: currentIndex.value
      })
      
      if (visible.value && playlistVideos.value && playlistVideos.value.length > 0) {
        console.log('组件挂载时数据已就绪，初始化播放器')
        nextTick(() => {
          initPlayer()
        })
      }
    })
    
    return {
      videoRefs,
      swipeRef,
      isPlaying,
      isLoading,
      totalVideos,
      isFavorited,
      isDisliked,
      showRefreshPrompt,
      showSeekBar,
      seekCurrentTime,
      videoDuration,
      seekProgress,
      seekAmount,
      isTransitioning,
      playVideo,
      pauseVideo,
      togglePlay,
      handleSwipeTouchStart,
      handleSwipeTouchMove,
      handleSwipeTouchEnd,
      handleSwipeClick,
      onSwipeChange,
      toggleFavorite,
      toggleDislike,
      generateNewRandomList,
      close,
      removeFileExtension,
      getVideoUrl,
      handleVideoEnded,
      formatTime,
      handleVideoLoadStart,
      handleVideoLoadedMetadata,
      handleVideoCanPlay,
      handleVideoPlay,
      handleVideoPause,
      handleTimeUpdate
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
}

.swipe-container {
  width: 100%;
  height: 100%;
}

.swipe-item {
  width: 100%;
  height: 100%;
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

.swipe-container {
  width: 100%;
  height: 100%;
}

.swipe-item {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.video-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
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