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

# 分别构建后端镜像 (x86 和 ARM)
echo "构建后端镜像 (x86)..."
(cd backend && \
docker buildx build --platform linux/amd64 \
  -t mocaca-backend-x86:${VERSION} \
  -t mocaca-backend-x86:latest \
  --load .) || exit 1

echo "构建后端镜像 (ARM)..."
(cd backend && \
docker buildx build --platform linux/arm64 \
  -t mocaca-backend-arm:${VERSION} \
  -t mocaca-backend-arm:latest \
  --load .) || exit 1

# 分别构建前端镜像 (x86 和 ARM，如果存在)
if [ "$BUILD_FRONTEND" = true ]; then
    echo "构建前端镜像 (x86)..."
    (cd frontend && \
    docker buildx build --platform linux/amd64 \
      -t mocaca-frontend-x86:${VERSION} \
      -t mocaca-frontend-x86:latest \
      --load .) || exit 1

    echo "构建前端镜像 (ARM)..."
    (cd frontend && \
    docker buildx build --platform linux/arm64 \
      -t mocaca-frontend-arm:${VERSION} \
      -t mocaca-frontend-arm:latest \
      --load .) || exit 1
else
    echo "跳过前端镜像构建"
fi

echo "=== 多架构镜像构建完成 ==="
echo "✅ 后端镜像已构建并加载到本地:"
echo "   - mocaca-backend-x86:${VERSION} (x86)"
echo "   - mocaca-backend-x86:latest (x86)"
echo "   - mocaca-backend-arm:${VERSION} (ARM)"
echo "   - mocaca-backend-arm:latest (ARM)"

if [ "$BUILD_FRONTEND" = true ]; then
    echo "✅ 前端镜像已构建并加载到本地:"
    echo "   - mocaca-frontend-x86:${VERSION} (x86)"
    echo "   - mocaca-frontend-x86:latest (x86)"
    echo "   - mocaca-frontend-arm:${VERSION} (ARM)"
    echo "   - mocaca-frontend-arm:latest (ARM)"
fi

# 导出本地镜像到tar文件
echo ""
echo "导出本地镜像到tar文件..."
docker save -o mocaca-backend-x86-${VERSION}.tar mocaca-backend-x86:latest
docker save -o mocaca-backend-arm-${VERSION}.tar mocaca-backend-arm:latest

if [ "$BUILD_FRONTEND" = true ]; then
    docker save -o mocaca-frontend-x86-${VERSION}.tar mocaca-frontend-x86:latest
    docker save -o mocaca-frontend-arm-${VERSION}.tar mocaca-frontend-arm:latest
fi

echo "生成的tar文件:"
ls -lh mocaca-*-${VERSION}.tar 2>/dev/null || echo "未生成tar文件"

# 查看镜像架构信息
echo "镜像架构信息:"
docker images | grep mocaca- || echo "镜像未加载到本地"

echo "生成的tar文件:"
ls -lh mocaca-*-${VERSION}-multiarch.tar 2>/dev/null || echo "未生成tar文件"

exit 0