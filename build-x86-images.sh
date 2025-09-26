#!/bin/bash

# 初始化多平台构建器
docker buildx create --use --name multiarch || true

# 获取当前版本号
VERSION=$(git describe --tags --abbrev=0 | sed 's/^v//' || echo "latest")

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
  -t aidedaijiayang/mocaca-backend:${VERSION} \
  -t aidedaijiayang/mocaca-backend:latest \
  --load . && \
docker save -o ../mocaca-backend-${VERSION}.tar aidedaijiayang/mocaca-backend:latest) || exit 1

# 构建前端镜像 (仅x86，如果存在)
if [ "$BUILD_FRONTEND" = true ]; then
    echo "构建前端镜像..."
    (cd frontend && \
    docker buildx build --platform linux/amd64 \
      -t aidedaijiayang/mocaca-frontend:${VERSION} \
      -t aidedaijiayang/mocaca-frontend:latest \
      --load . && \
    docker save -o ../mocaca-frontend-${VERSION}.tar aidedaijiayang/mocaca-frontend:latest) || exit 1
else
    echo "跳过前端镜像构建"
fi

echo "=== 镜像构建完成 ==="
echo "生成的tar文件:"
ls -lh mocaca-*-${VERSION}.tar 2>/dev/null || echo "未生成tar文件"

# 查看镜像架构信息
echo "镜像架构信息:"
docker images | grep aidedaijiayang/mocaca || echo "镜像未加载到本地"

exit 0