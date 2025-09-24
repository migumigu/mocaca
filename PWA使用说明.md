# PWA 使用说明

## 功能特性

该项目已配置为支持PWA（渐进式Web应用），具备以下特性：

- ✅ 可添加到手机桌面
- ✅ 全屏显示（无浏览器导航栏）
- ✅ 离线缓存功能
- ✅ 原生应用体验

## 添加到桌面的方法

### iOS设备（Safari浏览器）
1. 使用Safari浏览器打开应用
2. 点击底部工具栏的"分享"按钮（方框带向上箭头）
3. 滑动找到并点击"添加到主屏幕"
4. 确认添加，应用图标将出现在桌面

### Android设备（Chrome浏览器）
1. 使用Chrome浏览器打开应用
2. 点击右上角菜单按钮（三个点）
3. 选择"添加到主屏幕"
4. 确认添加，应用图标将出现在桌面

## 技术配置

### manifest.json
- `display: standalone` - 全屏显示，无浏览器UI
- `orientation: portrait` - 锁定竖屏显示
- 支持192x192和512x512图标

### HTML Meta标签
- `apple-mobile-web-app-capable: yes` - iOS全屏支持
- `apple-mobile-web-app-status-bar-style: black-translucent` - 状态栏样式
- `viewport-fit=cover` - 全面屏适配

## 开发说明

项目使用Vite + VitePWA插件构建，自动生成Service Worker实现离线缓存。

构建命令：
```bash
npm run build
```

开发命令：
```bash
npm run dev