from flask import Flask, jsonify, send_from_directory, request
from werkzeug.utils import secure_filename
import os
import random
import threading
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import sqlite3
import subprocess
import uuid
from PIL import Image
import io
import base64
import time
import hashlib
from collections import OrderedDict

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(__file__), 'instance', 'videos.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 文件句柄缓存管理器
class FileHandleCache:
    def __init__(self, max_size=10, timeout=300):
        self.cache = OrderedDict()
        self.max_size = max_size
        self.timeout = timeout
    
    def get(self, filepath):
        """获取文件句柄，如果存在且未超时"""
        if filepath in self.cache:
            handle_info = self.cache[filepath]
            if time.time() - handle_info['last_access'] < self.timeout:
                # 更新访问时间并移动到最新位置
                handle_info['last_access'] = time.time()
                self.cache.move_to_end(filepath)
                return handle_info['handle']
            else:
                # 超时，关闭句柄并移除
                self._close_handle(handle_info['handle'])
                del self.cache[filepath]
        return None
    
    def put(self, filepath, handle):
        """添加文件句柄到缓存"""
        if filepath in self.cache:
            # 如果已存在，先关闭旧句柄
            self._close_handle(self.cache[filepath]['handle'])
        
        # 添加新句柄
        self.cache[filepath] = {
            'handle': handle,
            'last_access': time.time()
        }
        
        # 如果超过最大大小，移除最旧的
        if len(self.cache) > self.max_size:
            oldest_filepath, oldest_info = self.cache.popitem(last=False)
            self._close_handle(oldest_info['handle'])
    
    def _close_handle(self, handle):
        """安全关闭文件句柄"""
        try:
            if handle and not handle.closed:
                handle.close()
        except Exception as e:
            print(f"关闭文件句柄时出错: {e}")
    
    def cleanup(self):
        """清理超时的句柄"""
        current_time = time.time()
        expired_files = []
        
        for filepath, handle_info in self.cache.items():
            if current_time - handle_info['last_access'] > self.timeout:
                expired_files.append(filepath)
        
        for filepath in expired_files:
            handle_info = self.cache[filepath]
            self._close_handle(handle_info['handle'])
            del self.cache[filepath]

# 全局文件句柄缓存
file_handle_cache = FileHandleCache(max_size=20, timeout=180)  # 缓存20个文件，3分钟超时



# 数据库模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), unique=True, nullable=False)
    filepath = db.Column(db.String(512), nullable=False)
    next_id = db.Column(db.Integer, db.ForeignKey('video.id'))
    thumbnail_path = db.Column(db.String(512))  # 缩略图文件路径
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 唯一约束，防止重复收藏
    __table_args__ = (db.UniqueConstraint('user_id', 'video_id', name='_user_video_uc'),)

class Dislike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 唯一约束，防止重复讨厌
    __table_args__ = (db.UniqueConstraint('user_id', 'video_id', name='_user_video_dislike_uc'),)

# 配置媒体文件路径
# 优先使用环境变量中的路径，否则使用默认路径
MEDIA_FOLDER = os.environ.get('MEDIA_FOLDER', os.path.join(os.path.dirname(__file__), '../media'))
THUMBNAIL_FOLDER = os.environ.get('THUMBNAIL_FOLDER', os.path.join(os.path.dirname(__file__), '../thumbnails'))
app.config['MEDIA_FOLDER'] = MEDIA_FOLDER
app.config['THUMBNAIL_FOLDER'] = THUMBNAIL_FOLDER

print(f"📁 媒体目录配置: {MEDIA_FOLDER}")
print(f"📁 缩略图目录配置: {THUMBNAIL_FOLDER}")
print(f"📁 媒体目录是否存在: {os.path.exists(MEDIA_FOLDER)}")
print(f"📁 缩略图目录是否存在: {os.path.exists(THUMBNAIL_FOLDER)}")

# 确保目录存在
os.makedirs(MEDIA_FOLDER, exist_ok=True)
os.makedirs(THUMBNAIL_FOLDER, exist_ok=True)

def init_db():
    with app.app_context():
        # 检查数据库文件是否存在（使用SQLAlchemy配置的路径）
        db_file = 'instance/videos.db'
        
        if not os.path.exists(db_file):
            # 如果数据库文件不存在，创建新的数据库
            print(f"数据库文件 {db_file} 不存在，创建新的数据库")
            db.create_all()
            # 创建默认管理员账户
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                admin_user = User(username='admin', password='admin', is_admin=True)
                db.session.add(admin_user)
                db.session.commit()
                print("创建默认管理员账户: admin/admin")
        else:
            # 数据库文件已存在，直接连接（确保表结构存在）
            db.create_all()
            print(f"数据库文件 {db_file} 已存在，直接连接")
        
        scan_media_folder()

