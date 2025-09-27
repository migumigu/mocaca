#!/bin/bash

# DockerHub镜像发布脚本
# 将最新的镜像推送到DockerHub

set -e

echo "=== DockerHub镜像发布脚本 ==="

# 获取当前版本号
VERSION=$(git describe --tags --abbrev=0 2>/dev/null || echo "1.8.2")
# 去掉版本号中的v前缀
VERSION=${VERSION#v}
echo "当前版本: $VERSION"

# 检查Docker是否已登录DockerHub
echo "✅ DockerHub已登录，跳过登录步骤"

# 检查镜像是否存在
echo "检查本地镜像..."
BACKEND_IMAGE="aidedaijiayang/mocaca-backend:$VERSION"
FRONTEND_IMAGE="aidedaijiayang/mocaca-frontend:$VERSION"

if ! docker image inspect "$BACKEND_IMAGE" &>/dev/null; then
    echo "❌ 后端镜像不存在: $BACKEND_IMAGE"
    echo "请先运行 ./build-x86-images.sh 构建镜像"
    exit 1
fi

if ! docker image inspect "$FRONTEND_IMAGE" &>/dev/null; then
    echo "❌ 前端镜像不存在: $FRONTEND_IMAGE"
    echo "请先运行 ./build-x86-images.sh 构建镜像"
    exit 1
fi

echo "✅ 镜像检查通过"

echo "✅ 镜像检查通过"

# 为镜像添加latest标签
echo "添加latest标签..."
docker tag "$BACKEND_IMAGE" "aidedaijiayang/mocaca-backend:latest"
docker tag "$FRONTEND_IMAGE" "aidedaijiayang/mocaca-frontend:latest"

# 推送镜像到DockerHub
echo "推送后端镜像到DockerHub..."
docker push "$BACKEND_IMAGE"
docker push "aidedaijiayang/mocaca-backend:latest"

echo "推送前端镜像到DockerHub..."
docker push "$FRONTEND_IMAGE"
docker push "aidedaijiayang/mocaca-frontend:latest"

echo "=== 镜像发布完成 ==="
echo "✅ 后端镜像已发布:"
echo "   - aidedaijiayang/mocaca-backend:$VERSION"
echo "   - aidedaijiayang/mocaca-backend:latest"

echo "✅ 前端镜像已发布:"
echo "   - aidedaijiayang/mocaca-frontend:$VERSION"
echo "   - aidedaijiayang/mocaca-frontend:latest"

echo ""
echo "镜像查看地址:"
echo "后端: https://hub.docker.com/r/aidedaijiayang/mocaca-backend"
echo "前端: https://hub.docker.com/r/aidedaijiayang/mocaca-frontend"