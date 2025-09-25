<template>
  <div id="app">
    <router-view />
    <!-- 全屏按钮（右上角） -->
    <div class="fullscreen-button" @click="toggleFullscreen">
      <div class="action-icon" :class="{ active: isFullscreen }">
        <span>{{ isFullscreen ? '恢复' : '全屏' }}</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      isFullscreen: false
    }
  },
  mounted() {
    // 监听全屏变化
    document.addEventListener('fullscreenchange', this.handleFullscreenChange)
    document.addEventListener('webkitfullscreenchange', this.handleFullscreenChange)
    document.addEventListener('mozfullscreenchange', this.handleFullscreenChange)
    document.addEventListener('MSFullscreenChange', this.handleFullscreenChange)
  },
  beforeUnmount() {
    document.removeEventListener('fullscreenchange', this.handleFullscreenChange)
    document.removeEventListener('webkitfullscreenchange', this.handleFullscreenChange)
    document.removeEventListener('mozfullscreenchange', this.handleFullscreenChange)
    document.removeEventListener('MSFullscreenChange', this.handleFullscreenChange)
  },
  methods: {
    toggleFullscreen() {
      if (!this.isFullscreen) {
        this.enterFullscreen()
      } else {
        this.exitFullscreen()
      }
    },
    enterFullscreen() {
      const element = document.documentElement
      
      if (element.requestFullscreen) {
        element.requestFullscreen().catch(err => {
          console.log('全屏请求错误:', err)
        })
      } else if (element.webkitRequestFullscreen) {
        element.webkitRequestFullscreen()
      } else if (element.mozRequestFullScreen) {
        element.mozRequestFullScreen()
      } else if (element.msRequestFullscreen) {
        element.msRequestFullscreen()
      }
    },
    exitFullscreen() {
      if (document.exitFullscreen) {
        document.exitFullscreen()
      } else if (document.webkitExitFullscreen) {
        document.webkitExitFullscreen()
      } else if (document.mozCancelFullScreen) {
        document.mozCancelFullScreen()
      } else if (document.msExitFullscreen) {
        document.msExitFullscreen()
      }
    },
    handleFullscreenChange() {
      this.isFullscreen = !!(
        document.fullscreenElement ||
        document.webkitFullscreenElement ||
        document.mozFullScreenElement ||
        document.msFullscreenElement
      )
    }
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  background-color: #f8f8f8;
}

/* 全屏按钮（右上角） */
.fullscreen-button {
  position: fixed;
  top: 20px;
  right: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  z-index: 1000;
}

.action-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  color: white;
  font-size: 12px;
  font-weight: 500;
  text-align: center;
  line-height: 1.2;
  padding: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.action-icon:hover {
  background: rgba(0, 0, 0, 0.7);
  transform: scale(1.05);
}

.action-icon.active {
  background: rgba(74, 144, 226, 0.6);
  box-shadow: 0 2px 12px rgba(74, 144, 226, 0.3);
  transform: scale(0.5);
  width: 48px;
  height: 48px;
  font-size: 14px;
  font-weight: 600;
}

.action-icon.active:hover {
  background: rgba(53, 122, 189, 0.7);
  transform: scale(0.55);
}
</style>