def is_portrait_video(filepath):
    """使用ffprobe判断视频是否为纵向视频"""
    try:
        import subprocess
        import json
        
        # 使用ffprobe获取视频信息
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height',
            '-of', 'json',
            filepath
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        info = json.loads(result.stdout)
        
        # 检查是否有视频流
        if not info.get('streams') or len(info['streams']) == 0:
            print(f"获取视频尺寸失败: 文件没有视频流 - {filepath}")
            return False
            
        width = info['streams'][0]['width']
        height = info['streams'][0]['height']
        return height > width  # 高度大于宽度即为纵向视频
        
    except Exception as e:
        print(f"获取视频尺寸失败: {e}")
        # 如果ffprobe不可用或视频无法读取，跳过该文件
        return False

def scan_media_folder():
    """递归扫描媒体文件夹及其子目录并更新数据库"""
    existing_files = {v.filename: v for v in Video.query.all()}
    current_files = set()
    
    # 递归扫描所有子目录
    for root, dirs, files in os.walk(app.config['MEDIA_FOLDER']):
        # 过滤隐藏目录
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for filename in files:
            # 跳过隐藏文件
            if filename.startswith('.'):
                continue
                
            if filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
                filepath = os.path.join(root, filename)
                # 只处理相对路径，保持文件名唯一性
                rel_path = os.path.relpath(filepath, app.config['MEDIA_FOLDER'])
                
                # 检查相对路径是否包含隐藏目录（只检查目录名，不检查路径分隔符）
                if any(part.startswith('.') for part in rel_path.split(os.sep) if part):
                    continue
                    
                if rel_path not in existing_files and is_portrait_video(filepath):
                    video = Video(filename=rel_path, filepath=filepath)
                    db.session.add(video)
                    current_files.add(rel_path)
    
    db.session.commit()
    update_next_ids()

def update_next_ids():
    """更新视频的next_id关系"""
    videos = Video.query.order_by(Video.id).all()
    for i in range(len(videos)-1):
        videos[i].next_id = videos[i+1].id
    db.session.commit()



@app.route('/api/videos/<int:video_id>')
def get_video_info(video_id):
    """获取视频信息(包含下一个视频ID)"""
    video = Video.query.get_or_404(video_id)
    
    # 查找下一个视频（按ID顺序，更小的ID在前）
    next_video = Video.query.filter(Video.id > video_id).order_by(Video.id.asc()).first()
    next_id = next_video.id if next_video else None
    
    return jsonify({
        'id': video.id,
        'filename': video.filename,
        'url': f'/api/videos/file/{video.filename}',
        'next_id': next_id
    })

@app.route('/api/videos/prev/<int:video_id>')
def get_prev_video(video_id):
    """获取前一个视频信息"""
    # 查找前一个视频（按ID顺序，更大的ID在前）
    prev_video = Video.query.filter(Video.id < video_id).order_by(Video.id.desc()).first()
    
    if prev_video:
        return jsonify({
            'id': prev_video.id,
            'filename': prev_video.filename,
            'url': f'/api/videos/file/{prev_video.filename}',
            'next_id': prev_video.id
        })
    else:
        # 如果没有前一个视频，返回最大的ID视频（循环播放）
        last_video = Video.query.order_by(Video.id.desc()).first()
        if last_video:
            return jsonify({
                'id': last_video.id,
                'filename': last_video.filename,
                'url': f'/api/videos/file/{last_video.filename}',
                'next_id': last_video.id
            })
        return jsonify({'error': 'No previous video found'}), 404

