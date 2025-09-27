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
  -t aidedaijiayang/mocaca-backend:${VERSION} \
  -t aidedaijiayang/mocaca-backend:latest \
  --load .) || exit 1

echo "构建后端镜像 (ARM)..."
(cd backend && \
docker buildx build --platform linux/arm64 \
  -t aidedaijiayang/mocaca-backend:${VERSION} \
  -t aidedaijiayang/mocaca-backend:latest \
  --load .) || exit 1

# 分别构建前端镜像 (x86 和 ARM，如果存在)
if [ "$BUILD_FRONTEND" = true ]; then
    echo "构建前端镜像 (x86)..."
    (cd frontend && \
    docker buildx build --platform linux/amd64 \
      -t aidedaijiayang/mocaca-frontend:${VERSION} \
      -t aidedaijiayang/mocaca-frontend:latest \
      --load .) || exit 1

    echo "构建前端镜像 (ARM)..."
    (cd frontend && \
    docker buildx build --platform linux/arm64 \
      -t aidedaijiayang/mocaca-frontend:${VERSION} \
      -t aidedaijiayang/mocaca-frontend:latest \
      --load .) || exit 1
else
    echo "跳过前端镜像构建"
fi

echo "=== 多架构镜像构建完成 ==="
echo "✅ 后端镜像已构建并加载到本地:"
echo "   - aidedaijiayang/mocaca-backend:${VERSION} (x86)"
echo "   - aidedaijiayang/mocaca-backend:latest (x86)"
echo "   - aidedaijiayang/mocaca-backend:${VERSION} (ARM)"
echo "   - aidedaijiayang/mocaca-backend:latest (ARM)"

if [ "$BUILD_FRONTEND" = true ]; then
    echo "✅ 前端镜像已构建并加载到本地:"
    echo "   - aidedaijiayang/mocaca-frontend:${VERSION} (x86)"
    echo "   - aidedaijiayang/mocaca-frontend:latest (x86)"
    echo "   - aidedaijiayang/mocaca-frontend:${VERSION} (ARM)"
    echo "   - aidedaijiayang/mocaca-frontend:latest (ARM)"
fi

# 导出本地镜像到tar文件（暂时注释掉）
# echo ""
# echo "导出本地镜像到tar文件..."
# docker save -o mocaca-backend-x86-${VERSION}.tar aidedaijiayang/mocaca-backend:latest
# docker save -o mocaca-backend-arm-${VERSION}.tar aidedaijiayang/mocaca-backend:latest

# if [ "$BUILD_FRONTEND" = true ]; then
#     docker save -o mocaca-frontend-x86-${VERSION}.tar aidedaijiayang/mocaca-frontend:latest
#     docker save -o mocaca-frontend-arm-${VERSION}.tar aidedaijiayang/mocaca-frontend:latest
# fi

# echo "生成的tar文件:"
# ls -lh mocaca-*-${VERSION}.tar 2>/dev/null || echo "未生成tar文件"

# 查看镜像架构信息
echo "镜像架构信息:"
docker images | grep aidedaijiayang/mocaca- || echo "镜像未加载到本地"

exit 0