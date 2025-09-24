<template>
  <div class="favorites-container">
    <div class="favorites-header">
      <h1>我的收藏</h1>
    </div>

    <div v-if="!currentUser" class="login-prompt">
      <div class="prompt-content">
        <div class="prompt-icon">🔒</div>
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
        <div class="empty-icon">⭐</div>
        <h2>暂无收藏</h2>
        <p>开始收藏您喜欢的视频吧</p>
      </div>

      <div v-else class="favorites-grid">
        <div 
          v-for="video in favorites" 
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
            />
            <div v-else class="thumbnail-placeholder">
              <div class="loading-spinner"></div>
            </div>
            <div class="video-title-overlay">
              {{ removeFileExtension(video.filename) }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部导航栏 -->
    <div class="bottom-nav">
      <div class="nav-item" @click="$router.push('/')">
        <NavIcons name="home" />
        <span>首页</span>
      </div>
      <div class="nav-item">
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
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import NavIcons from '../components/icons/NavIcons.vue'

export default {
  components: {
    NavIcons
  },
  setup() {
    const router = useRouter()
    const currentUser = ref(null)
    const favorites = ref([])
    const loading = ref(false)

    const getBaseUrl = () => {
      return import.meta.env.DEV 
        ? '/api' 
        : `${window.location.protocol}//${window.location.hostname}:5003/api`
    }

    const loadFavorites = async () => {
      if (!currentUser.value) return
      
      loading.value = true
      try {
        const baseUrl = getBaseUrl()
        const res = await fetch(`${baseUrl}/favorites?user_id=${currentUser.value.id}`)
        if (res.ok) {
          favorites.value = await res.json()
        }
      } catch (error) {
        console.error('获取收藏列表失败:', error)
      } finally {
        loading.value = false
      }
    }

    const removeFileExtension = (filename) => {
      return filename.replace(/\.[^/.]+$/, "")
    }

    const openPlayer = (video) => {
      if (!video || !video.id) {
        console.error('视频数据不完整:', video)
        return
      }
      
      router.push({
        name: 'Player',
        params: { id: video.id },
        query: { from: 'favorites' }
      })
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
    })

    return {
      currentUser,
      favorites,
      loading,
      removeFileExtension,
      openPlayer,
      goToLogin
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
</style>