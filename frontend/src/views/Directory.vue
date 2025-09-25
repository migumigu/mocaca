<template>
  <div class="directory-container">
    <!-- 简约待开发页面 -->
    <div class="coming-soon">
      <div class="coming-soon-content">
        <NavIcons name="folder" class="coming-soon-icon" />
        <h1>目录功能</h1>
        <p>此功能正在开发中，敬请期待</p>
        <div class="feature-list">
          <div class="feature-item">
            <NavIcons name="file" class="feature-icon" />
            <span>文件浏览</span>
          </div>
          <div class="feature-item">
            <NavIcons name="video" class="feature-icon" />
            <span>视频管理</span>
          </div>
          <div class="feature-item">
            <NavIcons name="search" class="feature-icon" />
            <span>智能搜索</span>
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
      <div class="nav-item active" @click="$router.push('/directory')">
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
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import NavIcons from '../components/icons/NavIcons.vue'

export default {
  components: {
    NavIcons
  },
  setup() {
    const router = useRouter()
    
    return {}
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

/* 简约待开发页面样式 */
.coming-soon {
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  padding: 60px 40px;
  text-align: center;
  margin-top: 40px;
}

.coming-soon-content {
  max-width: 400px;
  margin: 0 auto;
}

.coming-soon-icon {
  width: 80px;
  height: 80px;
  color: #ff6b81;
  margin-bottom: 24px;
}

.coming-soon h1 {
  font-size: 2rem;
  color: #333;
  margin-bottom: 16px;
  font-weight: 600;
}

.coming-soon p {
  font-size: 1.1rem;
  color: #666;
  margin-bottom: 32px;
  line-height: 1.6;
}

/* 功能列表样式 */
.feature-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 32px;
}

.feature-item {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 12px 20px;
  background: #f8f9fa;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.feature-item:hover {
  background: #f0f2f5;
  transform: translateX(4px);
}

.feature-icon {
  width: 24px;
  height: 24px;
  color: #ff6b81;
}

.feature-item span {
  font-size: 1rem;
  color: #333;
  font-weight: 500;
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