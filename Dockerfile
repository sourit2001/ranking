FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖和多个中文字体
RUN apt-get update && \
    apt-get install -y ffmpeg fonts-noto-cjk fonts-noto-cjk-extra fonts-wqy-microhei fonts-wqy-zenhei && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 安装Python包
COPY requirements.txt .
RUN pip install -r requirements.txt

# 创建上传目录
RUN mkdir -p uploads

# 复制应用代码
COPY . .

# 设置环境变量
ENV PYTHONIOENCODING=utf8
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# 暴露端口
EXPOSE 5000

# 运行应用
CMD ["python", "ranking_app.py"]