# Mocaca前端模块设计文档
## 为uni-app移植准备的架构分析

### 1. 当前技术栈分析

**框架与依赖：**
- Vue 3.5.18 + Composition API
- Vue Router 4.5.1 (SPA路由)
- Vant 4.9.21 (移动端UI组件库)
- Vite 7.0.6 (构建工具)
- PWA支持 (Service Worker)

**核心功能模块：**
- 视频列表展示 (VideoList.vue)
- 视频播放器 (Player.vue + VideoPlayer.vue)
- 用户系统 (Profile.vue)
- 收藏管理 (Favorites.vue)
- 目录浏览 (Directory.vue - 待开发)

### 2. 页面路由结构

**当前路由配置：**
```javascript
const routes = [
  { path: '/', name: 'VideoList', component: VideoList },
  { path: '/player/:id', name: 'Player', component: VideoPlayer },
  { path: '/profile', name: 'Profile', component: Profile },
  { path: '/favorites', name: 'Favorites', component: Favorites },
  { path: '/directory', name: 'Directory', component: Directory },
  { path: '/directory/:path*', name: 'DirectoryPath', component: Directory }
]
```

**uni-app对应方案：**
- 使用uni-app的页面路由系统
- 每个页面对应一个.vue文件
- 路由跳转使用uni.navigateTo等API

### 3. 核心组件分析

#### 3.1 VideoList.vue (首页)
**功能特性：**
- 双标签页：最新/发现
- 无限滚动加载
- 缩略图懒加载与预生成
- 滚动位置记忆
- 缓存机制 (sessionStorage)

**uni-app适配要点：**
- 使用scroll-view替代原生滚动
- 图片懒加载使用uni-app的lazy-load
- 缓存机制适配uni-app的存储API

#### 3.2 Player.vue (播放页)
**功能特性：**
- 全屏视频播放
- 原生video标签控制
- 路由参数传递视频ID

**uni-app适配要点：**
- 使用uni-app的video组件
- 全屏控制使用uni-app API
- 页面参数传递方式调整

#### 3.3 Profile.vue (个人中心)
**功能特性：**
- 用户登录/登出
- 密码修改
- 讨厌内容管理
- 管理员功能 (文件刷新、缩略图生成)

**uni-app适配要点：**
- 表单处理保持相同逻辑
- 管理员功能API调用方式不变

#### 3.4 Favorites.vue (收藏页)
**功能特性：**
- 收藏视频列表展示
- 登录状态验证
- 缩略图展示

### 4. API接口分析

**后端接口模式：**
```javascript
const baseUrl = import.meta.env.DEV 
  ? '/api' 
  : `${window.location.protocol}//${window.location.hostname}:5003/api`
```

**uni-app适配方案：**
- 配置统一的请求基地址
- 使用uni.request替代fetch
- 保持相同的接口数据结构

### 5. 状态管理分析

**当前状态管理方式：**
- Composition API的ref/reactive
- 本地存储 (localStorage/sessionStorage)
- 路由参数传递

**uni-app适配方案：**
- 继续使用Composition API
- 存储使用uni.setStorageSync等API
- 页面间数据传递使用全局变量或Vuex

### 6. UI组件适配策略

#### 6.1 Vant组件替换
**需要替换的Vant组件：**
- van-swipe → uni-app的swiper
- van-swipe-item → swiper-item
- 自定义底部导航栏

**替代方案：**
- 使用uni-app原生组件
- 自定义底部tabBar配置

#### 6.2 样式适配
**CSS差异处理：**
- 保持现有的CSS Grid布局
- 适配rpx单位系统
- 处理平台特定的样式差异

### 7. 平台特性适配

#### 7.1 全屏功能
**当前实现：**
```javascript
// 多浏览器全屏API
element.requestFullscreen()
document.exitFullscreen()
```

**uni-app方案：**
- 使用uni.setFullScreen等API
- 平台兼容性处理

#### 7.2 文件系统访问
**当前特性：**
- 基于Web的文件访问
- 缩略图生成与存储

**uni-app方案：**
- 使用uni-app的文件系统API
- 适配移动端文件存储路径

### 8. 移植优先级建议

**第一阶段 (核心功能)：**
1. 视频列表展示
2. 视频播放
3. 用户登录
4. 基本导航

**第二阶段 (完整功能)：**
1. 收藏功能
2. 缩略图管理
3. 管理员功能
4. 性能优化

### 9. 技术风险与解决方案

#### 9.1 性能考虑
- 缩略图预生成策略需要优化
- 大列表滚动性能测试
- 内存管理监控

#### 9.2 兼容性问题
- 不同平台视频格式支持
- 全屏播放行为差异
- 文件系统访问权限

### 10. 测试策略

**功能测试重点：**
- 视频播放流畅性
- 用户交互响应速度
- 跨平台一致性
- 网络异常处理

这份设计文档基于对现有代码的详细分析，为uni-app移植提供了清晰的技术路线图和风险控制方案。