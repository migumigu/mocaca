<template>
  <div class="app-container">
    <div class="video-grid-container" ref="videoGrid" @scroll="handleScroll">
      <!-- 顶部子页面导航 -->
      <div class="sub-nav">
        <div class="sub-nav-item" :class="{ active: activeTab === 'latest' }" @click="switchTab('latest')">
          最新
        </div>
        <div class="sub-nav-item" :class="{ active: activeTab === 'random' }" @click="switchTab('random')">
          发现
        </div>
      </div>
      
      <div class="video-grid">
        <div 
          v-for="video in videos" 
          :key="video.id"
          class="video-card"
          :style="{ display: modalPlayerVisible ? 'none' : 'block' }"
          @click="openPlayer(video)"
        >
          <div class="video-thumbnail">
            <img 
              class="thumbnail-image"
              :src="getThumbnailUrl(video)"
              :alt="removeFileExtension(video.filename)"
              @load="handleThumbnailLoad(video.id)"
              @error="handleThumbnailError(video.id)"
            />
            <div class="video-title-overlay">
              {{ removeFileExtension(video.filename) }}
            </div>
          </div>
        </div>
        
        <div v-if="loading" class="loading-more">
          加载中...
        </div>
        <div v-if="!hasMore" class="no-more">
          已到底部
        </div>
      </div>
    </div>
    
    <!-- 底部导航栏 -->
    <div class="bottom-nav">
      <div class="nav-item active">
        <NavIcons name="home" />
        <span>首页</span>
      </div>
      <div class="nav-item" @click="$router.push('/directory')">
        <NavIcons name="folder" />
        <span>目录</span>
      </div>
      <div class="nav-item" @click="$router.push('/favorites')">
        <NavIcons name="favorite" />
        <span>收藏</span>
      </div>
      <div class="nav-item" @click="$router.push('/profile')">
        <NavIcons name="user" />
        <span>我</span>
      </div>
    </div>
    
    <!-- 模态框播放器 -->
    <ModalVideoPlayer
      :visible="modalPlayerVisible"
      :video="currentPlayingVideo"
      :playlist-type="activeTab"
      :playlist-seed="activeTab === 'random' ? randomSeed : null"
      :playlist-videos="videos"
      :current-index="currentPlayingIndex"
      :from-page="activeTab"
      @close="handleModalClose"
      @video-change="handleVideoChange"
      @list-refresh="handleListRefresh"
    />
  </div>
</template>

