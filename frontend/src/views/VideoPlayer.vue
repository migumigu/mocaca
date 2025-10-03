<template>
  <div 
    class="player-container"
    @touchstart="handleTouchStart"
    @touchmove="handleTouchMove"
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
        
        <!-- 播放按钮，仅在视频暂停且不在加载时显示 -->
        <div v-if="!isPlaying && !isLoading" class="play-button" @click.stop="playVideo">
          <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="white">
            <path d="M8 5v14l11-7z"/>
          </svg>
        </div>

        <!-- 抖音风格右侧操作栏 -->
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
            
        <!-- 发现页面底部刷新按钮 -->
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
              <span>{{ formatTime(seekCurrentTime) }}</span>
              <span class="seek-duration">{{ formatTime(videoDuration) }}</span>
            </div>
            <div class="seek-amount">
              <span v-if="seekAmount > 0">+{{ seekAmount }}秒</span>
              <span v-else-if="seekAmount < 0">{{ seekAmount }}秒</span>
            </div>
          </div>
        </div>
      </div>
    </transition>
    

  </div>
</template>

<script>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { videoApi, favoriteApi, dislikeApi } from '../services/api.js'

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
    const touchStartX = ref(0)
    const touchEndX = ref(0)
    const touchCurrentX = ref(0)
    const swipeThreshold = 100 // 滑动阈值，超过这个值才触发切换
    
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

    // 播放列表类型和种子
    const playlistType = ref(route.query.playlistType || 'latest')
    const playlistSeed = ref(route.query.seed || null)
    
    // 卡片计数相关状态
    const currentVideoIndex = ref(-1)
    const totalVideos = ref(0)
    const playlistVideos = ref([])
    
    // 边界检测状态
    const showRefreshPrompt = ref(false)

    // 检查是否在收藏页面
    const isFavoritesPage = computed(() => {
      return route.path.includes('/favorites') || route.query.from === 'favorites'
    })

    // 检查是否从发现页面进入
    const isFromDirectoryPage = computed(() => {
      return route.query.from === 'directory'
    })

    // 检查是否在特定播放列表页面
    const isPlaylistPage = computed(() => {
      return playlistType.value === 'latest' || playlistType.value === 'random'
    })

    // 收藏列表相关状态
    const favoritesList = ref([])
    const currentFavoritesIndex = ref(-1)

    // 加载收藏列表导航信息（使用统一API服务）
    const loadFavoritesNavigation = async (videoId) => {
      if (!isFavoritesPage.value) return
      
      try {
        const savedUser = localStorage.getItem('currentUser')
        if (!savedUser) return
        
        const user = JSON.parse(savedUser)
        const data = await favoriteApi.getFavoriteNavigation(videoId, user.id)
        
        // 设置导航信息
        nextVideoId.value = data.next_video_id
        prevVideoId.value = data.prev_video_id
        currentVideoIndex.value = data.current_index
        totalVideos.value = data.total_favorites
      } catch (error) {
        console.error('加载收藏列表导航失败:', error)
      }
    }

    // 获取当前视频信息（使用统一API服务）
    const fetchVideoInfo = async (id) => {
      try {
        const data = await videoApi.getVideo(id)
        currentVideo.value = {
          ...data,
          url: videoApi.getVideoFileUrl(data.filename)
        }
        
        // 如果在收藏页面，使用统一API服务获取上下视频
        if (isFavoritesPage.value) {
          await loadFavoritesNavigation(id)
        } else if (isPlaylistPage.value) {
          // 根据播放列表类型获取上下视频
          await loadPlaylistNavigation(id)
        } else {
          // 普通页面按所有视频顺序设置
          nextVideoId.value = data.next_id
          
          // 获取前一个视频ID（使用统一API服务）
          try {
            const prevData = await videoApi.getPrevVideo(id)
            prevVideoId.value = prevData.id
          } catch (error) {
            console.error('获取前一个视频失败:', error)
            prevVideoId.value = null
          }
        }
      } catch (error) {
        console.error('获取视频信息失败:', error)
      }
    }

    // 根据播放列表类型获取导航视频（使用统一API服务）
    const loadPlaylistNavigation = async (currentId) => {
      try {
        if (playlistType.value === 'random') {
          // 发现页面（随机列表）：固定加载200个视频
          const data = await videoApi.getVideos(1, 200, true, playlistSeed.value || undefined)
          
          if (data.items && data.items.length > 0) {
            playlistVideos.value = data.items
            const videoIds = data.items.map(v => v.id)
            const currentIndex = videoIds.indexOf(parseInt(currentId))
            
            if (currentIndex !== -1) {
              // 设置卡片计数（固定为200个视频）
              currentVideoIndex.value = currentIndex
              totalVideos.value = 200 // 固定200个视频
              
              // 设置下一个视频ID
              if (currentIndex < videoIds.length - 1) {
                nextVideoId.value = videoIds[currentIndex + 1]
              } else {
                nextVideoId.value = null
              }
              
              // 设置上一个视频ID
              if (currentIndex > 0) {
                prevVideoId.value = videoIds[currentIndex - 1]
              } else {
                prevVideoId.value = null
              }
            }
          }
        } else {
          // 最新页面：使用统一API服务
          const [nextData, prevData] = await Promise.all([
            videoApi.getVideo(currentId),
            videoApi.getPrevVideo(currentId)
          ])
          
          nextVideoId.value = nextData.next_id
          prevVideoId.value = prevData.id
          
          // 获取部分视频用于显示卡片计数
          const data = await videoApi.getVideos(1, 50)
          if (data.items && data.items.length > 0) {
            playlistVideos.value = data.items
            const videoIds = data.items.map(v => v.id)
            const currentIndex = videoIds.indexOf(parseInt(currentId))
            
            if (currentIndex !== -1) {
              currentVideoIndex.value = currentIndex
              totalVideos.value = data.total
            }
          }
        }
      } catch (error) {
        console.error('获取播放列表导航失败:', error)
      }
    }

    // 生成新的随机列表
    const generateNewRandomList = () => {
      // 生成新的随机种子
      const newSeed = Math.floor(Math.random() * 1000000)
      playlistSeed.value = newSeed
      
      // 重新加载当前视频，但使用新的随机种子
      router.replace({
        query: {
          ...route.query,
          seed: newSeed
        }
      })
      
      // 重新加载导航数据
      loadPlaylistNavigation(props.id)
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
      
      // 阻止视频元素的上下文菜单（长按下载菜单）
      videoRef.value.addEventListener('contextmenu', (event) => {
        event.preventDefault()
        return false
      })
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
      // 根据来源页面决定返回位置
      if (isFavoritesPage.value) {
        router.push('/favorites')
      } else if (isFromDirectoryPage.value) {
        // 从发现页面进入，返回到发现页面
        router.push('/directory')
      } else if (isPlaylistPage.value) {
        // 从播放列表进入，返回到相应的播放列表
        const queryParams = {}
        if (playlistSeed.value) {
          queryParams.seed = playlistSeed.value
        }
        
        // 添加卡片索引恢复参数
        const cardIndex = sessionStorage.getItem('videoListCardIndex')
        if (cardIndex) {
          queryParams.cardIndex = cardIndex
        }
        
        router.push({ 
          path: '/', 
          query: { 
            playlistType: playlistType.value,
            ...queryParams
          } 
        })
      } else {
        // 默认返回到首页（最新列表）
        const cardIndex = sessionStorage.getItem('videoListCardIndex')
        const queryParams = cardIndex ? { cardIndex } : {}
        router.push({ 
          path: '/', 
          query: queryParams
        })
      }
    }

    // 处理触摸开始事件
    const handleTouchStart = (event) => {
      touchStartY.value = event.touches[0].clientY
      touchStartX.value = event.touches[0].clientX
      touchCurrentX.value = touchStartX.value
      
      // 开始长按计时器（2倍速播放）
      longPressTimer.value = setTimeout(() => {
        if (videoRef.value && !isLongPressing.value) {
          isLongPressing.value = true
          originalPlaybackRate.value = videoRef.value.playbackRate
          videoRef.value.playbackRate = 2.0 // 2倍速播放
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

    // 处理触摸移动事件
    const handleTouchMove = (event) => {
      if (!event.touches.length) return
      
      touchCurrentX.value = event.touches[0].clientX
      const deltaX = touchCurrentX.value - touchStartX.value
      
      // 水平滑动超过阈值，开始进度条快进
      if (Math.abs(deltaX) > 20 && videoRef.value) {
        // 取消长按计时器
        if (longPressTimer.value) {
          clearTimeout(longPressTimer.value)
          longPressTimer.value = null
        }
        
        // 停止长按2倍速
        if (isLongPressing.value) {
          isLongPressing.value = false
          videoRef.value.playbackRate = originalPlaybackRate.value
        }
        
        // 开始进度条快进
        if (!isSeeking.value) {
          isSeeking.value = true
          showSeekBar.value = true
        }
        
        // 计算快进量（每10像素对应1秒）
        const seekSeconds = Math.round(deltaX / 10)
        seekAmount.value = seekSeconds
        seekCurrentTime.value = Math.max(0, Math.min(videoDuration.value, seekStartTime.value + seekSeconds))
        seekProgress.value = (seekCurrentTime.value / videoDuration.value) * 100
      }
    }

    // 处理触摸结束事件
    const handleTouchEnd = (event) => {
      // 取消长按计时器
      if (longPressTimer.value) {
        clearTimeout(longPressTimer.value)
        longPressTimer.value = null
      }
      
      // 恢复长按2倍速
      if (isLongPressing.value) {
        isLongPressing.value = false
        if (videoRef.value) {
          videoRef.value.playbackRate = originalPlaybackRate.value
        }
      }
      
      // 处理进度条快进
      if (isSeeking.value && videoRef.value) {
        // 应用快进
        videoRef.value.currentTime = seekCurrentTime.value
        showSeekBar.value = false
        isSeeking.value = false
        
        // 如果视频暂停，播放视频
        if (videoRef.value.paused) {
          playVideo()
        }
      }
      
      // 处理垂直滑动切换视频
      touchEndY.value = event.changedTouches[0].clientY
      const swipeDistance = touchEndY.value - touchStartY.value
      
      // 判断滑动方向和距离（只在没有进行进度条快进时）
      if (!isSeeking.value && Math.abs(swipeDistance) > swipeThreshold) {
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
        
        // 更新卡片索引（当前索引+1）
        if (currentVideoIndex.value !== -1 && currentVideoIndex.value < totalVideos.value - 1) {
          const newCardIndex = currentVideoIndex.value + 1
          sessionStorage.setItem('videoListCardIndex', newCardIndex.toString())
          console.log(`更新卡片索引: ${currentVideoIndex.value} -> ${newCardIndex}`)
        }
        
        // 边界检测：如果是发现页面随机列表且到达第200个视频，显示刷新提示
        if (playlistType.value === 'random' && currentVideoIndex.value === 199) {
          showRefreshPrompt.value = true
          // 延迟隐藏过渡效果，确保用户看到提示
          setTimeout(() => {
            showRefreshPrompt.value = false
          }, 3000)
        }
        
        // 保持当前页面上下文
        const queryParams = {}
        if (isFavoritesPage.value) {
          queryParams.from = 'favorites'
        } else if (isPlaylistPage.value) {
          queryParams.playlistType = playlistType.value
          if (playlistSeed.value) {
            queryParams.seed = playlistSeed.value
          }
        }
        
        router.push({ 
          name: 'Player', 
          params: { id: nextVideoId.value }, 
          query: queryParams 
        })
        
        // 切换到新视频后自动播放
        setTimeout(() => {
          isTransitioning.value = false
          playVideo()
        }, 500) // 动画过渡时间
      }
    }

    // 加载前一个视频
    const loadPrevVideo = () => {
      if (prevVideoId.value && !isTransitioning.value) {
        isTransitioning.value = true
        // 设置滑动方向 - 向下滑动加载前一个（新视频从下方进入）
        document.documentElement.style.setProperty('--slide-direction', '-100%')
        
        // 更新卡片索引（当前索引-1）
        if (currentVideoIndex.value !== -1 && currentVideoIndex.value > 0) {
          const newCardIndex = currentVideoIndex.value - 1
          sessionStorage.setItem('videoListCardIndex', newCardIndex.toString())
          console.log(`更新卡片索引: ${currentVideoIndex.value} -> ${newCardIndex}`)
        }
        
        // 保持当前页面上下文
        const queryParams = {}
        if (isFavoritesPage.value) {
          queryParams.from = 'favorites'
        } else if (isPlaylistPage.value) {
          queryParams.playlistType = playlistType.value
          if (playlistSeed.value) {
            queryParams.seed = playlistSeed.value
          }
        }
        
        router.push({ 
          name: 'Player', 
          params: { id: prevVideoId.value }, 
          query: queryParams 
        })
        
        // 切换到新视频后自动播放
        setTimeout(() => {
          isTransitioning.value = false
          playVideo()
        }, 500) // 动画过渡时间
      }
    }

    // 去除文件后缀名和路径，只显示文件名（带空值检查）
    const removeFileExtension = (filename) => {
      if (!filename) return ''
      // 先提取文件名（去掉路径）
      const baseName = filename.split('/').pop().split('\\').pop()
      // 再去掉文件扩展名
      return baseName.replace(/\.[^/.]+$/, "")
    }

    // 格式化时间显示（秒 → 分:秒）
    const formatTime = (seconds) => {
      if (!seconds || isNaN(seconds)) return '00:00'
      const mins = Math.floor(seconds / 60)
      const secs = Math.floor(seconds % 60)
      return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
    }

    // 收藏功能相关状态
    const isFavorited = ref(false)
    const favoriteCount = ref(0)
    const currentUser = ref(null)

    // 讨厌功能相关状态
    const isDisliked = ref(false)
    const dislikeCount = ref(0)



    // 检查收藏状态（使用统一API服务）
    const checkFavoriteStatus = async () => {
      const savedUser = localStorage.getItem('currentUser')
      if (!savedUser) return
      
      currentUser.value = JSON.parse(savedUser)
      const userId = currentUser.value.id
      const videoId = route.params.id

      try {
        const data = await favoriteApi.checkFavorite(userId, videoId)
        isFavorited.value = data.is_favorited
      } catch (error) {
        console.error('检查收藏状态失败:', error)
      }
    }

    // 检查讨厌状态（使用统一API服务）
    const checkDislikeStatus = async () => {
      const savedUser = localStorage.getItem('currentUser')
      if (!savedUser) return
      
      currentUser.value = JSON.parse(savedUser)
      const userId = currentUser.value.id
      const videoId = route.params.id

      try {
        const data = await dislikeApi.checkDislike(userId, videoId)
        isDisliked.value = data.is_disliked
      } catch (error) {
        console.error('检查讨厌状态失败:', error)
      }
    }

    // 切换收藏状态（使用统一API服务）
    const toggleFavorite = async () => {
      const savedUser = localStorage.getItem('currentUser')
      if (!savedUser) {
        alert('请先登录后再收藏')
        return
      }

      currentUser.value = JSON.parse(savedUser)
      const userId = currentUser.value.id
      const videoId = route.params.id

      try {
        if (isFavorited.value) {
          // 取消收藏
          await favoriteApi.removeFavorite(userId, videoId)
          isFavorited.value = false
          favoriteCount.value = Math.max(0, favoriteCount.value - 1)
        } else {
          // 添加收藏
          await favoriteApi.addFavorite(userId, videoId)
          isFavorited.value = true
          favoriteCount.value += 1
        }
      } catch (error) {
        console.error('收藏操作失败:', error)
      }
    }

    // 切换讨厌状态（使用统一API服务）
    const toggleDislike = async () => {
      const savedUser = localStorage.getItem('currentUser')
      if (!savedUser) {
        alert('请先登录后再操作')
        return
      }

      currentUser.value = JSON.parse(savedUser)
      const userId = currentUser.value.id
      const videoId = route.params.id

      try {
        if (isDisliked.value) {
          // 取消讨厌
          await dislikeApi.removeDislike(userId, videoId)
          isDisliked.value = false
          dislikeCount.value = Math.max(0, dislikeCount.value - 1)
        } else {
          // 添加讨厌
          await dislikeApi.addDislike(userId, videoId)
          isDisliked.value = true
          dislikeCount.value += 1
        }
      } catch (error) {
        console.error('讨厌操作失败:', error)
      }
    }

    // 页面加载时检查收藏和讨厌状态
    onMounted(() => {
      checkFavoriteStatus()
      checkDislikeStatus()
    })

    // 监听视频ID变化，更新收藏和讨厌状态
    watch(() => route.params.id, (newId) => {
      if (newId) {
        checkFavoriteStatus()
        checkDislikeStatus()
      }
    })

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
      handleTouchMove,
      handleTouchEnd,
      setupVideoEventListeners,
      removeFileExtension,
      isFavorited,
      favoriteCount,
      toggleFavorite,
      isDisliked,
      dislikeCount,
      toggleDislike,
      // 新添加的状态和函数
      showSeekBar,
      seekCurrentTime,
      seekAmount,
      seekProgress,
      videoDuration,
      formatTime,
      // 卡片计数相关状态
      currentVideoIndex,
      totalVideos,
      // 播放列表相关状态
      playlistType,
      // 边界检测状态
      showRefreshPrompt
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

/* 右侧操作栏样式 */
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

.favorite-icon {
  width: 24px;
  height: 24px;
  transition: all 0.3s ease;
}

.favorite-icon.filled {
  color: #ff6b81;
  filter: drop-shadow(0 2px 4px rgba(255, 107, 129, 0.3));
}

.favorite-icon.outline {
  color: rgba(255, 255, 255, 0.8);
}

.action-button:hover .favorite-icon.outline {
  color: rgba(255, 255, 255, 1);
  transform: scale(1.1);
}

.action-button:hover .favorite-icon.filled {
  transform: scale(1.1);
  filter: drop-shadow(0 3px 6px rgba(255, 107, 129, 0.5));
}

/* 讨厌按钮样式 */
.dislike-icon {
  width: 24px;
  height: 24px;
  transition: all 0.3s ease;
}

.dislike-icon.filled {
  color: #00ff00;
  filter: drop-shadow(0 2px 4px rgba(0, 255, 0, 0.3));
}

.dislike-icon.outline {
  color: rgba(255, 255, 255, 0.8);
}

.action-button:hover .dislike-icon.outline {
  color: rgba(255, 255, 255, 1);
  transform: scale(1.1);
}

.action-button:hover .dislike-icon.filled {
  transform: scale(1.1);
  filter: drop-shadow(0 3px 6px rgba(255, 71, 87, 0.5));
}

.action-count {
  color: white;
  font-size: 0.9rem;
  margin-top: 4px;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
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

/* 发现页面刷新提示样式 */
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
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
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
  transition: all 0.3s ease;
}

.refresh-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.refresh-button:active {
  transform: translateY(0);
}
</style>