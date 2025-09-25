import os
import requests
import unittest

class VideoAPITest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.media_dir = os.path.join(os.path.dirname(__file__), '../media')
        cls.api_url = 'http://localhost:5000/api/videos'
        
    def test_media_directory_exists(self):
        """测试media目录是否存在"""
        self.assertTrue(os.path.exists(self.media_dir), 
                       f"Media目录不存在: {self.media_dir}")
        
    def test_video_files_exist(self):
        """测试media目录是否包含视频文件"""
        if os.path.exists(self.media_dir):
            video_files = [f for f in os.listdir(self.media_dir) 
                         if f.endswith(('.mp4', '.mov', '.avi'))]
            self.assertGreater(len(video_files), 0, 
                             "media目录中没有找到视频文件")
            
    def test_api_returns_videos(self):
        """测试API是否能返回视频列表"""
        response = requests.get(self.api_url)
        self.assertEqual(response.status_code, 200)
        videos = response.json()
        self.assertIsInstance(videos, list)
        if os.path.exists(self.media_dir):
            video_files = [f for f in os.listdir(self.media_dir) 
                         if f.endswith(('.mp4', '.mov', '.avi'))]
            self.assertEqual(len(videos), len(video_files))

if __name__ == '__main__':
    unittest.main()