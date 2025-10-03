<template>
  <div class="favorites-container">
    <div class="favorites-header">
      <h1>我的收藏</h1>
    </div>

    <div v-if="!currentUser" class="login-prompt">
      <div class="prompt-content">
        <NavIcons name="lock" class="prompt-icon" />
        <h2>需要登录</h2>
        <p>请先登录以查看您的收藏</p>
        <button @click="goToLogin" class="login-button">
          前往登录
        </button>
      </div>
    </div>

    <div v-else class="favorites-content">
      <div v-if="loading" class="loading">
        <div class="loading-spinner"></div>
        <p>加载中...</p>
      </div>

      <div v-else-if="favorites.length === 0" class="empty-favorites">
        <NavIcons name="star" class="empty-icon" />
        <h2>暂无收藏</h2>
        <p>开始收藏您喜欢的视频吧</p>
      </div>

      <div v-else class="favorites-grid">
        <!-- 当模态框播放器显示时，隐藏视频卡片以避免不必要的缩略图计算 -->
        <div 
          v-for="video in favorites" 
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
        
        <!-- 加载更多指示器 -->
        <div v-if="loading && favorites.length > 0" class="loading-more">
          <div class="loading-spinner"></div>
          <p>加载更多...</p>
        </div>
        
        <!-- 没有更多数据提示 -->
        <div v-if="!hasMore && favorites.length > 0" class="no-more-data">
          <p>已加载全部收藏视频</p>
        </div>
      </div>
    </div>

    <!-- 底部导航栏 -->
    <div class="bottom-nav">
      <div class="nav-item" @click="$router.push('/')">
        <NavIcons name="home" />
        <span>首页</span>
      </div>
      <div class="nav-item" @click="$router.push('/directory')">
        <NavIcons name="folder" />
        <span>目录</span>
      </div>
      <div class="nav-item active">
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
      :playlist-type="'favorites'"
      :playlist-videos="favorites"
      :current-index="currentPlayingIndex"
      :from-page="'favorites'"
      @close="handleModalClose"
      @video-change="handleVideoChange"
    />
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import NavIcons from '../components/icons/NavIcons.vue'
import ModalVideoPlayer from '../components/ModalVideoPlayer.vue'
import { favoriteApi, videoApi } from '../services/api.js'

