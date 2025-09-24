<template>
  <!-- 首页图标 -->
  <svg v-if="name === 'home'" class="nav-icon" width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
    <path d="M12 5.69l5 4.5V18h-2v-6H9v6H7v-7.81l5-4.5M12 3L2 12h3v8h6v-6h2v6h6v-8h3L12 3z"/>
  </svg>

  <!-- 目录图标 -->
  <svg v-else-if="name === 'folder'" class="nav-icon" width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
    <path d="M10 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z"/>
  </svg>

  <!-- 收藏图标 -->
  <svg v-else-if="name === 'favorite'" class="nav-icon" width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
    <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
  </svg>

  <!-- 用户图标 -->
  <svg v-else-if="name === 'user'" class="nav-icon" width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
    <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
  </svg>
</template>

<script>
export default {
  name: 'NavIcons',
  props: {
    name: {
      type: String,
      required: true,
      validator: (value) => ['home', 'folder', 'favorite', 'user'].includes(value)
    }
  }
}
</script>

<style scoped>
.nav-icon {
  width: 24px;
  height: 24px;
  transition: all 0.3s ease;
}
</style>