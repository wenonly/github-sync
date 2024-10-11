# github-sync

使用 docker 定时同步 github 源码到 nas 中，每天凌晨 1 点同步

## 使用

```bash
docker build -t github-sync .
docker run -d --name github-sync \
  -e GITHUB_TOKEN=你的GitHub令牌 \
  -e GITHUB_USER=你的GitHub用户名 \
  -v /path/to/local/data:/app/data \
  github-sync
```

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
