from flask import Flask, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import sqlite3

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///videos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 数据库模型
class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), unique=True, nullable=False)
    filepath = db.Column(db.String(512), nullable=False)
    next_id = db.Column(db.Integer, db.ForeignKey('video.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# 配置媒体文件路径
MEDIA_FOLDER = os.path.join(os.path.dirname(__file__), '../media')
app.config['MEDIA_FOLDER'] = MEDIA_FOLDER

def init_db():
    with app.app_context():
        db.create_all()
        scan_media_folder()

def scan_media_folder():
    """扫描媒体文件夹并更新数据库"""
    existing_files = {v.filename: v for v in Video.query.all()}
    current_files = set(os.listdir(app.config['MEDIA_FOLDER']))
    
    # 添加新文件
    for filename in current_files:
        if filename.endswith('.mp4') and filename not in existing_files:
            filepath = os.path.join(app.config['MEDIA_FOLDER'], filename)
            video = Video(filename=filename, filepath=filepath)
            db.session.add(video)
    
    db.session.commit()
    update_next_ids()

def update_next_ids():
    """更新视频的next_id关系"""
    videos = Video.query.order_by(Video.id).all()
    for i in range(len(videos)-1):
        videos[i].next_id = videos[i+1].id
    db.session.commit()

@app.route('/api/videos')
def list_videos():
    """获取视频列表"""
    videos = Video.query.order_by(Video.id).all()
    return jsonify([{
        'id': v.id,
        'filename': v.filename
    } for v in videos])

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
    """获取视频文件"""
    video_path = os.path.join(app.config['MEDIA_FOLDER'], filename)
    if os.path.exists(video_path):
        return send_from_directory(app.config['MEDIA_FOLDER'], filename)
    return jsonify({'error': 'Video not found'}), 404

@app.route('/api/scan', methods=['POST'])
def scan_videos():
    """手动触发扫描媒体文件夹"""
    scan_media_folder()
    return jsonify({'status': 'success'})

@app.route('/api/videos/<path:filename>')
def get_video(filename):
    # 直接使用原始文件名，不使用 secure_filename
    # 因为 secure_filename 会移除方括号等特殊字符
    video_path = os.path.join(app.config['MEDIA_FOLDER'], filename)
    
    if not os.path.exists(video_path):
        # 尝试查找不区分大小写的匹配
        for file in os.listdir(app.config['MEDIA_FOLDER']):
            if file.lower() == filename.lower():
                filename = file
                break
        # 再次检查文件是否存在
        video_path = os.path.join(app.config['MEDIA_FOLDER'], filename)
        if not os.path.exists(video_path):
            return f"File not found: {filename}", 404
        
    return send_from_directory(
        app.config['MEDIA_FOLDER'],
        filename,
        mimetype='video/mp4'
    )

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', '5003'))
    init_db()  # 初始化数据库
    app.run(host='0.0.0.0', port=port, debug=True)