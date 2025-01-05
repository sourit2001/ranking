FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 安装Python包
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 创建上传目录
RUN mkdir -p uploads

# 复制应用代码
COPY . .

# 设置环境变量
ENV PORT=10000

# 暴露端口
EXPOSE ${PORT}

# 运行应用
CMD gunicorn --bind 0.0.0.0:$PORT ranking_app:app