<script>
import { ref, onMounted, nextTick, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import NavIcons from '../components/icons/NavIcons.vue'
import ModalVideoPlayer from '../components/ModalVideoPlayer.vue'
import { videoApi } from '../services/api.js'

export default {
  components: {
    NavIcons,
    ModalVideoPlayer
  },
  setup() {
    const videos = ref([])
    const router = useRouter()
    const route = useRoute()
    const videoGrid = ref(null)
    const loading = ref(false)
    const hasMore = ref(true)
    const page = ref(1)
    const activeTab = ref('latest') // 'latest' 或 'random'
    const currentPlaylistType = ref('latest') // 当前播放列表类型
    const randomSeed = ref(Date.now()) // 随机种子，确保随机列表一致性
    
    // 缓存相关状态
    const cacheKey = ref('')
    const cachedData = ref(null)
    
    // 模态框播放器相关状态
    const modalPlayerVisible = ref(false)
    const currentPlayingVideo = ref(null)
    const currentPlayingIndex = ref(-1)
    
    // 缩略图URL缓存
    const thumbnailCache = ref({})
    

    
    // 生成缓存键
    const generateCacheKey = () => {
      const keyParts = [
        'videoList',
        currentPlaylistType.value,
        currentPlaylistType.value === 'random' ? randomSeed.value : 'latest'
      ]
      return keyParts.join(':')
    }

    // 保存缓存数据
    const saveCacheData = () => {
      const cacheData = {
        videos: videos.value,
        page: page.value,
        hasMore: hasMore.value,
        scrollPosition: videoGrid.value ? videoGrid.value.scrollTop : 0,
        timestamp: Date.now()
      }
      const key = generateCacheKey()
      sessionStorage.setItem(key, JSON.stringify(cacheData))
      console.log(`缓存数据已保存: ${key}, 视频数量: ${videos.value.length}`)
    }

    // 恢复缓存数据
    const restoreCacheData = () => {
      const key = generateCacheKey()
      const cached = sessionStorage.getItem(key)
      if (cached) {
        try {
          const cacheData = JSON.parse(cached)
          // 检查缓存是否过期（5分钟内有效）
          if (Date.now() - cacheData.timestamp < 5 * 60 * 1000) {
            // 发现页面随机列表：如果缓存数据超过200个视频，截断到200个
            if (activeTab.value === 'random' && cacheData.videos.length > 200) {
              cacheData.videos = cacheData.videos.slice(0, 200)
              cacheData.hasMore = false
              console.log(`发现页面随机列表缓存数据已截断: ${cacheData.videos.length}个视频`)
            }
            
            videos.value = cacheData.videos
            page.value = cacheData.page
            hasMore.value = cacheData.hasMore
            console.log(`缓存数据已恢复: ${key}, 视频数量: ${videos.value.length}`)
            return true
          } else {
            console.log(`缓存已过期: ${key}`)
            sessionStorage.removeItem(key)
          }
        } catch (error) {
          console.error('恢复缓存数据失败:', error)
        }
      }
      return false
    }

    const handleScroll = () => {
      const container = videoGrid.value
      if (container && container.scrollTop + container.clientHeight >= container.scrollHeight - 100) {
        loadVideos()
      }
    }

    const switchTab = (tab) => {
      if (activeTab.value === tab) return
      
      activeTab.value = tab
      currentPlaylistType.value = tab
      videos.value = []
      page.value = 1
      hasMore.value = true
      loading.value = false
      
      if (tab === 'random') {
        randomSeed.value = Date.now()
      }
      
      loadVideos()
    }

    onMounted(async () => {
      // 检查URL查询参数，设置正确的activeTab
      if (route.query.playlistType === 'random') {
        activeTab.value = 'random'
        currentPlaylistType.value = 'random'
        if (route.query.seed) {
          randomSeed.value = parseInt(route.query.seed)
        }
      }
      
      // 生成当前缓存键
      cacheKey.value = generateCacheKey()
      
      // 尝试从缓存恢复数据
      const hasCache = restoreCacheData()
      
      if (!hasCache) {
        // 如果没有缓存，需要加载数据
        const targetCardIndex = route.query.cardIndex ? parseInt(route.query.cardIndex) : -1
        
        // 计算需要加载的页数来包含目标卡片索引
        const videosPerPage = 20 // 每页20个视频
        let requiredPages = targetCardIndex >= 0 ? Math.ceil((targetCardIndex + 1) / videosPerPage) : 1
        
        // 发现页面随机列表限制：最多加载10页（200个视频）
        if (activeTab.value === 'random') {
          // 如果目标索引超过200，限制为最多200个视频
          if (targetCardIndex >= 200) {
            requiredPages = 10 // 最多10页，200个视频
            console.log(`发现页面随机列表：目标索引${targetCardIndex}超过200，限制为最多200个视频`)
          } else {
            requiredPages = Math.min(requiredPages, 10) // 最多10页，200个视频
          }
          console.log(`发现页面随机列表限制：最多加载${requiredPages}页（200个视频）`)
        }
        
        console.log(`目标卡片索引: ${targetCardIndex}, 需要加载页数: ${requiredPages}`)
        
        // 加载视频数据
        for (let i = 0; i < requiredPages; i++) {
          await loadVideos()
          if (!hasMore.value) break // 如果没有更多数据，停止加载
        }
      }
      
      // 数据加载完成后恢复滚动位置
      const targetCardIndex = route.query.cardIndex !== undefined ? parseInt(route.query.cardIndex) : 0
      
      // 发现页面随机列表：如果目标索引超过200，限制为199（最后一个有效索引）
      let actualCardIndex = targetCardIndex
      if (activeTab.value === 'random' && targetCardIndex >= 200) {
        actualCardIndex = 199
        console.log(`发现页面随机列表：目标索引${targetCardIndex}超过200，限制为${actualCardIndex}`)
      }
      
      console.log(`恢复滚动位置: cardIndex=${targetCardIndex}, 实际索引=${actualCardIndex}`)
      
      // 等待DOM完全渲染
      await nextTick()
      
      if (videoGrid.value && videos.value.length > 0) {
        const cards = document.querySelectorAll('.video-card')
        console.log(`DOM渲染完成: cards.length=${cards.length}, 实际索引=${actualCardIndex}`)
        
        if (cards.length > actualCardIndex && actualCardIndex >= 0) {
          // 计算目标卡片的位置
          const targetCard = cards[actualCardIndex]
          const cardTop = targetCard.offsetTop
          
          // 滚动到目标卡片位置，稍微向上偏移一些让卡片更居中
          videoGrid.value.scrollTop = Math.max(0, cardTop - 100)
          console.log(`滚动到卡片位置: 实际索引=${actualCardIndex}, cardTop=${cardTop}, scrollTop=${videoGrid.value.scrollTop}`)
        } else {
          // 如果卡片索引超出范围或为负数，默认滚动到顶部
          videoGrid.value.scrollTop = 0
          console.log(`滚动到顶部，卡片索引无效: 实际索引=${actualCardIndex}, 实际卡片数量=${cards.length}`)
        }
      } else {
        console.warn(`无法恢复滚动位置: videoGrid=${!!videoGrid.value}, videos.length=${videos.value.length}`)
      }
      

      
      // 添加页面离开时的缓存保存
      window.addEventListener('beforeunload', saveCacheData)
      
      // 页面加载后，自动为前几个视频生成缩略图
      setTimeout(() => {
        preGenerateThumbnails()
      }, 2000)
    })
    
    // 组件卸载时清理事件监听器
    onUnmounted(() => {
      if (saveCacheData) {
        window.removeEventListener('beforeunload', saveCacheData)
      }
    })


    
    // 在loadVideos函数中添加缩略图预生成
    const loadVideos = async () => {
      if (loading.value || !hasMore.value) return Promise.resolve()
      
      // 发现页面随机列表限制在200个视频以内
      if (activeTab.value === 'random' && videos.value.length >= 200) {
        hasMore.value = false
        console.log('发现页面随机列表已到达200个视频限制')
        return Promise.resolve()
      }
      
      loading.value = true
      try {
        // 构建查询参数
        const params = {
          page: page.value
        }
        
        // 获取当前用户ID，用于过滤讨厌的视频
        const savedUser = localStorage.getItem('currentUser')
        const user_id = savedUser ? JSON.parse(savedUser).id : null
        if (user_id) {
          params.user_id = user_id
        }
        
        if (activeTab.value === 'random') {
          params.random = true
          params.seed = randomSeed.value
          // 发现页面随机列表限制每页加载数量，确保不超过200个
          const remaining = 200 - videos.value.length
          if (remaining > 0) {
            params.per_page = Math.min(20, remaining)
          } else {
            hasMore.value = false
            loading.value = false
            return Promise.resolve()
          }
        }
        
        console.log(`发现页面API请求参数:`, params)
        
        // 使用统一的API服务获取视频列表
        const data = await videoApi.getVideos(params.page, params.per_page, params.random, params.seed)
        console.log(`发现页面API响应:`, data)
        console.log(`当前已加载视频数量: ${videos.value.length}, 新加载视频数量: ${data.items ? data.items.length : 0}`)
        
        if (!data.items) {
          hasMore.value = false
        } else {
          const oldLength = videos.value.length
          videos.value = [...videos.value, ...data.items]
          hasMore.value = data.has_next
          page.value += 1
          
          // 发现页面随机列表：达到200个视频后停止加载
          if (activeTab.value === 'random' && videos.value.length >= 200) {
            hasMore.value = false
            console.log('发现页面随机列表已到达200个视频限制')
          }
          
          // 即使视频不足20个也显示
          if (data.items.length < 20) {
            hasMore.value = false
          }
        }
      } catch (error) {
        console.error('获取视频列表失败:', error)
      } finally {
        loading.value = false
      }
    }

    const encodeVideoUrl = (url) => {
      try {
        const filename = url.split('/').pop()
        return `/api/videos/${filename}`
      } catch (e) {
        console.error('URL编码错误:', e)
        return url
      }
    }
    
    const removeFileExtension = (filename) => {
      if (!filename) return ''
      // 先提取文件名（去掉路径）
      const baseName = filename.split('/').pop().split('\\').pop()
      // 再去掉文件扩展名
      return baseName.replace(/\.[^/.]+$/, "")
    }

    const openPlayer = (video) => {
      console.log('=== 从发现页面打开模态框播放器 ===')
      console.log('点击的视频信息:', video)
      console.log('当前随机种子:', randomSeed.value)
      console.log('当前播放列表类型:', activeTab.value)
      console.log('当前视频列表长度:', videos.value.length)
      
      // 获取当前视频在列表中的索引
      const cardIndex = videos.value.findIndex(v => v.id === video.id)
      console.log('当前视频在列表中的索引:', cardIndex)
      
      if (cardIndex !== -1) {
        // 设置模态框播放器状态
        currentPlayingVideo.value = video
        currentPlayingIndex.value = cardIndex
        modalPlayerVisible.value = true
        console.log('打开模态框播放器，索引:', cardIndex)
      }
    }
    
    // 处理模态框播放器视频切换
    const handleVideoChange = (data) => {
      console.log('模态框播放器视频切换:', data)
      currentPlayingVideo.value = { ...data.video }
      currentPlayingIndex.value = data.index
      
      // 确保播放列表数据同步更新
      if (data.index >= 0 && data.index < videos.value.length) {
        videos.value[data.index] = { ...data.video }
      }
    }
    
    // 处理模态框播放器关闭
    const handleModalClose = () => {
      modalPlayerVisible.value = false
      currentPlayingVideo.value = null
      currentPlayingIndex.value = -1
    }
    
    // 处理模态框播放器列表刷新（随机列表）
    const handleListRefresh = () => {
      console.log('刷新随机列表')
      // 重新生成随机种子
      randomSeed.value = Date.now()
      // 重新加载视频列表
      videos.value = []
      page.value = 1
      hasMore.value = true
      loadVideos()
      // 关闭模态框
      modalPlayerVisible.value = false
    }

    // 获取缩略图URL - 优化逻辑
    const getThumbnailUrl = (video) => {
      const videoId = video.id
      
      // 检查缓存中是否已有该视频的缩略图URL
      if (thumbnailCache.value[videoId]) {
        console.log('📦 Using cached thumbnail URL for video:', videoId)
        return thumbnailCache.value[videoId]
      }
      
      console.log('🔍 getThumbnailUrl called with video:', {
        id: videoId,
        filename: video.filename,
        thumbnail_url: video.thumbnail_url
      })
      
      let thumbnailUrl
      
      // 如果后端返回了缩略图URL，直接使用并缓存
      if (video.thumbnail_url) {
        thumbnailUrl = video.thumbnail_url
        console.log('📸 Using backend thumbnail_url:', thumbnailUrl)
      } else {
        // 使用API服务中的统一缩略图URL生成方法
        thumbnailUrl = videoApi.getThumbnailUrl(videoId)
        console.log('🔄 Generated thumbnail URL via API service:', thumbnailUrl)
      }
      
      // 将结果存入缓存
      thumbnailCache.value[videoId] = thumbnailUrl
      console.log('💾 Cached thumbnail URL for video:', videoId)
      
      return thumbnailUrl
    }

    // 缩略图加载成功处理
    const handleThumbnailLoad = (videoId) => {
      console.log(`缩略图加载成功: ${videoId}`)
    }

    // 缩略图加载失败处理 - 简化逻辑
    const handleThumbnailError = async (videoId) => {
      console.log(`缩略图加载失败: ${videoId}`)
      // 由于我们直接使用 /api/thumbnail/<video_id> 接口，理论上不应该出现404错误
      // 如果出现错误，可能是网络问题或后端服务异常
      console.warn(`缩略图加载异常，视频ID: ${videoId}`)
    }

    // 预生成缩略图功能
    const preGenerateThumbnails = async (startIndex = 0, count = 5) => {
      // 为指定范围的视频预生成缩略图
      const endIndex = Math.min(startIndex + count, videos.value.length)
      const videosToPreGenerate = videos.value.slice(startIndex, endIndex)
      
      for (const video of videosToPreGenerate) {
        if (!video.thumbnail_url) {
          try {
            // 预生成缩略图，使用API服务
            await videoApi.apiFetch(`/thumbnail/${video.id}`)
            console.log(`预生成缩略图: ${video.id}`)
            // 更新该视频的缩略图URL，触发重新渲染
            const videoIndex = videos.value.findIndex(v => v.id === video.id)
            if (videoIndex !== -1) {
              const video = videos.value[videoIndex]
              // 使用后端返回的thumbnail_url，如果没有则使用正确的API路径
              if (!video.thumbnail_url) {
                // 使用API服务中的统一缩略图URL生成方法
                videos.value[videoIndex].thumbnail_url = videoApi.getThumbnailUrl(video.id)
              }
              videos.value = [...videos.value]
            }
          } catch (error) {
            console.error(`预生成缩略图失败: ${video.id}`, error)
          }
        }
      }
    }





    return { 
      videos,
      videoGrid,
      loading,
      hasMore,
      activeTab,
      randomSeed,
      modalPlayerVisible,
      currentPlayingVideo,
      currentPlayingIndex,
      handleScroll,
      encodeVideoUrl,
      openPlayer,
      removeFileExtension,
      getThumbnailUrl,
      handleVideoChange,
      handleModalClose,
      handleListRefresh,
      switchTab,
      handleThumbnailError,
      handleThumbnailLoad,
      preGenerateThumbnails
    }
  }
}
</script>

<style>
.loading-more,
.no-more {
  text-align: center;
  padding: 20px;
  grid-column: 1 / -1;
  color: #666;
}

.no-more {
  color: #999;
  font-size: 0.9em;
}

/* 顶部子页面导航样式 */
.sub-nav {
  display: flex;
  justify-content: center;
  margin-bottom: 12px;
  border-bottom: 1px solid #eee;
  background: white;
  position: sticky;
  top: 0;
  z-index: 10;
  padding: 6px 0;
}

.sub-nav-item {
  padding: 6px 16px;
  margin: 0 8px;
  cursor: pointer;
  border-radius: 16px;
  font-weight: 500;
  font-size: 0.85rem;
  transition: all 0.2s ease;
  color: #666;
}

.sub-nav-item:hover {
  background-color: #f5f5f5;
  color: #333;
}

.sub-nav-item.active {
  background-color: #ff6b81;
  color: white;
}
</style>

<style>
.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  position: relative;
  overflow: hidden;
}

