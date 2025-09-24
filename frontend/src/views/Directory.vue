<template>
  <div class="directory-container">
    <!-- 面包屑导航 -->
    <div class="breadcrumb">
      <span 
        class="breadcrumb-item" 
        :class="{ 'active': !currentPath }"
        @click="navigateTo('')"
      >
        根目录
      </span>
      <span 
        v-for="(part, index) in pathParts" 
        :key="index"
        class="breadcrumb-item"
      >
        <span class="separator">/</span>
        <span 
          :class="{ 'active': index === pathParts.length - 1 }"
          @click="navigateTo(pathParts.slice(0, index + 1).join('/'))"
        >
          {{ part }}
        </span>
      </span>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading">
      加载中...
    </div>

    <!-- 错误提示 -->
    <div v-else-if="error" class="error">
      {{ error }}
    </div>

    <!-- 目录内容 -->
    <div v-else class="directory-content">
      <!-- 子目录列表 -->
      <div v-if="subdirectories.length > 0" class="subdirectories-section">
        <h3>子目录</h3>
        <div class="subdirectories-grid">
          <div 
            v-for="subdir in subdirectories" 
            :key="subdir"
            class="directory-item"
            @click="navigateTo(subdir)"
          >
            <div class="directory-icon">
              📁
            </div>
            <div class="directory-name">
              {{ getDirectoryName(subdir) }}
            </div>
          </div>
        </div>
      </div>

      <!-- 视频文件列表 -->
      <div v-if="videos.length > 0" class="videos-section">
        <h3>视频文件 ({{ videos.length }})</h3>
        <div class="videos-grid">
          <div 
            v-for="video in videos" 
            :key="video.id"
            class="video-item"
            @click="openPlayer(video)"
          >
            <div class="video-thumbnail">
              <img 
                v-if="video.thumbnail_url"
                :src="video.thumbnail_url"
                :alt="video.title"
                class="thumbnail-image"
              />
              <div v-else class="thumbnail-placeholder">
                🎬
              </div>
            </div>
            <div class="video-title">
              {{ video.title }}
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="subdirectories.length === 0 && videos.length === 0" class="empty-state">
        <p>此目录为空</p>
      </div>
    </div>

    <!-- 底部导航栏 -->
    <div class="bottom-nav">
      <div class="nav-item" :class="{ active: $route.path === '/' }" @click="$router.push('/')">
        <NavIcons name="home" :active="$route.path === '/'" />
        <span>首页</span>
      </div>
      <div class="nav-item active">
        <NavIcons name="folder" :active="true" />
        <span>目录</span>
      </div>
      <div class="nav-item" :class="{ active: $route.path === '/favorites' }" @click="$router.push('/favorites')">
        <NavIcons name="favorite" :active="$route.path === '/favorites'" />
        <span>收藏</span>
      </div>
      <div class="nav-item" :class="{ active: $route.path === '/profile' }" @click="$router.push('/profile')">
        <NavIcons name="user" :active="$route.path === '/profile'" />
        <span>我</span>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import NavIcons from '../components/icons/NavIcons.vue'

