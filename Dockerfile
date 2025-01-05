FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖和ffmpeg
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 安装Python包
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 创建上传目录
RUN mkdir -p uploads && chmod 777 uploads

# 复制应用代码
COPY . .

# 设置环境变量
ENV PORT=10000
ENV PATH="/usr/bin:${PATH}"

# 验证ffmpeg安装
RUN ffmpeg -version

# 暴露端口
EXPOSE ${PORT}

# 运行应用
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 ranking_app:app