export default {
  components: {
    NavIcons,
    ModalVideoPlayer
  },
  setup() {
    const router = useRouter()
    const currentUser = ref(null)
    const favorites = ref([])
    const loading = ref(false)
    const hasMore = ref(true)
    const currentPage = ref(1)
    const totalPages = ref(1)
    
    // 模态框播放器相关状态
    const modalPlayerVisible = ref(false)
    const currentPlayingVideo = ref(null)
    const currentPlayingIndex = ref(-1)
    
    // 缩略图URL缓存
    const thumbnailCache = ref({})

    const loadFavorites = async (page = 1, append = false) => {
      if (!currentUser.value || loading.value) return
      
      loading.value = true
      try {
        console.log('🔍 Loading favorites for user:', currentUser.value.id, 'page:', page)
        const response = await favoriteApi.getFavorites(currentUser.value.id, page, 50)
        console.log('📊 Favorites API response:', response)

        if (append) {
          // 追加模式：将新数据添加到现有列表
          favorites.value = [...favorites.value, ...(response.items || [])]
        } else {
          // 首次加载：替换整个列表
          favorites.value = response.items || []
        }
        
        currentPage.value = response.page
        totalPages.value = response.total_pages
        hasMore.value = response.page < response.total_pages
        
        // 调试：检查第一个视频的缩略图URL生成
        if (favorites.value.length > 0) {
          const firstVideo = favorites.value[0]
          console.log('🔍 First video data:', firstVideo)
          console.log('📸 Generated thumbnail URL for first video:', getThumbnailUrl(firstVideo))
        }
      } catch (error) {
        console.error('获取收藏列表失败:', error)
      } finally {
        loading.value = false
      }
    }

    // 加载更多收藏视频
    const loadMoreFavorites = async () => {
      if (hasMore.value && !loading.value) {
        await loadFavorites(currentPage.value + 1, true)
      }
    }

    // 监听滚动事件，实现无限滚动
    const handleScroll = () => {
      const scrollElement = document.documentElement
      const scrollTop = scrollElement.scrollTop
      const scrollHeight = scrollElement.scrollHeight
      const clientHeight = scrollElement.clientHeight
      
      // 距离底部100px时触发加载
      if (scrollTop + clientHeight >= scrollHeight - 100) {
        loadMoreFavorites()
      }
    }

    const removeFileExtension = (filename) => {
      if (!filename) return ''
      // 先提取文件名（去掉路径）
      const baseName = filename.split('/').pop().split('\\').pop()
      // 再去掉文件扩展名
      return baseName.replace(/\.[^/.]+$/, "")
    }

    // 获取缩略图URL - 带缓存优化
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
      console.log(`收藏页面缩略图加载成功: ${videoId}`)
    }

    // 缩略图加载失败处理 - 简化逻辑
    const handleThumbnailError = async (videoId) => {
      console.log(`收藏页面缩略图加载失败: ${videoId}`)
      // 由于我们直接使用 /api/thumbnail/<video_id> 接口，理论上不应该出现404错误
      // 如果出现错误，可能是网络问题或后端服务异常
      console.warn(`缩略图加载异常，视频ID: ${videoId}`)
    }

    const openPlayer = (video) => {
      if (!video || !video.id) {
        console.error('视频数据不完整:', video)
        return
      }
      
      // 获取当前视频在收藏列表中的索引
      const cardIndex = favorites.value.findIndex(v => v.id === video.id)
      console.log('收藏列表打开模态框播放器，索引:', cardIndex)
      
      if (cardIndex !== -1) {
        // 设置模态框播放器状态
        currentPlayingVideo.value = video
        currentPlayingIndex.value = cardIndex
        modalPlayerVisible.value = true
      }
    }
    
    // 处理模态框播放器视频切换
    const handleVideoChange = (data) => {
      console.log('收藏列表模态框播放器视频切换:', data)
      currentPlayingVideo.value = { ...data.video }
      currentPlayingIndex.value = data.index
      
      // 确保收藏列表数据同步更新
      if (data.index >= 0 && data.index < favorites.value.length) {
        favorites.value[data.index] = { ...data.video }
      }
    }
    
    // 处理模态框播放器关闭
    const handleModalClose = () => {
      modalPlayerVisible.value = false
      currentPlayingVideo.value = null
      currentPlayingIndex.value = -1
    }

    const goToLogin = () => {
      router.push('/profile')
    }

    onMounted(() => {
      const savedUser = localStorage.getItem('currentUser')
      if (savedUser) {
        currentUser.value = JSON.parse(savedUser)
        loadFavorites()
      }
      
      // 添加滚动监听
      window.addEventListener('scroll', handleScroll)
    })

    // 组件卸载时移除滚动监听
    onUnmounted(() => {
      window.removeEventListener('scroll', handleScroll)
    })

    return {
      currentUser,
      favorites,
      loading,
      modalPlayerVisible,
      currentPlayingVideo,
      currentPlayingIndex,
      removeFileExtension,
      getThumbnailUrl,
      openPlayer,
      goToLogin,
      handleVideoChange,
      handleModalClose,
      handleThumbnailLoad,
      handleThumbnailError
    }
  }
}
</script>

<style scoped>
.favorites-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  min-height: 100vh;
  padding-bottom: 70px;
}

.favorites-header {
  text-align: center;
  margin-bottom: 30px;
}

.favorites-header h1 {
  font-size: 1.8rem;
  color: #333;
}

.login-prompt {
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.prompt-content {
  max-width: 300px;
  margin: 0 auto;
}

.prompt-icon {
  font-size: 3rem;
  margin-bottom: 20px;
}

.login-prompt h2 {
  margin-bottom: 10px;
  color: #333;
}

.login-prompt p {
  color: #666;
  margin-bottom: 20px;
}

.login-button {
  padding: 12px 24px;
  background: #ff6b81;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
}

.favorites-content {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.loading {
  text-align: center;
  padding: 40px;
  color: #666;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #ff6b81;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-favorites {
  text-align: center;
  padding: 40px;
  color: #666;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 16px;
}

.empty-favorites h2 {
  margin-bottom: 8px;
  color: #333;
}

.favorites-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 10px;
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
  padding-top: 133%;
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
  cursor: pointer;
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

/* 加载更多指示器样式 */
.loading-more {
  grid-column: 1 / -1;
  text-align: center;
  padding: 20px;
  color: #666;
}

.loading-more .loading-spinner {
  width: 24px;
  height: 24px;
  border: 2px solid #f3f3f3;
  border-top: 2px solid #ff6b81;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 8px;
}

.loading-more p {
  margin: 0;
  font-size: 0.9rem;
}

/* 没有更多数据提示样式 */
.no-more-data {
  grid-column: 1 / -1;
  text-align: center;
  padding: 20px;
  color: #999;
  font-size: 0.9rem;
  border-top: 1px solid #eee;
  margin-top: 10px;
}
</style>