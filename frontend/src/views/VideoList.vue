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
  </div>
</template>

<script>
import { ref, onMounted, nextTick, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import NavIcons from '../components/icons/NavIcons.vue'

export default {
  components: {
    NavIcons
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
    
    // 获取基础URL（包含/api路径）
    const getBaseUrl = () => {
      const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5003'
      return `${baseUrl}/api`
    }
    
    // 缓存相关状态
    const cacheKey = ref('')
    const cachedData = ref(null)
    

    
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
      
      // 即使有缓存，如果视频列表为空，也需要加载数据
      if (!hasCache || videos.value.length === 0) {
        // 需要加载数据
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
      
      // 页面加载后，自动为前几个视频生成缩略图
      setTimeout(() => {
        preGenerateThumbnails()
      }, 2000)
      
      // 添加页面离开时的缓存保存
      window.addEventListener('beforeunload', saveCacheData)
    })
    
    // 组件卸载时清理事件监听器
    onUnmounted(() => {
      if (saveCacheData) {
        window.removeEventListener('beforeunload', saveCacheData)
      }
    })

    const preGenerateThumbnails = async (startIndex = 0, count = 5) => {
      console.log(`=== 预生成缩略图开始 ===`)
      console.log(`起始索引: ${startIndex}, 数量: ${count}, 总视频数: ${videos.value.length}`)
      
      // 为指定范围的视频预生成缩略图
      const endIndex = Math.min(startIndex + count, videos.value.length)
      const videosToPreGenerate = videos.value.slice(startIndex, endIndex)
      console.log(`预生成缩略图视频范围: ${startIndex} 到 ${endIndex}, 共${videosToPreGenerate.length}个视频`)
      
      for (const video of videosToPreGenerate) {
        console.log(`处理视频ID: ${video.id}, 文件名: ${video.filename}, 当前缩略图URL: ${video.thumbnail_url}`)
        
        if (!video.thumbnail_url) {
          try {
            const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5003';
            const apiUrl = `${baseUrl}/api/thumbnail/${video.id}`
            console.log(`预生成缩略图API调用: ${apiUrl}`)
            
            const response = await fetch(apiUrl, {
              method: 'GET'
            })
            console.log(`预生成缩略图API响应状态: ${response.status}`)
            
            if (response.ok) {
              console.log(`预生成缩略图成功: ${video.id}`)
              // 更新该视频的缩略图URL，触发重新渲染
              const targetVideoIndex = videos.value.findIndex(v => v.id === video.id)
              console.log(`视频在列表中的索引: ${targetVideoIndex}`)
              
              if (targetVideoIndex !== -1) {
                // 使用后端返回的缩略图路径格式：只包含视频ID和文件名，不包含路径
                const thumbnailBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5003';
                // 从完整路径中提取文件名（需要先解码URL编码的路径）
                const decodedFilename = decodeURIComponent(video.filename);
                const filename = decodedFilename.split('/').pop().split('\\').pop();
                const newThumbnailUrl = `${thumbnailBaseUrl}/thumbnails/${video.id}_${filename}.jpg`
                console.log(`解码后的文件名: ${decodedFilename}, 提取的文件名: ${filename}`)
                console.log(`新缩略图URL: ${newThumbnailUrl}`)
                
                videos.value[targetVideoIndex].thumbnail_url = newThumbnailUrl
                // 强制更新视图
                videos.value = [...videos.value]
                console.log(`预生成缩略图URL更新完成`)
              }
            } else {
              console.warn(`预生成缩略图API调用失败: ${video.id}, 状态码: ${response.status}`)
            }
          } catch (error) {
            console.error(`预生成缩略图失败: ${video.id}`, error)
          }
        } else {
          console.log(`视频${video.id}已有缩略图，跳过预生成`)
        }
      }
      
      console.log(`预生成缩略图批次完成`)
      
      // 如果还有更多视频，继续预生成
      if (endIndex < videos.value.length) {
        console.log(`还有更多视频需要预生成，继续下一批`)
        setTimeout(() => {
          preGenerateThumbnails(endIndex, count)
        }, 1000) // 1秒后继续生成下一批
      } else {
        console.log(`所有视频缩略图预生成完成`)
      }
    }
    
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
        // 使用getBaseUrl接口获取API基础URL
        const baseUrl = getBaseUrl()
        
        // 获取当前用户ID，用于过滤讨厌的视频
        const savedUser = localStorage.getItem('currentUser')
        const user_id = savedUser ? JSON.parse(savedUser).id : null
        
        let apiUrl = `${baseUrl}/videos?page=${page.value}`
        
        if (user_id) {
          apiUrl += `&user_id=${user_id}`
        }
        
        if (activeTab.value === 'random') {
          apiUrl += `&random=true&seed=${randomSeed.value}`
          // 发现页面随机列表限制每页加载数量，确保不超过200个
          const remaining = 200 - videos.value.length
          if (remaining > 0) {
            apiUrl += `&per_page=${Math.min(20, remaining)}`
          } else {
            hasMore.value = false
            loading.value = false
            return Promise.resolve()
          }
        }
        
        console.log(`发现页面API请求: ${apiUrl}`)
        
        const res = await fetch(apiUrl, {
          headers: {
            'Content-Type': 'application/json'
          }
        })
        if (!res.ok) throw new Error(`HTTP错误! 状态码: ${res.status}`)
        
        const data = await res.json()
        console.log(`发现页面API响应:`, data)
        console.log(`当前已加载视频数量: ${videos.value.length}, 新加载视频数量: ${data.items ? data.items.length : 0}`)
        
        if (!data.items) {
          hasMore.value = false
        } else {
          const oldLength = videos.value.length
          // 处理缩略图URL：将相对路径转换为绝对URL
          const processedItems = data.items.map(item => {
            if (item.thumbnail_url && item.thumbnail_url.startsWith('/')) {
              // 生产环境：使用环境变量中的API基础URL
              const thumbnailBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5003';
              item.thumbnail_url = `${thumbnailBaseUrl}${item.thumbnail_url}`
            }
            return item
          })
          videos.value = [...videos.value, ...processedItems]
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
          
          // 缩略图现在由后端提供，无需前端处理视频加载
          
          // 为新加载的视频预生成缩略图
          if (oldLength >= 0) {
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
      if (!filename) return ''
      // 先提取文件名（去掉路径）
      const baseName = filename.split('/').pop().split('\\').pop()
      // 再去掉文件扩展名
      return baseName.replace(/\.[^/.]+$/, "")
    }

    const openPlayer = (video) => {
      console.log('=== 从发现页面打开播放器 ===')
      console.log('点击的视频信息:', video)
      console.log('当前随机种子:', randomSeed.value)
      console.log('当前播放列表类型:', activeTab.value)
      console.log('当前视频列表长度:', videos.value.length)
      console.log('当前视频列表前10个视频ID:', videos.value.slice(0, 10).map(v => v.id))
      
      // 保存当前点击的卡片在数组中的实际索引
      const cardIndex = videos.value.findIndex(v => v.id === video.id)
      console.log('当前视频在列表中的索引:', cardIndex)
      
      if (cardIndex !== -1) {
        sessionStorage.setItem('videoListCardIndex', cardIndex.toString())
        console.log('已保存索引到sessionStorage:', cardIndex)
      }
      
      router.push({
        name: 'Player',
        params: { id: video.id },
        query: {
          playlistType: activeTab.value,
          seed: activeTab.value === 'random' ? randomSeed.value : undefined
        }
      })
    }

    const handleThumbnailLoad = (videoId) => {
      console.log(`缩略图加载成功: ${videoId}`)
    }

    const handleThumbnailError = async (videoId) => {
      console.log(`=== 缩略图加载失败，尝试生成缩略图 ===`)
      console.log(`视频ID: ${videoId}`)
      
      // 触发后端生成缩略图
      try {
        const baseUrl = import.meta.env.VITE_API_BASE_URL || `${window.location.protocol}//${window.location.hostname}:5003`;
        const apiUrl = `${baseUrl}/api/thumbnail/${videoId}`
        console.log(`缩略图生成API URL: ${apiUrl}`)
        
        // 调用缩略图生成API（使用GET方法）
        const response = await fetch(apiUrl, {
          method: 'GET'
        })
        console.log(`缩略图生成API响应状态: ${response.status}`)
        
        if (response.ok) {
          console.log(`缩略图生成成功: ${videoId}`)
          // 更新该视频的缩略图URL，触发重新渲染
          const videoIndex = videos.value.findIndex(v => v.id === videoId)
          console.log(`视频在列表中的索引: ${videoIndex}`)
          
          if (videoIndex !== -1) {
            // 使用后端返回的缩略图路径格式：只包含视频ID和文件名，不包含路径
            const thumbnailBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5003';
            const targetVideo = videos.value[videoIndex];
            // 从完整路径中提取文件名（需要先解码URL编码的路径）
            const decodedFilename = decodeURIComponent(targetVideo.filename);
            const filename = decodedFilename.split('/').pop().split('\\').pop();
            const newThumbnailUrl = `${thumbnailBaseUrl}/thumbnails/${videoId}_${filename}.jpg`
            console.log(`解码后的文件名: ${decodedFilename}, 提取的文件名: ${filename}`)
            console.log(`新缩略图URL: ${newThumbnailUrl}`)
            
            videos.value[videoIndex].thumbnail_url = newThumbnailUrl
            // 强制更新视图
            videos.value = [...videos.value]
            console.log(`缩略图URL更新完成，强制视图更新`)
          } else {
            console.warn(`未找到视频ID为${videoId}的视频`)
          }
        } else {
          console.error(`缩略图生成失败: ${videoId}`, response.status, response.statusText)
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
      activeTab,
      handleScroll,
      encodeVideoUrl,
      openPlayer,
      removeFileExtension,
      handleThumbnailLoad,
      handleThumbnailError,
      switchTab
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