#!/bin/bash

# 多架构镜像构建脚本
# 同时构建x86和ARM架构的镜像

set -e

echo "=== 多架构镜像构建脚本 ==="

# 初始化多平台构建器
echo "初始化多平台构建器..."
docker buildx create --name multiarch --use --driver-opt network=host 2>/dev/null || true

# 获取当前版本号
VERSION=$(git describe --tags --abbrev=0 | sed 's/^v//' || echo "latest")
echo "当前版本: $VERSION"

# 检查前端目录是否存在
if [ ! -d "frontend" ]; then
    echo "警告: frontend 目录不存在，跳过前端构建"
    BUILD_FRONTEND=false
else
    BUILD_FRONTEND=true
fi

echo "=== 开始构建多架构镜像(v${VERSION}) ==="

# 构建后端镜像 (x86 + ARM)
echo "构建后端镜像 (x86 + ARM)..."
(cd backend && \
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t aidedaijiayang/mocaca-backend:${VERSION} \
  -t aidedaijiayang/mocaca-backend:latest \
  --push .) || exit 1

# 构建前端镜像 (x86 + ARM，如果存在)
if [ "$BUILD_FRONTEND" = true ]; then
    echo "构建前端镜像 (x86 + ARM)..."
    (cd frontend && \
    docker buildx build \
      --platform linux/amd64,linux/arm64 \
      -t aidedaijiayang/mocaca-frontend:${VERSION} \
      -t aidedaijiayang/mocaca-frontend:latest \
      --push .) || exit 1
else
    echo "跳过前端镜像构建"
fi

echo "=== 多架构镜像构建完成 ==="
echo "✅ 后端镜像已构建并推送到DockerHub:"
echo "   - aidedaijiayang/mocaca-backend:${VERSION} (x86 + ARM)"
echo "   - aidedaijiayang/mocaca-backend:latest (x86 + ARM)"

if [ "$BUILD_FRONTEND" = true ]; then
    echo "✅ 前端镜像已构建并推送到DockerHub:"
    echo "   - aidedaijiayang/mocaca-frontend:${VERSION} (x86 + ARM)"
    echo "   - aidedaijiayang/mocaca-frontend:latest (x86 + ARM)"
fi

echo ""
echo "镜像查看地址:"
echo "后端: https://hub.docker.com/r/aidedaijiayang/mocaca-backend"
echo "前端: https://hub.docker.com/r/aidedaijiayang/mocaca-frontend"

# 导出本地镜像用于测试
echo ""
echo "导出本地镜像到tar文件..."
docker pull aidedaijiayang/mocaca-backend:${VERSION}
docker save -o mocaca-backend-${VERSION}-multiarch.tar aidedaijiayang/mocaca-backend:${VERSION}

if [ "$BUILD_FRONTEND" = true ]; then
    docker pull aidedaijiayang/mocaca-frontend:${VERSION}
    docker save -o mocaca-frontend-${VERSION}-multiarch.tar aidedaijiayang/mocaca-frontend:${VERSION}
fi

echo "生成的tar文件:"
ls -lh mocaca-*-${VERSION}-multiarch.tar 2>/dev/null || echo "未生成tar文件"

exit 0