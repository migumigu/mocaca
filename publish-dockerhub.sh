#!/bin/bash

# DockerHub多架构镜像发布脚本
# 同时构建和推送x86和ARM架构的镜像到DockerHub

set -e

echo "=== DockerHub多架构镜像发布脚本 ==="

# 获取当前版本号
VERSION=$(git describe --tags --abbrev=0 2>/dev/null || echo "1.9.4")
# 去掉版本号中的v前缀
VERSION=${VERSION#v}
echo "当前版本: $VERSION"

# 检查前端目录是否存在
if [ ! -d "frontend" ]; then
    echo "警告: frontend 目录不存在，跳过前端构建"
    BUILD_FRONTEND=false
else
    BUILD_FRONTEND=true
fi

# 假设用户已登录DockerHub
echo "✅ DockerHub登录状态：用户已确保登录"

# 初始化多平台构建器
echo "初始化多平台构建器..."
docker buildx create --name multiarch --use --driver-opt network=host 2>/dev/null || true

# 重试函数
retry_command() {
    local max_attempts=3
    local attempt=1
    local delay=5
    
    while [ $attempt -le $max_attempts ]; do
        echo "尝试 $attempt/$max_attempts..."
        if "$@"; then
            echo "✅ 命令执行成功"
            return 0
        else
            echo "❌ 尝试 $attempt 失败，等待 ${delay}秒后重试..."
            sleep $delay
            ((attempt++))
            delay=$((delay * 2))  # 指数退避
        fi
    done
    
    echo "❌ 所有重试尝试均失败"
    return 1
}

echo "=== 开始构建和推送多架构镜像(v${VERSION}) ==="

# 构建和推送后端多架构镜像
echo "构建和推送后端多架构镜像..."
(cd backend && \
docker buildx build --platform linux/amd64,linux/arm64 \
  -t aidedaijiayang/mocaca-backend:${VERSION} \
  -t aidedaijiayang/mocaca-backend:latest \
  --push .) || exit 1

# 构建和推送前端多架构镜像（如果存在）
if [ "$BUILD_FRONTEND" = true ]; then
    echo "构建和推送前端多架构镜像..."
    (cd frontend && \
    docker buildx build --platform linux/amd64,linux/arm64 \
      -t aidedaijiayang/mocaca-frontend:${VERSION} \
      -t aidedaijiayang/mocaca-frontend:latest \
      --push .) || exit 1
else
    echo "跳过前端镜像构建"
fi

echo "=== 多架构镜像发布完成 ==="
echo "✅ 后端多架构镜像已发布:"
echo "   - aidedaijiayang/mocaca-backend:${VERSION} (支持x86和ARM)"
echo "   - aidedaijiayang/mocaca-backend:latest (支持x86和ARM)"

if [ "$BUILD_FRONTEND" = true ]; then
    echo "✅ 前端多架构镜像已发布:"
    echo "   - aidedaijiayang/mocaca-frontend:${VERSION} (支持x86和ARM)"
    echo "   - aidedaijiayang/mocaca-frontend:latest (支持x86和ARM)"
fi

echo ""
echo "镜像查看地址:"
echo "后端: https://hub.docker.com/r/aidedaijiayang/mocaca-backend"
echo "前端: https://hub.docker.com/r/aidedaijiayang/mocaca-frontend"

echo ""
echo "用户下载示例（自动匹配架构）:"
echo "docker pull aidedaijiayang/mocaca-backend:latest"
echo "docker pull aidedaijiayang/mocaca-frontend:latest"

echo ""
echo "架构验证命令:"
echo "docker buildx imagetools inspect aidedaijiayang/mocaca-backend:latest"