#!/usr/bin/env python3
"""
数据库初始化测试脚本
测试初始化过程是否会产生错误的数据导致文件找不到的问题
"""

import os
import sqlite3
import subprocess
import tempfile
import shutil

def test_db_initialization():
    """测试数据库初始化过程"""
    print("=== 数据库初始化测试 ===")
    
    # 创建临时目录用于测试
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"创建临时目录: {temp_dir}")
        
        # 创建测试媒体目录结构
        media_dir = os.path.join(temp_dir, 'media')
        os.makedirs(media_dir, exist_ok=True)
        
        # 创建一些测试视频文件
        test_files = [
            'video1.mp4',
            'subdir/video2.mp4', 
            'subdir/video3.mp4',
            'nonexistent/video4.mp4'  # 这个目录不存在，用于测试错误情况
        ]
        
        for file_path in test_files:
            full_path = os.path.join(media_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            if 'nonexistent' not in file_path:  # 只创建实际存在的文件
                with open(full_path, 'w') as f:
                    f.write("fake video content")
                print(f"创建测试文件: {full_path}")
        
        # 修改app.py中的媒体目录路径
        original_app_content = None
        try:
            with open('backend/app.py', 'r') as f:
                original_app_content = f.read()
            
            # 临时修改媒体目录路径
            modified_content = original_app_content.replace(
                "MEDIA_FOLDER = os.path.join(os.path.dirname(__file__), '../media')",
                f"MEDIA_FOLDER = '{media_dir}'"
            )
            
            with open('backend/app.py', 'w') as f:
                f.write(modified_content)
            
            print("临时修改媒体目录路径完成")
            
            # 运行数据库初始化
            print("运行数据库初始化...")
            result = subprocess.run(
                ['python', '-c', 'from backend.app import init_db; init_db()'],
                capture_output=True, text=True, cwd='.'
            )
            
            if result.returncode != 0:
                print(f"数据库初始化失败: {result.stderr}")
                return False
            
            print("数据库初始化成功")
            
            # 检查数据库内容
            db_path = 'backend/instance/videos.db'
            if not os.path.exists(db_path):
                print("数据库文件不存在")
                return False
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 查询所有视频记录
            cursor.execute("SELECT id, filename, filepath FROM video")
            videos = cursor.fetchall()
            
            print(f"数据库中找到 {len(videos)} 条视频记录")
            
            # 检查每条记录对应的文件是否存在
            invalid_count = 0
            for video_id, filename, filepath in videos:
                full_path = os.path.join(media_dir, filepath)
                exists = os.path.exists(full_path)
                
                if not exists:
                    print(f"错误: 视频ID {video_id} 文件不存在: {full_path}")
                    invalid_count += 1
                else:
                    print(f"正确: 视频ID {video_id} 文件存在: {full_path}")
            
            print(f"发现 {invalid_count} 个无效记录")
            
            if invalid_count > 0:
                print("❌ 测试失败: 数据库中存在无效文件记录")
                return False
            else:
                print("✅ 测试通过: 所有数据库记录都对应实际存在的文件")
                return True
                
        finally:
            # 恢复原始app.py内容
            if original_app_content:
                with open('backend/app.py', 'w') as f:
                    f.write(original_app_content)
                print("恢复原始app.py内容完成")

def test_scan_media_function():
    """测试scan_media_folder函数"""
    print("\n=== 扫描媒体文件夹功能测试 ===")
    
    # 导入必要的模块
    import sys
    sys.path.insert(0, 'backend')
    
    from app import app, Video, db
    
    with app.app_context():
        # 清空现有数据
        Video.query.delete()
        db.session.commit()
        
        # 手动调用扫描函数
        from app import scan_media_folder
        scan_media_folder()
        
        # 检查结果
        videos = Video.query.all()
        print(f"扫描后找到 {len(videos)} 个视频")
        
        # 检查文件存在性
        invalid_count = 0
        for video in videos:
            video_path = os.path.join('/Users/yang/Documents/code/mocaca', video.filepath)
            if not os.path.exists(video_path):
                print(f"错误: 视频ID {video.id} 文件不存在: {video_path}")
                invalid_count += 1
        
        if invalid_count > 0:
            print(f"❌ 扫描功能测试失败: 发现 {invalid_count} 个无效记录")
            return False
        else:
            print("✅ 扫描功能测试通过: 所有记录都对应实际文件")
            return True

if __name__ == '__main__':
    print("开始数据库初始化测试...")
    
    # 测试1: 数据库初始化
    test1_result = test_db_initialization()
    
    # 测试2: 扫描功能
    test2_result = test_scan_media_function()
    
    print(f"\n=== 测试结果汇总 ===")
    print(f"数据库初始化测试: {'通过' if test1_result else '失败'}")
    print(f"扫描功能测试: {'通过' if test2_result else '失败'}")
    
    if test1_result and test2_result:
        print("✅ 所有测试通过！数据库初始化过程没有问题")
    else:
        print("❌ 测试失败，请检查数据库初始化逻辑")