# 多阶段构建优化版
# 阶段1: 构建环境 (使用完整Alpine镜像)
FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/python:3.12-alpine as builder

# 配置华为云PyPI镜像
RUN echo "[global]" > /etc/pip.conf && \
    echo "index-url = https://repo.huaweicloud.com/repository/pypi/simple" >> /etc/pip.conf && \
    echo "trusted-host = repo.huaweicloud.com" >> /etc/pip.conf

# 安装系统构建依赖
RUN apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    jpeg-dev \
    zlib-dev \
    ffmpeg

WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt gunicorn

# 阶段2: 运行时环境 (最小化镜像)
FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/python:3.12-alpine

# 仅安装运行时依赖
RUN apk add --no-cache jpeg-dev zlib-dev ffmpeg

# 创建非root用户
RUN adduser -D appuser && mkdir /app && chown appuser:appuser /app
USER appuser
WORKDIR /app

# 从构建阶段复制已安装的Python包
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local
COPY --chown=appuser:appuser . .

# 确保用户本地bin在PATH中
ENV PATH=/home/appuser/.local/bin:$PATH
ENV FLASK_APP=app.py FLASK_ENV=production

EXPOSE 5003
CMD ["gunicorn", "--bind", "0.0.0.0:5003", "app:app"]