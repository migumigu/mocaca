# 前端Dockerfile
FROM nginx:1.25-alpine

# 复制编译后的静态文件
COPY dist /usr/share/nginx/html

# 复制Nginx配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 启动Nginx
CMD ["nginx", "-g", "daemon off;"]