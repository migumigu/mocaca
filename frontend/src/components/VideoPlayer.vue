<template>
  <div class="player-container">
    <van-swipe 
      vertical 
      :loop="false"
      :touchable="true"
      @change="onSwipeChange"
    >
      <van-swipe-item v-for="video in videos" :key="video.id">
        <video 
          ref="videoEl"
          :src="video.url" 
          autoplay
          playsinline
          preload="auto"
          muted
          class="video-element"
          @loadstart="onVideoLoadStart"
          @loadeddata="onVideoLoaded"
          @waiting="onVideoWaiting"
          @canplay="onVideoCanPlay"
          @progress="onVideoProgress"
          @playing="onVideoPlaying"
          @error="onVideoError"
        ></video>
      </van-swipe-item>
    </van-swipe>
  </div>
</template>

<script>
import { ref } from 'vue'
import { Swipe, SwipeItem } from 'vant'

export default {
  components: { VanSwipe: Swipe, VanSwipeItem: SwipeItem },
  props: ['videos'],
  emits: ['swipe-up', 'swipe-down'],
  setup(props, { emit }) {
    const videoEl = ref(null)
    
    const onSwipeChange = (index) => {
      // 暂停所有视频
      const videos = videoEl.value
      if (videos) {
        videos.forEach(v => v.pause())
      }
      // 播放当前视频
      if (videos && videos[index]) {
        videos[index].play().catch(error => {
          console.log('播放失败，尝试静音播放:', error)
          videos[index].muted = true
          videos[index].play()
        })
      }
    }

    const onVideoLoaded = (event) => {
      console.log(`=== 视频元数据加载完成 === ${new Date().toISOString()}`)
    }

    const onVideoWaiting = (event) => {
      console.log(`=== 视频等待缓冲 === ${new Date().toISOString()}`)
    }

    const onVideoCanPlay = (event) => {
      console.log(`=== 视频可以播放 === ${new Date().toISOString()}`)
    }

    const onVideoLoadStart = (event) => {
      console.log(`=== 视频加载开始 === ${new Date().toISOString()}`)
    }

    const onVideoProgress = (event) => {
      const video = event.target
      if (video.buffered.length > 0) {
        const bufferedEnd = video.buffered.end(video.buffered.length - 1)
        const duration = video.duration
        const bufferedPercent = (bufferedEnd / duration * 100).toFixed(1)
        console.log(`缓冲进度: ${bufferedPercent}% (${bufferedEnd.toFixed(1)}s/${duration.toFixed(1)}s) ${new Date().toISOString()}`)
      }
    }

    const onVideoPlaying = (event) => {
      console.log(`=== 视频开始播放 === ${new Date().toISOString()}`)
    }

    const onVideoError = (event) => {
      console.error(`=== 视频加载错误 === ${new Date().toISOString()}`, event.target.error)
    }

    return { 
      videoEl, 
      onSwipeChange, 
      onVideoLoadStart,
      onVideoLoaded, 
      onVideoWaiting, 
      onVideoCanPlay,
      onVideoProgress,
      onVideoPlaying,
      onVideoError
    }
  }
}
</script>

<style scoped>
.player-container {
  height: 100vh;
  width: 100vw;
  background: #000;
}

.video-element {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
</style>