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
                <path d="M12 12L12 18" stroke="white" stroke-width="2" stroke-linecap="round"/>
                <path d="M10 10L14 14" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
                <path d="M14 10L10 14" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
              <svg v-else class="dislike-icon outline" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
                <path d="M12 12L12 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                <path d="M10 10L14 14" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                <path d="M14 10L10 14" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
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
      </div>
    </transition>
    

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

    // 加载收藏列表
    const loadFavoritesList = async () => {
      if (!isFavoritesPage.value) return
      
      try {
        const savedUser = localStorage.getItem('currentUser')
        if (!savedUser) return
        
        const user = JSON.parse(savedUser)
        const baseUrl = getBaseUrl()
        const res = await fetch(`${baseUrl}/favorites?user_id=${user.id}`)
        
        if (res.ok) {
          const data = await res.json()
          favoritesList.value = data || [] // 直接使用返回的数组，不是data.favorites
        }
      } catch (error) {
        console.error('加载收藏列表失败:', error)
      }
    }

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
        
        // 如果在收藏页面，按收藏列表顺序设置上下视频
        if (isFavoritesPage.value) {
          await loadFavoritesList()
          const index = favoritesList.value.findIndex(fav => fav.id === parseInt(id))
          currentFavoritesIndex.value = index
          
          if (index !== -1) {
            // 设置下一个视频ID
            if (index < favoritesList.value.length - 1) {
              nextVideoId.value = favoritesList.value[index + 1].id
            } else {
              nextVideoId.value = null
            }
            
            // 设置上一个视频ID
            if (index > 0) {
              prevVideoId.value = favoritesList.value[index - 1].id
            } else {
              prevVideoId.value = null
            }
          }
        } else if (isPlaylistPage.value) {
          // 根据播放列表类型获取上下视频
          await loadPlaylistNavigation(id)
        } else {
          // 普通页面按所有视频顺序设置
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
        }
      } catch (error) {
        console.error('获取视频信息失败:', error)
      }
    }

    // 根据播放列表类型获取导航视频
    const loadPlaylistNavigation = async (currentId) => {
      try {
        const baseUrl = getBaseUrl()
        let apiUrl = `${baseUrl}/videos?page=1&per_page=100` // 获取足够多的视频用于导航
        
        if (playlistType.value === 'random') {
          apiUrl += `&random=true&seed=${playlistSeed.value}`
        }
        
        const res = await fetch(apiUrl)
        if (!res.ok) throw new Error(`HTTP错误! 状态码: ${res.status}`)
        
        const data = await res.json()
        if (data.items && data.items.length > 0) {
          const videoIds = data.items.map(v => v.id)
          const currentIndex = videoIds.indexOf(parseInt(currentId))
          
          if (currentIndex !== -1) {
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
      } catch (error) {
        console.error('获取播放列表导航失败:', error)
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
        router.push({ 
          path: '/', 
          query: { 
            playlistType: playlistType.value,
            ...queryParams
          } 
        })
      } else {
        // 默认返回到首页（最新列表）
        router.push('/')
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
        
        setTimeout(() => {
          isTransitioning.value = false
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

    const getBaseUrl = () => {
      return import.meta.env.DEV 
        ? '/api' 
        : `${window.location.protocol}//${window.location.hostname}:5003/api`
    }

    // 检查收藏状态
    const checkFavoriteStatus = async () => {
      const savedUser = localStorage.getItem('currentUser')
      if (!savedUser) return
      
      currentUser.value = JSON.parse(savedUser)
      const userId = currentUser.value.id
      const videoId = route.params.id

      try {
        const baseUrl = getBaseUrl()
        const res = await fetch(`${baseUrl}/favorites/check?user_id=${userId}&video_id=${videoId}`)
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
      
      currentUser.value = JSON.parse(savedUser)
      const userId = currentUser.value.id
      const videoId = route.params.id

      try {
        const baseUrl = getBaseUrl()
        const res = await fetch(`${baseUrl}/dislikes/check?user_id=${userId}&video_id=${videoId}`)
        if (res.ok) {
          const data = await res.json()
          isDisliked.value = data.is_disliked
        }
      } catch (error) {
        console.error('检查讨厌状态失败:', error)
      }
    }

    // 切换收藏状态
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
        const baseUrl = getBaseUrl()
        
        if (isFavorited.value) {
          // 取消收藏
          const res = await fetch(`${baseUrl}/favorites?user_id=${userId}&video_id=${videoId}`, {
            method: 'DELETE'
          })
          if (res.ok) {
            isFavorited.value = false
            favoriteCount.value = Math.max(0, favoriteCount.value - 1)
          }
        } else {
          // 添加收藏
          const res = await fetch(`${baseUrl}/favorites`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              user_id: userId,
              video_id: videoId
            })
          })
          if (res.ok) {
            isFavorited.value = true
            favoriteCount.value += 1
          }
        }
      } catch (error) {
        console.error('收藏操作失败:', error)
      }
    }

    // 切换讨厌状态
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
        const baseUrl = getBaseUrl()
        
        if (isDisliked.value) {
          // 取消讨厌
          const res = await fetch(`${baseUrl}/dislikes?user_id=${userId}&video_id=${videoId}`, {
            method: 'DELETE'
          })
          if (res.ok) {
            isDisliked.value = false
            dislikeCount.value = Math.max(0, dislikeCount.value - 1)
          }
        } else {
          // 添加讨厌
          const res = await fetch(`${baseUrl}/dislikes`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              user_id: userId,
              video_id: videoId
            })
          })
          if (res.ok) {
            isDisliked.value = true
            dislikeCount.value += 1
          }
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
      formatTime
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
  color: #ff4757;
  filter: drop-shadow(0 2px 4px rgba(255, 71, 87, 0.3));
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
</style>