@app.route('/api/videos/file/<path:filename>')
def get_video_file(filename):
    """获取视频文件（支持子目录，实现优化的流式传输）"""
    start_time = time.time()
    video_path = os.path.join(app.config['MEDIA_FOLDER'], filename)
    
    if not os.path.exists(video_path):
        print(f"❌ 视频文件不存在: {video_path}")
        return jsonify({'error': 'Video not found'}), 404
    
    # 获取文件信息
    file_size = os.path.getsize(video_path)
    file_mtime = os.path.getmtime(video_path)
    
    # 设置缓存头（1小时缓存）
    cache_control = 'public, max-age=3600'
    
    # 检查ETag和If-None-Match
    etag = f'"{file_size}-{file_mtime}"'
    if_none_match = request.headers.get('If-None-Match')
    if if_none_match and if_none_match == etag:
        return '', 304  # Not Modified
    
    # 获取Range请求头
    range_header = request.headers.get('Range')
    
    if not range_header:
        # 如果没有Range请求，返回整个文件
        response = send_from_directory(os.path.dirname(video_path), os.path.basename(video_path))
        response.headers.add('Accept-Ranges', 'bytes')
        response.headers.add('Cache-Control', cache_control)
        response.headers.add('ETag', etag)
        
        # 记录响应时间
        response_time = time.time() - start_time
        print(f"📊 完整文件响应时间: {response_time:.3f}s - {filename}")
        return response
    
    # 解析Range请求头（格式：bytes=start-end）
    try:
        range_type, range_value = range_header.split('=')
        if range_type != 'bytes':
            raise ValueError("Invalid range type")
        
        start_str, end_str = range_value.split('-')
        start = int(start_str) if start_str else 0
        end = int(end_str) if end_str else file_size - 1
        
        # 验证范围有效性
        if start < 0 or end < 0 or start >= file_size or end >= file_size or start > end:
            return jsonify({'error': 'Invalid range'}), 416
        
        # 计算读取大小（限制最大读取大小）
        content_length = end - start + 1
        max_chunk_size = 1024 * 1024 * 10  # 10MB最大块大小
        if content_length > max_chunk_size:
            end = start + max_chunk_size - 1
            content_length = max_chunk_size
        
        # 使用文件句柄缓存读取文件
        try:
            # 尝试从缓存获取文件句柄
            file_handle = file_handle_cache.get(video_path)
            
            if file_handle is None:
                # 缓存中没有，打开新文件句柄
                file_handle = open(video_path, 'rb')
                file_handle_cache.put(video_path, file_handle)
                print(f"📂 打开新文件句柄: {filename}")
            else:
                print(f"♻️ 使用缓存文件句柄: {filename}")
            
            # 使用缓存的文件句柄读取数据
            file_handle.seek(start)
            
            # 分块读取，避免大文件内存问题
            chunk_size = min(content_length, 8192)  # 8KB chunks
            data = b''
            remaining = content_length
            
            while remaining > 0:
                chunk = file_handle.read(min(chunk_size, remaining))
                if not chunk:
                    break
                data += chunk
                remaining -= len(chunk)
        
        except (IOError, OSError) as e:
            print(f"❌ 文件读取错误: {e}")
            # 文件读取失败，清理缓存并返回整个文件作为备选方案
            if video_path in file_handle_cache.cache:
                file_handle_cache._close_handle(file_handle_cache.cache[video_path]['handle'])
                del file_handle_cache.cache[video_path]
            
            response = send_from_directory(os.path.dirname(video_path), os.path.basename(video_path))
            response.headers.add('Accept-Ranges', 'bytes')
            response.headers.add('Cache-Control', cache_control)
            response.headers.add('ETag', etag)
            return response
        
        # 构建响应
        response = app.response_class(
            data,
            status=206,  # Partial Content
            mimetype='video/mp4',
            direct_passthrough=False
        )
        
        response.headers.add('Content-Range', f'bytes {start}-{end}/{file_size}')
        response.headers.add('Accept-Ranges', 'bytes')
        response.headers.add('Content-Length', str(content_length))
        response.headers.add('Cache-Control', cache_control)
        response.headers.add('ETag', etag)
        
        # 记录响应时间
        response_time = time.time() - start_time
        print(f"📊 Range请求响应时间: {response_time:.3f}s - {filename} (Range: {start_str}-{end_str})")
        
        return response
        
    except (ValueError, IndexError, TypeError) as e:
        print(f"❌ Range请求解析错误: {e}")
        # Range请求格式错误，返回整个文件
        response = send_from_directory(os.path.dirname(video_path), os.path.basename(video_path))
        response.headers.add('Accept-Ranges', 'bytes')
        response.headers.add('Cache-Control', cache_control)
        response.headers.add('ETag', etag)
        return response

@app.route('/thumbnails/<filename>')
def serve_thumbnail(filename):
    """直接提供缩略图静态文件访问（保持向后兼容）"""
    return send_from_directory(app.config['THUMBNAIL_FOLDER'], filename)

@app.route('/api/thumbnails/<filename>')
def serve_thumbnail_api(filename):
    """通过API路径提供缩略图静态文件访问"""
    return send_from_directory(app.config['THUMBNAIL_FOLDER'], filename)

@app.route('/api/scan', methods=['POST'])
def scan_videos():
    """手动触发扫描媒体文件夹"""
    scan_media_folder()
    return jsonify({'status': 'success'})



def generate_thumbnail(video_path, output_path, time_position='00:00:01'):
    """使用ffmpeg生成视频缩略图"""
    try:
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-ss', time_position,
            '-vframes', '1',
            '-vf', 'scale=320:-1',
            '-q:v', '2',
            output_path,
            '-y'  # 覆盖已存在的文件
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"生成缩略图失败: {e}")
        return False
    except Exception as e:
        print(f"生成缩略图异常: {e}")
        return False

@app.route('/api/thumbnail/<int:video_id>')
def get_thumbnail(video_id):
    """获取视频缩略图，如果不存在则生成"""
    video = Video.query.get_or_404(video_id)
    
    # 如果已有缩略图路径，直接返回
    if video.thumbnail_path and os.path.exists(video.thumbnail_path):
        return send_from_directory(
            os.path.dirname(video.thumbnail_path),
            os.path.basename(video.thumbnail_path),
            mimetype='image/jpeg'
        )
    
    # 生成缩略图
    video_path = os.path.join(app.config['MEDIA_FOLDER'], video.filename)
    if not os.path.exists(video_path):
        return jsonify({'error': 'Video file not found'}), 404
    
    # 创建缩略图文件名
    thumbnail_filename = f"{video.id}_{os.path.basename(video.filename)}.jpg"
    thumbnail_path = os.path.join(app.config['THUMBNAIL_FOLDER'], thumbnail_filename)
    
    # 生成缩略图
    if generate_thumbnail(video_path, thumbnail_path):
        # 更新数据库
        video.thumbnail_path = thumbnail_path
        db.session.commit()
        return send_from_directory(
            app.config['THUMBNAIL_FOLDER'],
            thumbnail_filename,
            mimetype='image/jpeg'
        )
    else:
        return jsonify({'error': 'Failed to generate thumbnail'}), 500

