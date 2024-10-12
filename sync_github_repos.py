from email.message import EmailMessage
import os
import requests
from git import Repo, RemoteProgress
import sys
import schedule
import time
from datetime import datetime, timedelta
import pytz
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

# 获取 GitHub token
token = os.getenv("GITHUB_TOKEN")
headers = {"Authorization": f"token {token}"}

# GitHub 用户名
username = os.getenv("GITHUB_USER")

# 获取仓库列表
repos_url = f"https://api.github.com/users/{username}/repos"

# 确保 data 目录存在
data_dir = "data"
if not os.path.exists(data_dir):
    os.makedirs(data_dir)


class CloneProgress(RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=""):
        if max_count:
            percentage = f"{cur_count / max_count * 100:.2f}%"
            sys.stdout.write(f"\r克隆进度: {percentage}")
            sys.stdout.flush()


def send_email(subject, message):
    # 获取环境变量
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    sender = os.getenv("EMAIL_SENDER")
    receiver = os.getenv("EMAIL_RECEIVER")

    # 检查必要的环境变量
    required_vars = [
        "SMTP_SERVER",
        "SMTP_USERNAME",
        "SMTP_PASSWORD",
        "EMAIL_SENDER",
        "EMAIL_RECEIVER",
    ]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(f"缺少必要的环境变量: {', '.join(missing_vars)}")

    # 打印配置信息（不包括密码）
    print(
        f"SMTP 配置: 服务器={smtp_server}, 端口={smtp_port}, 用户名={smtp_username}, 发件人={sender}, 收件人={receiver}"
    )

    # 创建邮件消息
    msg = EmailMessage()
    msg.set_content(message)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    print(msg)

    # 返回邮件消息和SMTP配置
    return msg, {
        "server": smtp_server,
        "port": smtp_port,
        "username": smtp_username,
        "password": smtp_password,
    }


def check_token_validity():
    response = requests.get("https://api.github.com/user", headers=headers)
    if response.status_code != 200:
        # 检查是否配置了所有必要的邮件环境变量
        required_vars = [
            "SMTP_SERVER",
            "SMTP_PORT",
            "SMTP_USERNAME",
            "SMTP_PASSWORD",
            "EMAIL_SENDER",
            "EMAIL_RECEIVER",
        ]
        if all(os.getenv(var) for var in required_vars):
            msg, smtp_config = send_email(
                "GitHub Token 过期提醒",
                "您在 github-sync 服务中配置的 GitHub Token 已过期，请更新。",
            )
            try:
                with smtplib.SMTP(smtp_config["server"], smtp_config["port"]) as server:
                    server.starttls()
                    server.login(smtp_config["username"], smtp_config["password"])
                    server.send_message(msg)
                    server.quit()  # 显式关闭连接
                print("邮件发送成功")
            except smtplib.SMTPException as e:
                print(f"SMTP错误: {str(e)}")
            except Exception as e:
                print(f"发送邮件时发生未知错误: {str(e)}")
        else:
            print("未配置邮件相关环境变量，跳过发送邮件流程")
        return False
    return True


def sync_github_repos():
    if not check_token_validity():
        print("GitHub Token 已过期，同步操作已取消。")
        return

    repos_response = requests.get(repos_url, headers=headers)
    repos_data = repos_response.json()
    # 遍历仓库并克隆或拉取
    for repo in repos_data:
        repo_name = repo["name"]
        repo_url = f"https://{token}@github.com/{username}/{repo_name}.git"
        repo_path = os.path.join(data_dir, repo_name)

        print(f"正在克隆或更新 {username}/{repo_name}")

        if not os.path.exists(repo_path):
            print(f"正在克隆 {username}/{repo_name} 的所有分支")
            Repo.clone_from(repo_url, repo_path, progress=CloneProgress())
            repo = Repo(repo_path)
            for remote_branch in repo.remote().refs:
                branch_name = remote_branch.remote_head
                if branch_name != "HEAD":
                    repo.create_head(branch_name, remote_branch).set_tracking_branch(
                        remote_branch
                    )
            print("\n克隆完成")
        else:
            print(f"{repo_name} 已存在，正在拉取所有分支的最新更改...")
            repo = Repo(repo_path)
            repo.git.fetch("--all")
            for remote_branch in repo.remote().refs:
                branch_name = remote_branch.remote_head
                if branch_name != "HEAD":
                    if branch_name in repo.heads:
                        local_branch = repo.heads[branch_name]
                        local_branch.set_tracking_branch(remote_branch)
                        local_branch.checkout()
                        repo.git.pull("origin", branch_name)
                    else:
                        repo.create_head(
                            branch_name, remote_branch
                        ).set_tracking_branch(remote_branch)
            print("所有分支更新完成")


def parse_time(time_str):
    """将时间字符串解析为小时、分钟和秒"""
    try:
        parts = time_str.split(":")
        if len(parts) == 3:
            return int(parts[0]), int(parts[1]), int(parts[2])
        elif len(parts) == 2:
            return int(parts[0]), int(parts[1]), 0
        else:
            raise ValueError
    except ValueError:
        print(f"无效的时间格式: {time_str}。使用默认值 01:00:00")
        return 1, 0, 0


def run_at_specified_time():
    # 从环境变量获取运行时间，默认为凌晨1点
    run_time = os.getenv("RUN_TIME", "01:00:00")
    run_hour, run_minute, run_second = parse_time(run_time)

    # 获取时区
    tz_name = os.getenv("TZ", "Asia/Shanghai")
    tz = pytz.timezone(tz_name)

    while True:
        now = datetime.now(tz)
        next_run = now.replace(
            hour=run_hour, minute=run_minute, second=run_second, microsecond=0
        )

        if now >= next_run:
            next_run += timedelta(days=1)

        time_until_next_run = (next_run - now).total_seconds()

        print(f"下次运行时间: {next_run}")
        print(f"等待时间: {time_until_next_run} 秒")

        time.sleep(time_until_next_run)
        sync_github_repos()


if __name__ == "__main__":
    sync_github_repos()
    run_at_specified_time()