.video-grid-container {
  padding: 8px;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  flex: 1;
  overflow-y: auto;
  padding-bottom: 56px; /* 为底部导航栏留出空间 */
  box-sizing: border-box;
  /* 隐藏滚动条但保持滚动功能 */
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE and Edge */
}

/* 隐藏WebKit浏览器的滚动条 */
.video-grid-container::-webkit-scrollbar {
  display: none;
}

h1 {
  text-align: center;
  margin-bottom: 20px;
  font-size: 1.5rem;
}

.video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 8px;
  width: 100%;
}

.video-card {
  border-radius: 8px;
  overflow: hidden;
  position: relative;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: transform 0.2s;
}

.video-card:hover {
  transform: scale(1.03);
}

.video-thumbnail {
  position: relative;
  padding-top: 133%; /* 3:4 比例，类似小红书卡片 */
  overflow: hidden;
}

.thumbnail-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumbnail-placeholder {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f0f0f0;
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 2px solid #ccc;
  border-top: 2px solid #ff6b81;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.video-title-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 8px;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.7));
  color: white;
  font-size: 0.8rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.favorite-button {
  position: absolute;
  top: 8px;
  right: 8px;
  z-index: 10;
  cursor: pointer;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 50%;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
}

.favorite-button:hover {
  background: rgba(0, 0, 0, 0.7);
}

.favorite-icon {
  font-size: 16px;
  line-height: 1;
}

/* 底部导航栏样式 */
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 56px;
  background-color: #fff;
  display: flex;
  justify-content: space-around;
  align-items: center;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
  z-index: 100;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  height: 100%;
  color: #666;
  transition: color 0.3s;
}

.nav-item.active {
  color: #ff6b81;
}

.nav-icon {
  width: 24px;
  height: 24px;
  margin-bottom: 2px;
  transition: all 0.3s ease;
}

.nav-item.active .nav-icon {
  color: #ff6b81;
}

.nav-item:not(.active) .nav-icon {
  color: #666;
}

.nav-item:hover .nav-icon {
  transform: scale(1.1);
}

.nav-item span {
  font-size: 0.7rem;
}
</style>