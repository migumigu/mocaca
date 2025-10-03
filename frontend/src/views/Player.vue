<template>
  <div class="player-container" ref="playerContainer">
    <video 
      ref="videoPlayer"
      controls
      autoplay
      playsinline
      webkit-playsinline
      x5-playsinline
      :src="videoUrl"
      class="fullscreen-video"
      x-webkit-airplay="allow"
    ></video>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { videoApi } from '../services/api.js'

export default {
  setup() {
    const route = useRoute()
    const videoPlayer = ref(null)
    const playerContainer = ref(null)
    const videoUrl = ref('')

    onMounted(() => {
      // 从路由获取视频ID并设置视频URL
      const videoId = route.params.id
      videoUrl.value = videoApi.getVideoFileUrl(videoId)
    })

    return {
      videoPlayer,
      playerContainer,
      videoUrl
    }
  }
}
</script>

<style>
.player-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: black;
  overflow: hidden;
}

.fullscreen-video {
  width: 100%;
  height: 100%;
  object-fit: contain;
}
</style>