export default {
  components: {
    NavIcons
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    
    const currentPath = ref('')
    const subdirectories = ref([])
    const videos = ref([])
    const loading = ref(false)
    const error = ref('')

    // 计算路径部分
    const pathParts = computed(() => {
      return currentPath.value ? currentPath.value.split('/').filter(part => part) : []
    })

    const getBaseUrl = () => {
      return import.meta.env.DEV 
        ? '/api' 
        : `${window.location.protocol}//${window.location.hostname}:5003/api`
    }

    // 获取目录名称（最后一部分）
    const getDirectoryName = (fullPath) => {
      const parts = fullPath.split('/')
      return parts[parts.length - 1]
    }

    // 加载目录内容
    const loadDirectoryContents = async (path = '') => {
      loading.value = true
      error.value = ''
      
      try {
        const baseUrl = getBaseUrl()
        const apiPath = path ? `/directory/${encodeURIComponent(path)}` : '/directories'
        const res = await fetch(`${baseUrl}${apiPath}`)
        
        if (!res.ok) {
          throw new Error(`HTTP ${res.status}: ${res.statusText}`)
        }
        
        const data = await res.json()
        subdirectories.value = data.subdirectories || []
        videos.value = data.videos || []
        
      } catch (err) {
        error.value = `加载目录失败: ${err.message}`
        console.error('加载目录失败:', err)
      } finally {
        loading.value = false
      }
    }

    // 导航到指定目录
    const navigateTo = (path) => {
      currentPath.value = path
      // 更新URL但不触发路由跳转
      const newPath = path ? `/directory/${encodeURIComponent(path)}` : '/directory'
      window.history.replaceState(null, '', newPath)
      loadDirectoryContents(path)
    }

    // 打开视频播放器
    const openPlayer = (video) => {
      router.push({
        name: 'Player',
        params: { id: video.id }
      })
    }

    // 预生成缩略图
    const preGenerateThumbnails = async (startIndex = 0, count = 5) => {
      // 为指定范围的视频预生成缩略图
      const endIndex = Math.min(startIndex + count, videos.value.length)
      const videosToPreGenerate = videos.value.slice(startIndex, endIndex)
      
      for (const video of videosToPreGenerate) {
        if (!video.thumbnail_url) {
          try {
            const baseUrl = getBaseUrl()
            await fetch(`${baseUrl}/thumbnail/${video.id}`)
            console.log(`预生成缩略图: ${video.id}`)
            // 更新该视频的缩略图URL，触发重新渲染
            const videoIndex = videos.value.findIndex(v => v.id === video.id)
            if (videoIndex !== -1) {
              videos.value[videoIndex].thumbnail_url = `${baseUrl}/thumbnail/${video.id}`
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

    // 初始化
    onMounted(() => {
      // 从路由参数获取当前路径
      const routePath = route.params.path || ''
      currentPath.value = routePath
      loadDirectoryContents(routePath).then(() => {
        // 页面加载后，自动为前几个视频生成缩略图
        setTimeout(() => {
          if (videos.value.length > 0) {
            preGenerateThumbnails()
          }
        }, 2000)
      })
    })

    // 监听路由变化
    watch(() => route.params.path, (newPath) => {
      currentPath.value = newPath || ''
      loadDirectoryContents(newPath)
    })

    return {
      currentPath,
      pathParts,
      subdirectories,
      videos,
      loading,
      error,
      getDirectoryName,
      navigateTo,
      openPlayer
    }
  }
}
</script>

<style scoped>
.directory-container {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
  min-height: 100vh;
  padding-bottom: 70px;
}

/* 面包屑导航 */
.breadcrumb {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  flex-wrap: wrap;
}

.breadcrumb-item {
  cursor: pointer;
  color: #666;
  font-size: 0.9rem;
}

.breadcrumb-item.active {
  color: #ff6b81;
  font-weight: 500;
}

.breadcrumb-item:hover:not(.active) {
  color: #ff6b81;
  text-decoration: underline;
}

.separator {
  margin: 0 8px;
  color: #999;
}

/* 加载和错误状态 */
.loading, .error, .empty-state {
  text-align: center;
  padding: 40px;
  color: #666;
}

.error {
  color: #e74c3c;
}

/* 目录内容 */
.directory-content {
  margin-bottom: 20px;
}

.subdirectories-section, .videos-section {
  margin-bottom: 30px;
}

.subdirectories-section h3, .videos-section h3 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 1.1rem;
}

/* 子目录网格 */
.subdirectories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.directory-item {
  background: white;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  text-align: center;
  transition: transform 0.2s, box-shadow 0.2s;
}

.directory-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.directory-icon {
  font-size: 2rem;
  margin-bottom: 8px;
}

.directory-name {
  font-size: 0.9rem;
  color: #333;
  word-break: break-all;
}

/* 视频网格 */
.videos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 15px;
}

.video-item {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: transform 0.2s;
}

.video-item:hover {
  transform: scale(1.03);
}

.video-thumbnail {
  position: relative;
  padding-top: 100%;
  background: #f0f0f0;
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
  font-size: 2rem;
  background: linear-gradient(135deg, #ff6b81, #ff8fa3);
  color: white;
}

.video-title {
  padding: 10px;
  font-size: 0.8rem;
  color: #333;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 底部导航栏 */
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

.nav-item span {
  font-size: 0.7rem;
}
</style>