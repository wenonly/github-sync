# github-sync

使用 docker 定时同步 github 源码到 nas 中，每天凌晨 1 点同步

## 使用

```bash
docker run -d --name github-sync \
  -e GITHUB_TOKEN=你的GitHub令牌 \
  -e GITHUB_USER=你的GitHub用户名 \
  -v /path/to/local/data:/app/data \
  github-sync
```

## 环境变量配置

| 环境变量       | 描述                | 默认值        |
| -------------- | ------------------- | ------------- |
| GITHUB_TOKEN   | GitHub 个人访问令牌 | 无            |
| GITHUB_USER    | GitHub 用户名       | 无            |
| RUN_TIME       | 每日同步时间        | 01:00:00      |
| TZ             | 时区                | Asia/Shanghai |
| SMTP_SERVER    | SMTP 服务器地址     | smtp.qq.com   |
| SMTP_PORT      | SMTP 服务器端口     | 587           |
| SMTP_USERNAME  | SMTP 用户名         | 无            |
| SMTP_PASSWORD  | SMTP 密码           | 无            |
| EMAIL_SENDER   | 发件人邮箱地址      | 无            |
| EMAIL_RECEIVER | 收件人邮箱地址      | 无            |

## 注意事项

- 需要设置 GITHUB_TOKEN 和 GITHUB_USER 环境变量
- 需要挂载一个本地目录到容器中的/app/data 目录

## 编译

```bash
docker build -t github-sync .
```

如果需要编译多平台，使用下面的命令

```bash
docker buildx build --platform linux/amd64,linux/arm64 -t github-sync:latest .
```
