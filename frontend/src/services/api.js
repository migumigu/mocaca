/**
 * 统一的API服务封装
 * 处理所有前端与后端的API通信
 */

/**
 * 获取完整的API基础URL
 * @returns {string} 完整的API基础URL
 */
export const getBaseUrl = () => {
  // 如果设置了环境变量，使用环境变量 + /api
  if (import.meta.env.VITE_API_BASE_URL) {
    return `${import.meta.env.VITE_API_BASE_URL}/api`
  }
  
  // 开发环境使用代理路径
  if (import.meta.env.DEV) {
    return '/api'
  }
  
  // 生产环境默认使用当前域名+端口 + /api
  return `${window.location.protocol}//${window.location.hostname}:5003/api`
}

/**
 * 获取API请求的完整URL
 * @param {string} endpoint - API端点路径（如 '/videos'）
 * @returns {string} 完整的API URL
 */
export const getApiUrl = (endpoint) => {
  const baseUrl = getBaseUrl()
  // 确保endpoint以斜杠开头
  const normalizedEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`
  return `${baseUrl}${normalizedEndpoint}`
}

/**
 * 统一的API请求函数
 * @param {string} endpoint - API端点
 * @param {Object} options - fetch选项
 * @returns {Promise<Response>}
 */
export const apiFetch = async (endpoint, options = {}) => {
  const url = getApiUrl(endpoint)
  
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    }
  }
  
  try {
    const response = await fetch(url, { ...defaultOptions, ...options })
    
    if (!response.ok) {
      throw new Error(`HTTP错误! 状态码: ${response.status}`)
    }
    
    return response
  } catch (error) {
    console.error(`API请求失败 [${endpoint}]:`, error)
    throw error
  }
}

/**
 * GET请求封装
 * @param {string} endpoint - API端点
 * @param {Object} params - 查询参数
 * @param {Object} options - 额外选项（如headers）
 * @returns {Promise<Object>}
 */
export const apiGet = async (endpoint, params = {}, options = {}) => {
  const queryString = new URLSearchParams(params).toString()
  const url = queryString ? `${endpoint}?${queryString}` : endpoint
  
  const response = await apiFetch(url, options)
  return await response.json()
}

/**
 * POST请求封装
 * @param {string} endpoint - API端点
 * @param {Object} data - 请求数据
 * @param {Object} options - 额外选项（如headers）
 * @returns {Promise<Object>}
 */
export const apiPost = async (endpoint, data = {}, options = {}) => {
  const response = await apiFetch(endpoint, {
    method: 'POST',
    body: JSON.stringify(data),
    ...options
  })
  return await response.json()
}

/**
 * PUT请求封装
 * @param {string} endpoint - API端点
 * @param {Object} data - 请求数据
 * @returns {Promise<Object>}
 */
export const apiPut = async (endpoint, data = {}) => {
  const response = await apiFetch(endpoint, {
    method: 'PUT',
    body: JSON.stringify(data)
  })
  return await response.json()
}

/**
 * DELETE请求封装
 * @param {string} endpoint - API端点
 * @param {Object} params - 查询参数
 * @param {Object} options - 额外选项（如headers）
 * @returns {Promise<Object>}
 */
export const apiDelete = async (endpoint, params = {}, options = {}) => {
  const queryString = new URLSearchParams(params).toString()
  const url = queryString ? `${endpoint}?${queryString}` : endpoint
  
  const response = await apiFetch(url, {
    method: 'DELETE',
    ...options
  })
  return await response.json()
}

/**
 * 视频相关API
 */
export const videoApi = {
  // 获取视频列表
  getVideos: (page = 1, perPage = 50, random = false, seed = null) => {
    const params = { page, per_page: perPage }
    if (random) params.random = true
    if (seed) params.seed = seed
    return apiGet('/videos', params)
  },
  
  // 获取单个视频信息
  getVideo: (id) => apiGet(`/videos/${id}`),
  
  // 获取前一个视频
  getPrevVideo: (id) => apiGet(`/videos/prev/${id}`),
  
  // 获取视频文件URL
  getVideoFileUrl: (filename) => getApiUrl(`/videos/file/${encodeURIComponent(filename)}`),
  
  // 获取缩略图URL
  getThumbnailUrl: (videoId) => getApiUrl(`/thumbnail/${videoId}`)
}

/**
 * 用户相关API
 */
export const userApi = {
  // 用户登录
  login: (username, password) => apiPost('/login', { username, password }),
  
  // 修改密码
  changePassword: (userId, currentPassword, newPassword) => 
    apiPost('/change-password', { user_id: userId, current_password: currentPassword, new_password: newPassword })
}

/**
 * 收藏相关API
 */
export const favoriteApi = {
  // 获取用户收藏
  getFavorites: (userId, page = 1, perPage = 50) => 
    apiGet('/favorites', { user_id: userId, page, per_page: perPage }),
  
  // 检查收藏状态
  checkFavorite: (userId, videoId) => 
    apiGet('/favorites/check', { user_id: userId, video_id: videoId }),
  
  // 添加收藏
  addFavorite: (userId, videoId) => 
    apiPost('/favorites', { user_id: userId, video_id: videoId }),
  
  // 取消收藏
  removeFavorite: (userId, videoId) => 
    apiDelete('/favorites', { user_id: userId, video_id: videoId }),
  
  // 收藏导航
  getFavoriteNavigation: (videoId, userId) => 
    apiGet(`/favorites/navigation/${videoId}`, { user_id: userId })
}

/**
 * 讨厌相关API
 */
export const dislikeApi = {
  // 获取用户讨厌列表
  getDislikes: (userId) => apiGet('/dislikes', { user_id: userId }),
  
  // 检查讨厌状态
  checkDislike: (userId, videoId) => 
    apiGet('/dislikes/check', { user_id: userId, video_id: videoId }),
  
  // 添加讨厌
  addDislike: (userId, videoId) => 
    apiPost('/dislikes', { user_id: userId, video_id: videoId }),
  
  // 取消讨厌
  removeDislike: (userId, videoId) => 
    apiDelete('/dislikes', { user_id: userId, video_id: videoId })
}

/**
 * 管理员API
 */
export const adminApi = {
  // 刷新文件列表
  refreshFiles: (userId) => apiPost('/admin/refresh-files', {}, {
    headers: { 'Authorization': `Bearer ${userId}` }
  }),
  
  // 获取刷新状态
  getRefreshStatus: (userId) => apiGet('/admin/refresh-status', {}, {
    headers: { 'Authorization': `Bearer ${userId}` }
  }),
  
  // 生成缩略图
  generateThumbnails: (userId) => apiPost('/admin/generate-thumbnails', {}, {
    headers: { 'Authorization': `Bearer ${userId}` }
  }),
  
  // 删除所有讨厌内容
  deleteAllDislikeContent: (userId) => apiDelete('/admin/delete-all-dislike-content', {}, {
    headers: { 'Authorization': `Bearer ${userId}` }
  })
}

export default {
  getBaseUrl,
  getApiUrl,
  apiFetch,
  apiGet,
  apiPost,
  apiPut,
  apiDelete,
  videoApi,
  userApi,
  favoriteApi,
  dislikeApi,
  adminApi
}