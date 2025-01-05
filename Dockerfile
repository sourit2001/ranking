FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖和中文字体
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    fonts-noto-cjk \
    fonts-noto-cjk-extra \
    fonts-wqy-zenhei \
    fonts-wqy-microhei && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 安装Python包
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 创建上传目录
RUN mkdir -p uploads && chmod 777 uploads

# 复制应用代码
COPY . .

# 设置环境变量
ENV PORT=10000
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 暴露端口
EXPOSE 10000

# 运行应用
CMD ["python", "ranking_app.py"]