@app.route('/api/upload_thumbnail/<int:video_id>', methods=['POST'])
def upload_thumbnail(video_id):
    """前端上传缩略图（base64格式）"""
    video = Video.query.get_or_404(video_id)
    data = request.get_json()
    
    if not data or 'thumbnail' not in data:
        return jsonify({'error': 'No thumbnail data provided'}), 400
    
    try:
        # 解析base64数据
        thumbnail_data = data['thumbnail']
        if thumbnail_data.startswith('data:image/jpeg;base64,'):
            thumbnail_data = thumbnail_data.replace('data:image/jpeg;base64,', '')
        
        # 解码base64
        image_data = base64.b64decode(thumbnail_data)
        
        # 保存缩略图
        thumbnail_filename = f"{video.id}_{os.path.basename(video.filename)}.jpg"
        thumbnail_path = os.path.join(app.config['THUMBNAIL_FOLDER'], thumbnail_filename)
        
        with open(thumbnail_path, 'wb') as f:
            f.write(image_data)
        
        # 更新数据库
        video.thumbnail_path = thumbnail_path
        db.session.commit()
        
        return jsonify({'status': 'success', 'thumbnail_path': thumbnail_path})
        
    except Exception as e:
        return jsonify({'error': f'Failed to process thumbnail: {str(e)}'}), 500

