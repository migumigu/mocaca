<template>
  <div class="video-grid-container">
    <h1>视频文件列表</h1>
    
    <div class="video-grid">
      <div 
        v-for="video in videos" 
        :key="video.id"
        class="video-card"
        @click="openPlayer(video)"
      >
        <div class="video-thumbnail">
          <!-- 视频缩略图 -->
          <video 
            class="thumbnail-video"
            :src="`/api/videos/file/${encodeURIComponent(video.filename)}`"
            preload="metadata"
            muted
            playsinline
            webkit-playsinline
            x5-playsinline
          ></video>
          <!-- 视频标题 -->
          <div class="video-title-overlay">
            {{ removeFileExtension(video.filename) }}
          </div>
        </div>
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
    
    onMounted(async () => {
      try {
        const res = await fetch('/api/videos', {
          headers: {
            'Content-Type': 'application/json'
          }
        })
        if (!res.ok) throw new Error(`HTTP错误! 状态码: ${res.status}`)
        
        const data = await res.json()
        videos.value = data
        
        // 设置视频元素只显示第一帧
        setTimeout(() => {
          const videoElements = document.querySelectorAll('.thumbnail-video')
          videoElements.forEach(video => {
            video.currentTime = 0.1 // 设置到0.1秒确保能获取到帧
            video.addEventListener('loadeddata', () => {
              video.pause()
            })
          })
        }, 500) // 延迟确保视频元素已加载
      } catch (error) {
        console.error('获取视频列表失败:', error)
      }
    })

    const encodeVideoUrl = (url) => {
      try {
        // 直接使用原始文件名
        const filename = url.split('/').pop()
        return `/api/videos/${filename}`
      } catch (e) {
        console.error('URL编码错误:', e)
        return url // 回退原始URL
      }
    }
    
    // 去除文件后缀名
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
      encodeVideoUrl,
      openPlayer,
      removeFileExtension
    }
  }
}
</script>

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