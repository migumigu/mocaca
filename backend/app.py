from flask import Flask, jsonify, send_from_directory, request
from werkzeug.utils import secure_filename
import os
import random
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import sqlite3
import subprocess
import uuid
from PIL import Image
import io
import base64

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///videos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

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
MEDIA_FOLDER = os.path.join(os.path.dirname(__file__), '../media')
THUMBNAIL_FOLDER = os.path.join(os.path.dirname(__file__), '../thumbnails')
app.config['MEDIA_FOLDER'] = MEDIA_FOLDER
app.config['THUMBNAIL_FOLDER'] = THUMBNAIL_FOLDER

# 确保缩略图目录存在
os.makedirs(THUMBNAIL_FOLDER, exist_ok=True)

def init_db():
    with app.app_context():
        db.create_all()
        # 创建默认管理员账户
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(username='admin', password='admin', is_admin=True)
            db.session.add(admin_user)
            db.session.commit()
            print("创建默认管理员账户: admin/admin")
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
        
        width = info['streams'][0]['width']
        height = info['streams'][0]['height']
        return height > width  # 高度大于宽度即为纵向视频
        
    except Exception as e:
        print(f"获取视频尺寸失败: {e}")
        # 如果ffprobe不可用或视频无法读取，默认接受该视频
        return True

def scan_media_folder():
    """递归扫描媒体文件夹及其子目录并更新数据库"""
    existing_files = {v.filename: v for v in Video.query.all()}
    current_files = set()
    
    # 递归扫描所有子目录
    for root, dirs, files in os.walk(app.config['MEDIA_FOLDER']):
        for filename in files:
            if filename.endswith('.mp4'):
                filepath = os.path.join(root, filename)
                # 只处理相对路径，保持文件名唯一性
                rel_path = os.path.relpath(filepath, app.config['MEDIA_FOLDER'])
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
    return jsonify({
        'id': video.id,
        'filename': video.filename,
        'url': f'/api/videos/file/{video.filename}',
        'next_id': video.next_id
    })

@app.route('/api/videos/prev/<int:video_id>')
def get_prev_video(video_id):
    """获取前一个视频信息"""
    # 查找指向当前视频的视频（即前一个视频）
    prev_video = Video.query.filter_by(next_id=video_id).first()
    
    if prev_video:
        return jsonify({
            'id': prev_video.id,
            'filename': prev_video.filename,
            'url': f'/api/videos/file/{prev_video.filename}',
            'next_id': prev_video.next_id
        })
    else:
        # 如果没有前一个视频，返回列表中的最后一个视频（循环播放）
        last_video = Video.query.filter(Video.next_id.is_(None)).first()
        if last_video:
            return jsonify({
                'id': last_video.id,
                'filename': last_video.filename,
                'url': f'/api/videos/file/{last_video.filename}',
                'next_id': last_video.next_id
            })
        return jsonify({'error': 'No previous video found'}), 404

@app.route('/api/videos/file/<path:filename>')
def get_video_file(filename):
    """获取视频文件（支持子目录）"""
    video_path = os.path.join(app.config['MEDIA_FOLDER'], filename)
    if os.path.exists(video_path):
        # 从完整路径中提取目录和文件名
        dirname = os.path.dirname(video_path)
        basename = os.path.basename(video_path)
        return send_from_directory(dirname, basename)
    return jsonify({'error': 'Video not found'}), 404

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
                'thumbnail_url': f'/api/thumbnail/{v.id}' if v.thumbnail_path else None
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
                'thumbnail_url': f'/api/thumbnail/{v.id}' if v.thumbnail_path else None
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
    """获取用户的收藏列表"""
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'error': '用户ID不能为空'}), 400
    
    favorites = Favorite.query.filter_by(user_id=user_id).all()
    favorite_videos = []
    for fav in favorites:
        video = Video.query.get(fav.video_id)
        if video:
            favorite_videos.append({
                'id': video.id,
                'filename': video.filename,
                'thumbnail_url': f'/api/thumbnail/{video.id}' if video.thumbnail_path else None
            })
    
    return jsonify(favorite_videos)

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
                'thumbnail_url': f'/api/thumbnail/{video.id}' if video.thumbnail_path else None
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

# 管理员API - 刷新文件列表
@app.route('/api/admin/refresh-files', methods=['POST'])
def admin_refresh_files():
    # 检查用户权限
    user_id = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not user_id:
        return jsonify({'error': '未授权'}), 401
    
    user = User.query.get(user_id)
    if not user or not user.is_admin:
        return jsonify({'error': '权限不足'}), 403
    
    try:
        # 重新扫描媒体目录
        media_dir = '/Users/yang/Documents/code/mocaca/media'
        video_files = []
        
        for root, dirs, files in os.walk(media_dir):
            for file in files:
                if file.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, media_dir)
                    video_files.append({
                        'filename': file,
                        'filepath': relative_path,
                        'directory': root.replace(media_dir, '').lstrip('/')
                    })
        
        # 更新数据库
        Video.query.delete()  # 清空现有数据
        
        for video_data in video_files:
            video = Video(
                filename=video_data['filename'],
                filepath=video_data['filepath'],
                directory=video_data['directory']
            )
            db.session.add(video)
        
        db.session.commit()
        
        return jsonify({
            'message': f'成功更新文件列表，共找到 {len(video_files)} 个视频文件',
            'file_count': len(video_files)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'刷新文件列表失败: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', '5003'))
    init_db()  # 初始化数据库
    app.run(host='0.0.0.0', port=port, debug=True)