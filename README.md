# 视频播放平台 v0.1.1

## 主要功能

### 前端功能
- 视频列表展示（小红书风格卡片布局）
- 视频播放页面（抖音风格交互）
  - 上下滑动切换视频
  - 自动播放
  - 播放/暂停控制
- 响应式设计，适配移动端和桌面端

### 后端功能
- 视频文件管理API
  - 获取视频列表
  - 获取单个视频信息
  - 获取前一个/下一个视频信息
- 视频文件服务
  - 支持视频流式传输
  - 支持部分内容请求（206状态码）
- 数据库管理
  - 视频元数据存储
  - 视频关系维护

## 设计模型

### 系统架构
```
前端 (Vue 3 + Vant UI) ↔ 后端 (Flask + SQLAlchemy) ↔ 数据库 (SQLite)
```

### 前端设计
- **组件化架构**
  - VideoList: 视频列表页面
  - VideoPlayer: 视频播放页面
- **状态管理**
  - 使用Vue组合式API管理组件状态
  - 路由参数驱动视频切换
- **交互设计**
  - 卡片式列表布局
  - 手势控制播放切换

### 后端设计
- **RESTful API设计**
  - GET /api/videos - 获取视频列表
  - GET /api/videos/{id} - 获取视频信息
  - GET /api/videos/prev/{id} - 获取前一个视频
  - GET /api/videos/next/{id} - 获取下一个视频
  - GET /api/videos/file/{filename} - 获取视频文件
- **数据模型**
```python
class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), unique=True, nullable=False)
    filepath = db.Column(db.String(512), nullable=False)
    next_id = db.Column(db.Integer, db.ForeignKey('video.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

## 使用说明

1. 启动后端服务：
```bash
cd backend && python app.py
```

2. 启动前端开发服务器：
```bash
cd frontend && npm run dev
```

3. 访问前端应用：
http://localhost:5174/

## 版本历史
- v0.1.0: 初始版本，基础功能实现
- v0.1.1: 添加README文档，完善功能说明