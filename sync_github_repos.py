import os
import requests
from git import Repo, RemoteProgress
import sys
import schedule
import time
from datetime import datetime, timedelta
import pytz

# 获取 GitHub token
token = os.environ.get('GITHUB_TOKEN')
headers = {'Authorization': f'token {token}'}

# GitHub 用户名
username = os.environ.get('GITHUB_USER')

# 获取仓库列表
repos_url = f'https://api.github.com/users/{username}/repos'
repos_response = requests.get(repos_url, headers=headers)
repos_data = repos_response.json()

# 确保 data 目录存在
data_dir = 'data'
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

class CloneProgress(RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=''):
        if max_count:
            percentage = f'{cur_count / max_count * 100:.2f}%'
            sys.stdout.write(f'\r克隆进度: {percentage}')
            sys.stdout.flush()

def sync_github_repos():
    # 遍历仓库并克隆或拉取
    for repo in repos_data:
        repo_name = repo['name']
        repo_url = f'https://{token}@github.com/{username}/{repo_name}.git'
        repo_path = os.path.join(data_dir, repo_name)
        
        print(f'正在克隆或更新 {username}/{repo_name}')
        
        if not os.path.exists(repo_path):
            print(f'正在克隆 {username}/{repo_name} 的所有分支')
            Repo.clone_from(repo_url, repo_path, progress=CloneProgress())
            repo = Repo(repo_path)
            for remote_branch in repo.remote().refs:
                branch_name = remote_branch.remote_head
                if branch_name != 'HEAD':
                    repo.create_head(branch_name, remote_branch).set_tracking_branch(remote_branch)
            print('\n克隆完成')
        else:
            print(f'{repo_name} 已存在，正在拉取所有分支的最新更改...')
            repo = Repo(repo_path)
            repo.git.fetch('--all')
            for remote_branch in repo.remote().refs:
                branch_name = remote_branch.remote_head
                if branch_name != 'HEAD':
                    if branch_name in repo.heads:
                        local_branch = repo.heads[branch_name]
                        local_branch.set_tracking_branch(remote_branch)
                        local_branch.checkout()
                        repo.git.pull('origin', branch_name)
                    else:
                        repo.create_head(branch_name, remote_branch).set_tracking_branch(remote_branch)
            print('所有分支更新完成')

def run_at_shanghai_1am():
    while True:
        shanghai_tz = pytz.timezone('Asia/Shanghai')
        now = datetime.now(shanghai_tz)
        next_run = now.replace(hour=1, minute=0, second=0, microsecond=0)
        if now.time() >= next_run.time():
            next_run += timedelta(days=1)
        time_until_next_run = (next_run - now).total_seconds()
        
        print(f"下次运行时间: {next_run}")
        print(f"等待时间: {time_until_next_run} 秒")
        
        time.sleep(time_until_next_run)
        sync_github_repos()

if __name__ == "__main__":
    sync_github_repos()
    run_at_shanghai_1am()