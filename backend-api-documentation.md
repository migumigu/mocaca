# Mocaca 后端API文档

## 概述
这是一个基于Flask的视频管理后端系统，支持视频播放、用户认证、收藏功能、讨厌功能以及管理员操作。

## 基础信息
- **后端服务地址**: `http://serverip:5003` (默认端口5003)
- **前端开发服务器**: `http://localhost:5173` (Vite开发服务器)
- **API前缀**: `/api`
- **缩略图路径**: `/thumbnails`
- **数据库**: SQLite (位于`backend/instance/videos.db`)
- **媒体文件目录**: `../media` (可通过环境变量`MEDIA_FOLDER`配置)
- **缩略图目录**: `../thumbnails` (可通过环境变量`THUMBNAIL_FOLDER`配置)

## 前端开发服务器配置
前端使用Vite开发服务器，配置了代理规则：
- `/api/*` → 代理到后端服务 `http://localhost:5003/api/*`
- `/thumbnails/*` → 代理到后端服务 `http://localhost:5003/thumbnails/*`

这样前端可以直接通过相对路径访问API和缩略图资源。

## API接口分类

### 1. 视频管理API

#### 获取视频列表
- **URL**: `GET /api/videos`
- **参数**:
  - `page` (可选): 页码，默认1
  - `per_page` (可选): 每页数量，默认20
  - `random` (可选): 是否随机排序，默认false
  - `seed` (可选): 随机种子
  - `user_id` (可选): 用户ID（用于过滤讨厌视频）
- **响应**: 包含视频列表、分页信息

#### 获取单个视频信息
- **URL**: `GET /api/videos/<video_id>`
- **响应**: 视频基本信息及下一个视频ID

#### 获取前一个视频
- **URL**: `GET /api/videos/prev/<video_id>`
- **功能**: 获取播放序列中的前一个视频

#### 获取视频文件
- **URL**: `GET /api/videos/file/<filename>`
- **功能**: 直接返回视频文件流

#### 获取视频缩略图
- **URL**: `GET /api/thumbnail/<video_id>`
- **功能**: 返回缩略图，如不存在会自动生成

### 2. 用户认证API

#### 用户登录
- **URL**: `POST /api/login`
- **请求体**: `{"username": "admin", "password": "admin"}`
- **响应**: 用户信息和权限

#### 修改密码
- **URL**: `POST /api/change-password`
- **请求体**: `{"user_id": 1, "current_password": "old", "new_password": "new"}`
- **权限**: 需要登录

### 3. 收藏功能API

#### 获取收藏列表
- **URL**: `GET /api/favorites?user_id=<user_id>`
- **功能**: 获取用户收藏的所有视频

#### 添加收藏
- **URL**: `POST /api/favorites`
- **请求体**: `{"user_id": 1, "video_id": 1}`

#### 移除收藏
- **URL**: `DELETE /api/favorites?user_id=1&video_id=1`

#### 检查收藏状态
- **URL**: `GET /api/favorites/check?user_id=1&video_id=1`

### 4. 讨厌功能API

#### 获取讨厌列表
- **URL**: `GET /api/dislikes?user_id=<user_id>`

#### 添加讨厌
- **URL**: `POST /api/dislikes`
- **请求体**: `{"user_id": 1, "video_id": 1}`

#### 移除讨厌
- **URL**: `DELETE /api/dislikes?user_id=1&video_id=1`

#### 检查讨厌状态
- **URL**: `GET /api/dislikes/check?user_id=1&video_id=1`

### 5. 缩略图管理API

#### 上传缩略图
- **URL**: `POST /api/upload_thumbnail/<video_id>`
- **请求体**: `{"thumbnail": "base64编码的图片数据"}`

### 6. 系统管理API（需要管理员权限）

#### 扫描媒体文件夹
- **URL**: `POST /api/scan`
- **功能**: 手动触发媒体文件扫描

#### 删除讨厌内容
- **URL**: `DELETE /api/admin/delete-dislike-content?video_id=<video_id>`
- **权限**: 管理员（Authorization头中传递用户ID）
- **功能**: 删除单个讨厌视频及相关文件

#### 批量删除所有讨厌内容
- **URL**: `DELETE /api/admin/delete-all-dislike-content`
- **功能**: 删除所有被讨厌的视频

#### 批量生成缩略图
- **URL**: `POST /api/admin/generate-thumbnails`
- **功能**: 为所有视频生成缩略图

#### 刷新文件列表
- **URL**: `POST /api/admin/refresh-files`
- **功能**: 智能扫描并更新数据库文件列表

## 权限说明

- **普通用户**: 可访问视频、收藏、讨厌相关API
- **管理员**: 额外可访问`/api/admin/*`接口
- **管理员账户**: 默认用户名`admin`，密码`admin`

## 认证方式
管理员接口需要在请求头中传递用户ID：
```
Authorization: Bearer <user_id>
```

## 数据模型

### User表
- `id`: 用户ID
- `username`: 用户名（唯一）
- `password`: 密码
- `is_admin`: 是否为管理员
- `created_at`: 创建时间

### Video表  
- `id`: 视频ID
- `filename`: 文件名（相对路径）
- `filepath`: 完整文件路径
- `next_id`: 下一个视频ID（播放序列）
- `thumbnail_path`: 缩略图路径
- `created_at`: 创建时间

### Favorite表
- `user_id`: 用户ID
- `video_id`: 视频ID
- 唯一约束防止重复收藏

### Dislike表
- `user_id`: 用户ID  
- `video_id`: 视频ID
- 唯一约束防止重复讨厌

## 特殊功能

1. **纵向视频过滤**: 自动过滤横向视频，只保留纵向视频
2. **智能文件扫描**: 支持递归扫描子目录
3. **缩略图自动生成**: 使用ffmpeg自动生成缩略图
4. **讨厌内容过滤**: 可根据用户讨厌列表过滤视频
5. **循环播放**: 支持视频播放序列循环

## 环境变量配置

```bash
# 媒体文件目录
export MEDIA_FOLDER=/path/to/media

# 缩略图目录  
export THUMBNAIL_FOLDER=/path/to/thumbnails

# Flask服务端口
export FLASK_PORT=5003
```

## 启动方式

### 后端服务
```bash
cd backend
python app.py
```

### 前端开发服务
```bash
cd frontend
npm run dev
```

### 开发环境完整启动
```bash
# 终端1 - 启动后端
cd backend && python app.py

# 终端2 - 启动前端  
cd frontend && npm run dev
```

该后端系统提供了完整的视频管理功能，支持用户交互和内容管理，适合短视频播放类应用。