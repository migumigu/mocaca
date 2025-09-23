<template>
  <div class="video-grid-container">
    <h1>快乐源泉~</h1>
    
    <div 
      class="video-grid"
      ref="videoGrid"
      @scroll="handleScroll"
    >
      <div 
        v-for="video in videos" 
        :key="video.id"
        class="video-card"
        @click="openPlayer(video)"
      >
        <div class="video-thumbnail">
          <video 
            class="thumbnail-video"
            :src="`/api/videos/file/${encodeURIComponent(video.filename)}`"
            preload="metadata"
            muted
            playsinline
            webkit-playsinline
            x5-playsinline
          ></video>
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
    
    const loadVideos = async () => {
      if (loading.value || !hasMore.value) return
      
      loading.value = true
      try {
        const res = await fetch(`http://localhost:5003/api/videos?page=${page.value}`, {
          headers: {
            'Content-Type': 'application/json'
          }
        })
        if (!res.ok) throw new Error(`HTTP错误! 状态码: ${res.status}`)
        
        const data = await res.json()
        if (!data.items) {
          hasMore.value = false
        } else {
          videos.value = [...videos.value, ...data.items]
          hasMore.value = data.has_next
          page.value += 1
          // 即使视频不足20个也显示
          if (data.items.length < 20) {
            hasMore.value = false
          }
          
          // 延迟设置视频缩略图
          setTimeout(() => {
            const videoElements = document.querySelectorAll('.thumbnail-video')
            videoElements.forEach(video => {
              if (!video.dataset.loaded) {
                video.currentTime = 0.1
                video.addEventListener('loadeddata', () => {
                  video.pause()
                  video.dataset.loaded = true
                })
              }
            })
          }, 100)
        }
      } catch (error) {
        console.error('获取视频列表失败:', error)
      } finally {
        loading.value = false
      }
    }
    
    const handleScroll = () => {
      const grid = videoGrid.value
      if (grid.scrollTop + grid.clientHeight >= grid.scrollHeight - 100) {
        loadVideos()
      }
    }

    onMounted(() => {
      loadVideos()
    })

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

    return { 
      videos,
      videoGrid,
      loading,
      hasMore,
      handleScroll,
      encodeVideoUrl,
      openPlayer,
      removeFileExtension
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
.video-grid-container {
  padding: 10px;
  max-width: 1200px;
  margin: 0 auto;
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

.thumbnail-video {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  pointer-events: none; /* 防止视频可点击 */
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
</style>