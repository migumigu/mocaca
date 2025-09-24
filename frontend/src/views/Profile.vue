<template>
  <div class="profile-container">
    <div class="profile-header">
      <h1>我</h1>
    </div>

    <div class="login-section" v-if="!currentUser">
      <h2>登录</h2>
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <input
            type="text"
            v-model="loginForm.username"
            placeholder="用户名"
            required
          />
        </div>
        <div class="form-group">
          <input
            type="password"
            v-model="loginForm.password"
            placeholder="密码"
            required
          />
        </div>
        <button type="submit" :disabled="loggingIn">
          {{ loggingIn ? '登录中...' : '登录' }}
        </button>
      </form>
      <p v-if="loginError" class="error-message">{{ loginError }}</p>
    </div>

    <div class="user-info" v-else>
      <div class="user-card">
        <div class="user-avatar">
          👤
        </div>
        <div class="user-details">
          <h2>{{ currentUser.username }}</h2>
          <p v-if="currentUser.is_admin" class="admin-badge">管理员</p>
          <p class="user-id">ID: {{ currentUser.id }}</p>
        </div>
      </div>

      <div class="stats-section">
        <div class="stat-item">
          <span class="stat-number">{{ dislikes.length }}</span>
          <span class="stat-label">讨厌</span>
        </div>
      </div>

      <button @click="handleLogout" class="logout-btn">
        退出登录
      </button>
    </div>

    <div class="dislikes-section" v-if="currentUser">
      <h3>我的讨厌</h3>
      <div v-if="dislikesLoading" class="loading">
        加载中...
      </div>
      <div v-else-if="dislikes.length === 0" class="empty-dislikes">
        <p>暂无讨厌</p>
      </div>
      <div v-else class="dislikes-grid">
        <div 
          v-for="video in dislikes" 
          :key="video.id"
          class="small-video-card"
          @click="openPlayer(video)"
        >
          <div class="small-video-thumbnail">
            <img 
              v-if="video.thumbnail_url"
              class="small-thumbnail-image"
              :src="video.thumbnail_url"
              :alt="removeFileExtension(video.filename)"
            />
            <div v-else class="small-thumbnail-placeholder">
              <div class="small-loading-spinner"></div>
            </div>
          </div>
          <div class="small-video-title">
            {{ removeFileExtension(video.filename) }}
          </div>
        </div>
      </div>
    </div>

    <!-- 底部导航栏 -->
    <div class="bottom-nav">
      <div class="nav-item" :class="{ active: $route.path === '/' }" @click="$router.push('/')">
        <NavIcons name="home" :active="$route.path === '/'" />
        <span>首页</span>
      </div>
      <div class="nav-item" :class="{ active: $route.path === '/favorites' }" @click="$router.push('/favorites')">
        <NavIcons name="favorite" :active="$route.path === '/favorites'" />
        <span>收藏</span>
      </div>
      <div class="nav-item active">
        <NavIcons name="user" :active="true" />
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
    const loginForm = ref({
      username: '',
      password: ''
    })
    const loggingIn = ref(false)
    const loginError = ref('')
    const dislikes = ref([])
    const dislikesLoading = ref(false)

    const getBaseUrl = () => {
      return import.meta.env.DEV 
        ? '/api' 
        : `${window.location.protocol}//${window.location.hostname}:5003/api`
    }

    const handleLogin = async () => {
      loggingIn.value = true
      loginError.value = ''
      
      try {
        const baseUrl = getBaseUrl()
        const res = await fetch(`${baseUrl}/login`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(loginForm.value)
        })
        
        const data = await res.json()
        if (res.ok) {
          currentUser.value = data.user
          localStorage.setItem('currentUser', JSON.stringify(data.user))
          await loadDislikes()
        } else {
          loginError.value = data.error || '登录失败'
        }
      } catch (error) {
        loginError.value = '网络错误，请重试'
      } finally {
        loggingIn.value = false
      }
    }

    const handleLogout = () => {
      currentUser.value = null
      localStorage.removeItem('currentUser')
      dislikes.value = []
    }

    const loadDislikes = async () => {
      if (!currentUser.value) return
      
      dislikesLoading.value = true
      try {
        const baseUrl = getBaseUrl()
        const res = await fetch(`${baseUrl}/dislikes?user_id=${currentUser.value.id}`)
        if (res.ok) {
          dislikes.value = await res.json()
        }
      } catch (error) {
        console.error('获取讨厌列表失败:', error)
      } finally {
        dislikesLoading.value = false
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

    onMounted(() => {
      // 检查本地存储是否有登录用户
      const savedUser = localStorage.getItem('currentUser')
      if (savedUser) {
        currentUser.value = JSON.parse(savedUser)
        loadDislikes()
      }
    })

    return {
      currentUser,
      loginForm,
      loggingIn,
      loginError,
      dislikes,
      dislikesLoading,
      handleLogin,
      handleLogout,
      removeFileExtension,
      openPlayer
    }
  }
}
</script>

<style scoped>
.profile-container {
  padding: 20px;
  max-width: 600px;
  margin: 0 auto;
  min-height: 100vh;
  padding-bottom: 70px;
}

.profile-header {
  text-align: center;
  margin-bottom: 30px;
}

.profile-header h1 {
  font-size: 1.8rem;
  color: #333;
}

.login-section {
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.login-section h2 {
  text-align: center;
  margin-bottom: 20px;
  color: #333;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.form-group input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
}

.login-form button {
  padding: 12px;
  background: #ff6b81;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
}

.login-form button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.error-message {
  color: #e74c3c;
  text-align: center;
  margin-top: 10px;
}

.user-info {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.user-card {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.user-avatar {
  font-size: 3rem;
  margin-right: 15px;
}

.user-details h2 {
  margin: 0 0 5px 0;
  color: #333;
}

.admin-badge {
  background: #ff6b81;
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
  display: inline-block;
}

.user-id {
  color: #666;
  font-size: 0.9rem;
  margin: 0;
}

.stats-section {
  display: flex;
  justify-content: center;
  margin: 20px 0;
}

.stat-item {
  text-align: center;
  padding: 0 20px;
}

.stat-number {
  display: block;
  font-size: 1.5rem;
  font-weight: bold;
  color: #ff6b81;
}

.stat-label {
  font-size: 0.9rem;
  color: #666;
}

.logout-btn {
  width: 100%;
  padding: 10px;
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.favorites-section {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.favorites-section h3 {
  margin: 0 0 15px 0;
  color: #333;
}

.loading, .empty-favorites {
  text-align: center;
  padding: 40px;
  color: #666;
}

.dislikes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  gap: 8px;
}

.small-video-card {
  border-radius: 6px;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: transform 0.2s;
  background: white;
}

.small-video-card:hover {
  transform: scale(1.05);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.small-video-thumbnail {
  position: relative;
  padding-top: 100%; /* 正方形比例 */
  overflow: hidden;
}

.small-thumbnail-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.small-thumbnail-placeholder {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f8f9fa;
}

.small-loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid #e9ecef;
  border-top: 2px solid #6c757d;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.small-video-title {
  padding: 4px 2px;
  font-size: 0.65rem;
  color: #495057;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.2;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
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