# 修改视频列表API，返回缩略图URL
@app.route('/api/videos')
def list_videos():
    """获取视频列表（支持分页和随机排序，排除讨厌视频）"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    random_mode = request.args.get('random', 'false').lower() == 'true'
    seed = request.args.get('seed', type=int)
    user_id = request.args.get('user_id', type=int)
    
    if random_mode:
        # 使用种子确保随机列表的一致性
        if seed:
            random.seed(seed)
        else:
            random.seed()  # 使用系统时间作为种子
        
        # 获取所有视频ID，排除用户讨厌的视频
        if user_id:
            # 获取用户讨厌的视频ID列表
            disliked_videos = Dislike.query.filter_by(user_id=user_id).with_entities(Dislike.video_id).all()
            disliked_ids = [d.video_id for d in disliked_videos]
            # 排除讨厌的视频
            all_videos = Video.query.filter(~Video.id.in_(disliked_ids)).with_entities(Video.id).all()
        else:
            all_videos = Video.query.with_entities(Video.id).all()
        
        all_video_ids = [v.id for v in all_videos]
        
        # 随机打乱视频ID顺序
        random.shuffle(all_video_ids)
        
        # 计算分页
        total_videos = len(all_video_ids)
        total_pages = (total_videos + per_page - 1) // per_page
        has_next = page < total_pages
        
        # 获取当前页的视频ID
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        current_page_ids = all_video_ids[start_idx:end_idx]
        
        # 获取当前页的视频详情
        current_videos = Video.query.filter(Video.id.in_(current_page_ids)).all()
        
        # 保持随机顺序
        video_map = {v.id: v for v in current_videos}
        ordered_videos = [video_map[vid] for vid in current_page_ids if vid in video_map]
        
        return jsonify({
            'items': [{
                'id': v.id,
                'filename': v.filename,
                'thumbnail_url': f'/api/thumbnails/{os.path.basename(v.thumbnail_path)}' if v.thumbnail_path else None
            } for v in ordered_videos],
            'has_next': has_next,
            'total': total_videos
        })
    else:
        # 默认按ID顺序排序（最新在前），排除用户讨厌的视频
        if user_id:
            # 获取用户讨厌的视频ID列表
            disliked_videos = Dislike.query.filter_by(user_id=user_id).with_entities(Dislike.video_id).all()
            disliked_ids = [d.video_id for d in disliked_videos]
            # 排除讨厌的视频
            query = Video.query.filter(~Video.id.in_(disliked_ids)).order_by(Video.id.desc())
        else:
            query = Video.query.order_by(Video.id.desc())
        
        pagination = query.paginate(
            page=page, 
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'items': [{
                'id': v.id,
                'filename': v.filename,
                'thumbnail_url': f'/api/thumbnails/{os.path.basename(v.thumbnail_path)}' if v.thumbnail_path else None
            } for v in pagination.items],
            'has_next': pagination.has_next,
            'total': pagination.total
        })

# 用户认证和收藏相关API
@app.route('/api/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': '用户名和密码不能为空'}), 400
    
    user = User.query.filter_by(username=data['username'], password=data['password']).first()
    if user:
        return jsonify({
            'status': 'success',
            'user': {
                'id': user.id,
                'username': user.username,
                'is_admin': user.is_admin
            }
        })
    return jsonify({'error': '用户名或密码错误'}), 401

@app.route('/api/favorites', methods=['GET'])
def get_favorites():
    """获取用户的收藏列表（支持分页）"""
    user_id = request.args.get('user_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    if not user_id:
        return jsonify({'error': '用户ID不能为空'}), 400
    
    # 获取收藏总数
    total_favorites = Favorite.query.filter_by(user_id=user_id).count()
    
    # 分页查询收藏记录
    favorites = Favorite.query.filter_by(user_id=user_id)\
        .order_by(Favorite.created_at.desc())\
        .offset((page - 1) * per_page)\
        .limit(per_page)\
        .all()
    
    favorite_videos = []
    for fav in favorites:
        video = Video.query.get(fav.video_id)
        if video:
            favorite_videos.append({
                'id': video.id,
                'filename': video.filename,
                'thumbnail_url': f'/api/thumbnails/{os.path.basename(video.thumbnail_path)}' if video.thumbnail_path else None
            })
    
    return jsonify({
        'items': favorite_videos,
        'total': total_favorites,
        'page': page,
        'per_page': per_page,
        'total_pages': (total_favorites + per_page - 1) // per_page
    })

@app.route('/api/favorites', methods=['POST'])
def add_favorite():
    """添加收藏"""
    data = request.get_json()
    if not data or 'user_id' not in data or 'video_id' not in data:
        return jsonify({'error': '用户ID和视频ID不能为空'}), 400
    
    try:
        favorite = Favorite(user_id=data['user_id'], video_id=data['video_id'])
        db.session.add(favorite)
        db.session.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '收藏失败，可能已经收藏过'}), 400

@app.route('/api/favorites', methods=['DELETE'])
def remove_favorite():
    """移除收藏"""
    user_id = request.args.get('user_id', type=int)
    video_id = request.args.get('video_id', type=int)
    
    if not user_id or not video_id:
        return jsonify({'error': '用户ID和视频ID不能为空'}), 400
    
    favorite = Favorite.query.filter_by(user_id=user_id, video_id=video_id).first()
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({'status': 'success'})
    return jsonify({'error': '收藏记录不存在'}), 404

@app.route('/api/favorites/navigation/<int:video_id>', methods=['GET'])
def get_favorites_navigation(video_id):
    """获取收藏列表中指定视频的导航信息（下一个和前一个视频）"""
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'error': '用户ID不能为空'}), 400
    
    # 获取用户的所有收藏视频ID（按收藏时间倒序）
    favorites = Favorite.query.filter_by(user_id=user_id)\
        .order_by(Favorite.created_at.desc())\
        .all()
    
    favorite_video_ids = [fav.video_id for fav in favorites]
    
    # 查找当前视频在收藏列表中的位置
    try:
        current_index = favorite_video_ids.index(video_id)
    except ValueError:
        return jsonify({'error': '视频不在收藏列表中'}), 404
    
    # 获取下一个和前一个视频ID
    next_video_id = None
    prev_video_id = None
    
    if current_index > 0:
        prev_video_id = favorite_video_ids[current_index - 1]
    
    if current_index < len(favorite_video_ids) - 1:
        next_video_id = favorite_video_ids[current_index + 1]
    
    return jsonify({
        'current_video_id': video_id,
        'next_video_id': next_video_id,
        'prev_video_id': prev_video_id,
        'current_index': current_index,
        'total_favorites': len(favorite_video_ids)
    })

@app.route('/api/favorites/check', methods=['GET'])
def check_favorite():
    """检查是否已收藏"""
    user_id = request.args.get('user_id', type=int)
    video_id = request.args.get('video_id', type=int)
    
    if not user_id or not video_id:
        return jsonify({'error': '用户ID和视频ID不能为空'}), 400
    
    favorite = Favorite.query.filter_by(user_id=user_id, video_id=video_id).first()
    return jsonify({'is_favorited': favorite is not None})

# 讨厌功能API
@app.route('/api/dislikes', methods=['GET'])
def get_dislikes():
    """获取用户的讨厌列表"""
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'error': '用户ID不能为空'}), 400
    
    dislikes = Dislike.query.filter_by(user_id=user_id).all()
    dislike_videos = []
    for dislike in dislikes:
        video = Video.query.get(dislike.video_id)
        if video:
            dislike_videos.append({
                'id': video.id,
                'filename': video.filename,
                'thumbnail_url': f'/api/thumbnails/{os.path.basename(video.thumbnail_path)}' if video.thumbnail_path else None
            })
    
    return jsonify(dislike_videos)

@app.route('/api/dislikes', methods=['POST'])
def add_dislike():
    """添加讨厌"""
    data = request.get_json()
    if not data or 'user_id' not in data or 'video_id' not in data:
        return jsonify({'error': '用户ID和视频ID不能为空'}), 400
    
    try:
        dislike = Dislike(user_id=data['user_id'], video_id=data['video_id'])
        db.session.add(dislike)
        db.session.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '讨厌失败，可能已经讨厌过'}), 400

@app.route('/api/dislikes', methods=['DELETE'])
def remove_dislike():
    """移除讨厌"""
    user_id = request.args.get('user_id', type=int)
    video_id = request.args.get('video_id', type=int)
    
    if not user_id or not video_id:
        return jsonify({'error': '用户ID和视频ID不能为空'}), 400
    
    dislike = Dislike.query.filter_by(user_id=user_id, video_id=video_id).first()
    if dislike:
        db.session.delete(dislike)
        db.session.commit()
        return jsonify({'status': 'success'})
    return jsonify({'error': '讨厌记录不存在'}), 404

@app.route('/api/dislikes/check', methods=['GET'])
def check_dislike():
    """检查是否已讨厌"""
    user_id = request.args.get('user_id', type=int)
    video_id = request.args.get('video_id', type=int)
    
    if not user_id or not video_id:
        return jsonify({'error': '用户ID和视频ID不能为空'}), 400
    
    dislike = Dislike.query.filter_by(user_id=user_id, video_id=video_id).first()
    return jsonify({'is_disliked': dislike is not None})

# 管理员API - 删除讨厌内容（包括文件和数据库记录）
@app.route('/api/admin/delete-dislike-content', methods=['DELETE'])
def admin_delete_dislike_content():
    """管理员删除讨厌内容（包括文件、缩略图、数据库记录）"""
    # 检查用户权限
    user_id = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not user_id:
        return jsonify({'error': '未授权'}), 401
    
    user = User.query.get(user_id)
    if not user or not user.is_admin:
        return jsonify({'error': '权限不足'}), 403
    
    video_id = request.args.get('video_id', type=int)
    if not video_id:
        return jsonify({'error': '视频ID不能为空'}), 400
    
    try:
        # 获取视频信息
        video = Video.query.get(video_id)
        if not video:
            return jsonify({'error': '视频不存在'}), 404
        
        # 记录文件路径用于删除
        video_file_path = video.filepath
        thumbnail_path = video.thumbnail_path
        
        # 删除所有相关的讨厌记录
        Dislike.query.filter_by(video_id=video_id).delete()
        
        # 删除视频记录
        db.session.delete(video)
        db.session.commit()
        
        # 删除物理文件
        deleted_files = []
        if os.path.exists(video_file_path):
            os.remove(video_file_path)
            deleted_files.append(video_file_path)
        
        if thumbnail_path and os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)
            deleted_files.append(thumbnail_path)
        
        return jsonify({
            'status': 'success',
            'message': '讨厌内容删除成功',
            'deleted_files': deleted_files,
            'video_id': video_id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'删除失败: {str(e)}'}), 500

# 管理员API - 批量删除所有讨厌内容
@app.route('/api/admin/delete-all-dislike-content', methods=['DELETE'])
def admin_delete_all_dislike_content():
    """管理员批量删除所有讨厌内容（包括文件、缩略图、数据库记录）"""
    # 检查用户权限
    user_id = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not user_id:
        return jsonify({'error': '未授权'}), 401
    
    user = User.query.get(user_id)
    if not user or not user.is_admin:
        return jsonify({'error': '权限不足'}), 403
    
    try:
        # 获取所有讨厌的视频ID
        disliked_video_ids = [d.video_id for d in Dislike.query.all()]
        
        if not disliked_video_ids:
            return jsonify({'message': '没有讨厌内容可删除'})
        
        # 获取所有讨厌的视频
        disliked_videos = Video.query.filter(Video.id.in_(disliked_video_ids)).all()
        
        deleted_files = []
        deleted_video_ids = []
        
        # 删除所有讨厌记录
        Dislike.query.delete()
        
        # 删除视频记录和相关文件
        for video in disliked_videos:
            video_file_path = video.filepath
            thumbnail_path = video.thumbnail_path
            
            # 删除物理文件
            if os.path.exists(video_file_path):
                os.remove(video_file_path)
                deleted_files.append(video_file_path)
            
            if thumbnail_path and os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)
                deleted_files.append(thumbnail_path)
            
            # 删除视频记录
            db.session.delete(video)
            deleted_video_ids.append(video.id)
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': '所有讨厌内容删除成功',
            'deleted_files_count': len(deleted_files),
            'deleted_videos_count': len(deleted_video_ids),
            'deleted_video_ids': deleted_video_ids
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'批量删除失败: {str(e)}'}), 500

# 修改密码API
@app.route('/api/change-password', methods=['POST'])
def change_password():
    """修改用户密码"""
    data = request.get_json()
    if not data or 'user_id' not in data or 'current_password' not in data or 'new_password' not in data:
        return jsonify({'error': '用户ID、当前密码和新密码不能为空'}), 400
    
    try:
        user = User.query.get(data['user_id'])
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 验证当前密码
        if user.password != data['current_password']:
            return jsonify({'error': '当前密码不正确'}), 400
        
        # 更新密码
        user.password = data['new_password']
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': '密码修改成功'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'密码修改失败: {str(e)}'}), 500

# 管理员API - 批量生成缩略图
@app.route('/api/admin/generate-thumbnails', methods=['POST'])
def admin_generate_thumbnails():
    """为所有没有缩略图的视频生成缩略图"""
    # 检查用户权限
    user_id = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not user_id:
        return jsonify({'error': '未授权'}), 401
    
    user = User.query.get(user_id)
    if not user or not user.is_admin:
        return jsonify({'error': '权限不足'}), 403
    
    try:
        # 获取所有视频
        all_videos = Video.query.all()
        total_videos = len(all_videos)
        
        # 统计已有缩略图的视频
        existing_thumbnails = 0
        videos_without_thumbnails = []
        
        for video in all_videos:
            if video.thumbnail_path and os.path.exists(video.thumbnail_path):
                existing_thumbnails += 1
            else:
                videos_without_thumbnails.append(video)
        
        generated_count = 0
        failed_videos = []
        
        print(f"🎯 开始生成缩略图统计:")
        print(f"   - 总视频数: {total_videos}")
        print(f"   - 已有缩略图: {existing_thumbnails}")
        print(f"   - 需要生成: {len(videos_without_thumbnails)}")
        
        for i, video in enumerate(videos_without_thumbnails):
            print(f"🔄 处理第 {i+1}/{len(videos_without_thumbnails)} 个视频: {video.filename}")
            
            video_path = os.path.join(app.config['MEDIA_FOLDER'], video.filename)
            if not os.path.exists(video_path):
                print(f"❌ 视频文件不存在: {video_path}")
                failed_videos.append({'video_id': video.id, 'filename': video.filename, 'error': '视频文件不存在'})
                continue
            
            # 创建缩略图文件名
            thumbnail_filename = f"{video.id}_{os.path.basename(video.filename)}.jpg"
            thumbnail_path = os.path.join(app.config['THUMBNAIL_FOLDER'], thumbnail_filename)
            
            # 生成缩略图
            if generate_thumbnail(video_path, thumbnail_path):
                # 更新数据库
                video.thumbnail_path = thumbnail_path
                generated_count += 1
                print(f"✅ 成功生成缩略图: {thumbnail_filename}")
            else:
                failed_videos.append({'video_id': video.id, 'filename': video.filename, 'error': '缩略图生成失败'})
                print(f"❌ 缩略图生成失败: {video.filename}")
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'缩略图生成完成，总视频: {total_videos}，已有缩略图: {existing_thumbnails}，新增: {generated_count}，失败: {len(failed_videos)}',
            'total_videos': total_videos,
            'existing_thumbnails': existing_thumbnails,
            'generated_count': generated_count,
            'failed_count': len(failed_videos),
            'failed_videos': failed_videos
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ 批量生成缩略图失败: {str(e)}")
        import traceback
        print(f"🔍 详细错误信息: {traceback.format_exc()}")
        return jsonify({'error': f'批量生成缩略图失败: {str(e)}'}), 500

# 后台任务状态跟踪
refresh_task_status = {
    'running': False,
    'progress': 0,
    'message': '',
    'error': None
}

def async_refresh_files():
    """异步刷新文件列表的后台任务"""
    global refresh_task_status
    
    # 在应用上下文中执行数据库操作
    with app.app_context():
        try:
            refresh_task_status = {
                'running': True,
                'progress': 0,
                'message': '开始扫描媒体目录...',
                'error': None
            }
            
            # 获取媒体目录路径
            media_dir = app.config['MEDIA_FOLDER']
            print(f"🎯 开始智能扫描媒体目录: {media_dir}")
            
            # 获取当前数据库中的所有视频记录
            existing_videos = Video.query.all()
            existing_filepaths = {v.filepath: v for v in existing_videos}
            existing_filenames = {v.filename: v for v in existing_videos}
        
            print(f"🗃️ 当前数据库中的视频记录数: {len(existing_videos)}")
            
            # 扫描文件系统中的视频文件
            video_files = []
            scanned_dirs = []
            file_system_files = set()
            
            refresh_task_status['progress'] = 10
            refresh_task_status['message'] = '正在扫描文件系统...'
            
            # 递归扫描所有子目录，过滤隐藏文件和目录
            for root, dirs, files in os.walk(media_dir):
                # 过滤隐藏目录（以.开头的目录）
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                # 检查当前目录是否为隐藏目录（只检查目录名，不检查路径分隔符）
                # 正确的隐藏目录判断：只检查目录名是否以.开头
                current_dir = os.path.basename(root)
                if current_dir.startswith('.'):
                    print(f"⏭️ 跳过隐藏目录: {root}")
                    continue
                    
                scanned_dirs.append(root)
                print(f"🔍 扫描目录: {root}")
                
                for file in files:
                    # 跳过隐藏文件（以.开头的文件）
                    if file.startswith('.'):
                        continue
                        
                    if file.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, media_dir)
                        
                        # 检查相对路径是否包含隐藏目录（只检查目录名，不检查路径分隔符）
                        if any(part.startswith('.') for part in relative_path.split(os.sep) if part):
                            continue
                        
                        video_files.append({
                            'filename': file,
                            'filepath': relative_path,
                            'full_path': file_path
                        })
                        file_system_files.add(relative_path)
            
            refresh_task_status['progress'] = 50
            refresh_task_status['message'] = f'扫描完成，找到 {len(video_files)} 个视频文件，正在更新数据库...'
            
            print(f"📊 扫描完成统计:")
            print(f"   - 扫描目录总数: {len(scanned_dirs)}")
            print(f"   - 找到视频文件数: {len(video_files)}")
            
            # 智能更新数据库
            added_count = 0
            removed_count = 0
            unchanged_count = 0
            
            # 修复路径匹配：将数据库中的完整路径转换为相对路径进行比较
            existing_relative_paths = {}
            for filepath, video in existing_filepaths.items():
                try:
                    relative_path = os.path.relpath(filepath, media_dir)
                    existing_relative_paths[relative_path] = video
                except ValueError:
                    # 如果路径转换失败，可能是跨磁盘路径，直接使用文件名
                    existing_relative_paths[video.filename] = video
            
            # 1. 删除数据库中不存在对应文件的记录
            for relative_path, video in existing_relative_paths.items():
                if relative_path not in file_system_files:
                    print(f"🗑️ 删除数据库中不存在的文件记录: {relative_path}")
                    db.session.delete(video)
                    removed_count += 1
            
            refresh_task_status['progress'] = 70
            refresh_task_status['message'] = '正在添加新增文件...'
            
            # 2. 添加新增的文件到数据库
            for video_data in video_files:
                if video_data['filepath'] not in existing_relative_paths:
                    # 检查是否为纵向视频
                    if is_portrait_video(video_data['full_path']):
                        video = Video(
                            filename=video_data['filepath'],
                            filepath=video_data['full_path']
                        )
                        db.session.add(video)
                        print(f"💾 添加新增视频到数据库: {video_data['filepath']}")
                        added_count += 1
                    else:
                        print(f"⏭️ 跳过横向视频: {video_data['filepath']}")
                else:
                    unchanged_count += 1
        
            db.session.commit()
            
            refresh_task_status['progress'] = 100
            refresh_task_status['message'] = f'更新完成！新增 {added_count} 个文件，清理 {removed_count} 个不存在文件'
            refresh_task_status['running'] = False
            
            print("✅ 智能更新数据库完成")
            print(f"📈 更新统计:")
            print(f"   - 新增视频: {added_count}")
            print(f"   - 删除记录: {removed_count}")
            print(f"   - 保持不变: {unchanged_count}")
            print(f"   - 最终总数: {Video.query.count()}")
            
        except Exception as e:
            refresh_task_status = {
                'running': False,
                'progress': 0,
                'message': '',
                'error': str(e)
            }
            print(f"❌ 刷新文件列表失败: {str(e)}")
            import traceback
            print(f"🔍 详细错误信息: {traceback.format_exc()}")

# 管理员API - 刷新文件列表（异步版本）
@app.route('/api/admin/refresh-files', methods=['POST'])
def admin_refresh_files():
    # 检查用户权限
    user_id = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not user_id:
        return jsonify({'error': '未授权'}), 401
    
    user = User.query.get(user_id)
    if not user or not user.is_admin:
        return jsonify({'error': '权限不足'}), 403
    
    # 检查是否已有任务在运行
    if refresh_task_status['running']:
        return jsonify({
            'status': 'running',
            'message': '文件刷新任务正在运行中，请稍后查看结果',
            'progress': refresh_task_status['progress']
        })
    
    try:
        # 启动后台任务
        thread = threading.Thread(target=async_refresh_files)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'status': 'started',
            'message': '文件刷新任务已开始，将在后台处理',
            'progress': 0
        })
        
    except Exception as e:
        return jsonify({'error': f'启动刷新任务失败: {str(e)}'}), 500

# 管理员API - 获取刷新任务状态
@app.route('/api/admin/refresh-status', methods=['GET'])
def admin_refresh_status():
    # 检查用户权限
    user_id = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not user_id:
        return jsonify({'error': '未授权'}), 401
    
    user = User.query.get(user_id)
    if not user or not user.is_admin:
        return jsonify({'error': '权限不足'}), 403
    
    return jsonify(refresh_task_status)

# 定时清理文件句柄缓存
def start_cache_cleanup_task():
    """启动定时清理任务"""
    def cleanup_task():
        while True:
            time.sleep(60)  # 每分钟清理一次
            file_handle_cache.cleanup()
            print("🧹 清理超时文件句柄缓存")
    
    thread = threading.Thread(target=cleanup_task)
    thread.daemon = True
    thread.start()

# 应用启动时自动初始化数据库
def initialize_database():
    """在应用启动时初始化数据库"""
    with app.app_context():
        init_db()

# 在应用启动时立即初始化数据库
initialize_database()

# 启动缓存清理任务
start_cache_cleanup_task()

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', '5003'))
    app.run(host='0.0.0.0', port=port, debug=True)