#!/bin/bash

# 初始化多平台构建器
docker buildx create --use --name multiarch || true

# 获取当前版本号
VERSION=$(git describe --tags --abbrev=0 | sed 's/^v//' || echo "latest")
# 强制使用1.7.6版本
VERSION="1.7.6"

# 设置华为云镜像源
export DOCKER_BUILDKIT=1

echo "=== 开始构建 x86 架构镜像(v${VERSION}) ==="

# 检查前端目录是否存在
if [ ! -d "frontend" ]; then
    echo "警告: frontend 目录不存在，跳过前端构建"
    BUILD_FRONTEND=false
else
    BUILD_FRONTEND=true
fi

# 构建后端镜像 (仅x86)
echo "构建后端镜像..."
(cd backend && \
docker buildx build --platform linux/amd64 \
  -t mocaca-backend-x86:${VERSION} \
  -t mocaca-backend-x86:latest \
  --load . && \
docker save -o ../mocaca-backend-x86-${VERSION}.tar mocaca-backend-x86:latest) || exit 1

# 构建前端镜像 (仅x86，如果存在)
if [ "$BUILD_FRONTEND" = true ]; then
    echo "构建前端镜像..."
    (cd frontend && \
    docker buildx build --platform linux/amd64 \
      -t mocaca-frontend-x86:${VERSION} \
      -t mocaca-frontend-x86:latest \
      --load . && \
    docker save -o ../mocaca-frontend-x86-${VERSION}.tar mocaca-frontend-x86:latest) || exit 1
else
    echo "跳过前端镜像构建"
fi

echo "=== 镜像构建完成 ==="
echo "生成的tar文件:"
ls -lh mocaca-*-x86-${VERSION}.tar 2>/dev/null || echo "未生成tar文件"

# 查看镜像架构信息
echo "镜像架构信息:"
docker images | grep mocaca-x86 || echo "镜像未加载到本地"

exit 0