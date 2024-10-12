# 使用官方 Python 运行时作为父镜像
FROM python:3.13.0-slim

# 设置工作目录
WORKDIR /app

# 安装必要的系统包并设置时区
RUN apt-get update && apt-get install -y git tzdata && \
    ln -fs /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata

# 复制当前目录下的所有文件到容器中的 /app 目录下
COPY . /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Shanghai
ENV RUN_TIME=01:00:00
ENV GITHUB_TOKEN=123
ENV GITHUB_USER=123
ENV SMTP_SERVER=smtp.qq.com
ENV SMTP_PORT=587
ENV SMTP_USERNAME=
ENV SMTP_PASSWORD=
ENV EMAIL_SENDER=
ENV EMAIL_RECEIVER=

# 安装任何需要的 Python 包
RUN pip install --no-cache-dir requests GitPython schedule pytz

# 设置容器启动时执行的命令
CMD ["python", "sync_github_repos.py"]