<template>
  <div class="app-container">
    <div class="video-grid-container" ref="videoGrid" @scroll="handleScroll">
      <h1>快乐源泉~</h1>
      
      <div class="video-grid">
        <div 
          v-for="video in videos" 
          :key="video.id"
          class="video-card"
          @click="openPlayer(video)"
        >
          <div class="video-thumbnail">
            <img 
              v-if="video.thumbnail_url"
              class="thumbnail-image"
              :src="video.thumbnail_url"
              :alt="removeFileExtension(video.filename)"
              @load="handleThumbnailLoad(video.id)"
              @error="handleThumbnailError(video.id)"
            />
            <div v-else class="thumbnail-placeholder">
              <div class="loading-spinner"></div>
            </div>
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
        <i class="nav-icon">🏠</i>
        <span>首页</span>
      </div>
      <div class="nav-item">
        <i class="nav-icon">📁</i>
        <span>目录</span>
      </div>
      <div class="nav-item" @click="$router.push('/favorites')">
        <i class="nav-icon">⭐</i>
        <span>收藏</span>
      </div>
      <div class="nav-item" @click="$router.push('/profile')">
        <i class="nav-icon">👤</i>
        <span>我</span>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

export default {
  setup() {
    const videos = ref([])
    const router = useRouter()
    const videoGrid = ref(null)
    const loading = ref(false)
    const hasMore = ref(true)
    const page = ref(1)
    

    
    const handleScroll = () => {
      const container = videoGrid.value
      if (container && container.scrollTop + container.clientHeight >= container.scrollHeight - 100) {
        loadVideos()
      }
    }

    onMounted(() => {
      loadVideos()
      
      // 页面加载后，自动为前几个视频生成缩略图
      setTimeout(() => {
        preGenerateThumbnails()
      }, 2000)
    })

    const preGenerateThumbnails = async (startIndex = 0, count = 5) => {
      // 为指定范围的视频预生成缩略图
      const endIndex = Math.min(startIndex + count, videos.value.length)
      const videosToPreGenerate = videos.value.slice(startIndex, endIndex)
      
      for (const video of videosToPreGenerate) {
        if (!video.thumbnail_url) {
          try {
            const baseUrl = import.meta.env.DEV 
              ? '/api' 
              : `${window.location.protocol}//${window.location.hostname}:5003/api`;
            
            await fetch(`${baseUrl}/thumbnail/${video.id}`)
            console.log(`预生成缩略图: ${video.id}`)
            // 更新该视频的缩略图URL，触发重新渲染
            const videoIndex = videos.value.findIndex(v => v.id === video.id)
            if (videoIndex !== -1) {
              videos.value[videoIndex].thumbnail_url = `/api/thumbnail/${video.id}`
              // 强制更新视图
              videos.value = [...videos.value]
            }
          } catch (error) {
            console.error(`预生成缩略图失败: ${video.id}`, error)
          }
        }
      }
      
      // 如果还有更多视频，继续预生成
      if (endIndex < videos.value.length) {
        setTimeout(() => {
          preGenerateThumbnails(endIndex, count)
        }, 1000) // 1秒后继续生成下一批
      }
    }
    
    // 在loadVideos函数中添加缩略图预生成
    const loadVideos = async () => {
      if (loading.value || !hasMore.value) return
      
      loading.value = true
      try {
        // 根据环境动态获取API基础URL
        const baseUrl = import.meta.env.DEV 
          ? '/api' 
          : `${window.location.protocol}//${window.location.hostname}:5003/api`;
        const res = await fetch(`${baseUrl}/videos?page=${page.value}`, {
          headers: {
            'Content-Type': 'application/json'
          }
        })
        if (!res.ok) throw new Error(`HTTP错误! 状态码: ${res.status}`)
        
        const data = await res.json()
        if (!data.items) {
          hasMore.value = false
        } else {
          const oldLength = videos.value.length
          videos.value = [...videos.value, ...data.items]
          hasMore.value = data.has_next
          page.value += 1
          // 即使视频不足20个也显示
          if (data.items.length < 20) {
            hasMore.value = false
          }
          
          // 缩略图现在由后端提供，无需前端处理视频加载
          
          // 为新加载的视频预生成缩略图
          if (oldLength > 0) {
            preGenerateThumbnails(oldLength, 5)
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
      return filename.replace(/\.[^/.]+$/, "")
    }

    const openPlayer = (video) => {
      router.push({
        name: 'Player',
        params: { id: video.id }
      })
    }

    const handleThumbnailLoad = (videoId) => {
      console.log(`缩略图加载成功: ${videoId}`)
    }

    const handleThumbnailError = async (videoId) => {
      console.log(`缩略图加载失败，尝试生成: ${videoId}`)
      
      // 触发后端生成缩略图
      try {
        const baseUrl = import.meta.env.DEV 
          ? '/api' 
          : `${window.location.protocol}//${window.location.hostname}:5003/api`;
        
        // 调用缩略图生成API
        const response = await fetch(`${baseUrl}/thumbnail/${videoId}`)
        if (response.ok) {
          console.log(`缩略图生成成功: ${videoId}`)
          // 更新该视频的缩略图URL，触发重新渲染
          const videoIndex = videos.value.findIndex(v => v.id === videoId)
          if (videoIndex !== -1) {
            videos.value[videoIndex].thumbnail_url = `/api/thumbnail/${videoId}`
            // 强制更新视图
            videos.value = [...videos.value]
          }
        } else {
          console.error(`缩略图生成失败: ${videoId}`, response.status)
        }
      } catch (error) {
        console.error(`触发缩略图生成失败: ${videoId}`, error)
      }
    }

    return { 
      videos,
      videoGrid,
      loading,
      hasMore,
      handleScroll,
      encodeVideoUrl,
      openPlayer,
      removeFileExtension,
      handleThumbnailLoad,
      handleThumbnailError
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
  padding: 10px;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  flex: 1;
  overflow-y: auto;
  padding-bottom: 60px; /* 为底部导航栏留出空间 */
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
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 10px;
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
  font-size: 1.2rem;
  margin-bottom: 2px;
}

.nav-item span {
  font-size: 0.7rem;
}
</style>