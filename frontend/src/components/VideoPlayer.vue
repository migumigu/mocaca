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
          class="video-element"
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
        videos[index].play()
      }
    }

    return { videoEl, onSwipeChange }
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