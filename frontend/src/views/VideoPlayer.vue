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
                <path d="M19 15h-4v4h-2v-4H9l3.5-3.5L19 15zm-8-9h4V2h2v4h4l-3.5 3.5L11 6z"/>
              </svg>
              <svg v-else class="dislike-icon outline" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M19 15h-4v4h-2v-4H9l3.5-3.5L19 15zm-8-9h4V2h2v4h4l-3.5 3.5L11 6z"/>
              </svg>
            </div>
          </div>
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

    // 去除文件后缀名（带空值检查）
    const removeFileExtension = (filename) => {
      if (!filename) return ''
      return filename.replace(/\.[^/.]+$/, "")
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
      handleTouchEnd,
      setupVideoEventListeners,
      removeFileExtension,
      isFavorited,
      favoriteCount,
      toggleFavorite,
      isDisliked,
      dislikeCount,
      toggleDislike
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