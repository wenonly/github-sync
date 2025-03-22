pipeline {
    agent {
        docker {
            image 'python:3.13.2'
        }
    }

    environment {
        // 从 Jenkins 凭据中获取环境变量
        GITHUB_TOKEN = credentials('github-token')
        GITHUB_USER = 'wenonly'
    }

    stages {
        stage('Run Sync') {
            steps {
                script {
                    sh 'python --version'
                    sh 'pip install --no-cache-dir -r requirements.txt'
                    sh 'python sync_github_repos.py'
                }
            }
        }
    }

    post {
        success {
            emailext (
                to: 'taowenaio@outlook.com',
                subject: "同步成功: ${currentBuild.fullDisplayName}",
                body: """
                    <h2>同步成功通知</h2>
                    <p>项目: ${env.JOB_NAME}</p>
                    <p>构建编号: ${env.BUILD_NUMBER}</p>
                    <p>构建 URL: <a href='${env.BUILD_URL}'>${env.BUILD_URL}</a></p>
                    <p>查看控制台输出: <a href='${env.BUILD_URL}console'>${env.BUILD_URL}console</a></p>
                """,
                mimeType: 'text/html',
                attachLog: true
            )
        }
        failure {
            emailext (
                to: 'taowenaio@outlook.com',
                subject: "同步失败: ${currentBuild.fullDisplayName}",
                body: """
                    <h2>同步失败通知</h2>
                    <p>项目: ${env.JOB_NAME}</p>
                    <p>构建编号: ${env.BUILD_NUMBER}</p>
                    <p>构建 URL: <a href='${env.BUILD_URL}'>${env.BUILD_URL}</a></p>
                    <p>查看控制台输出: <a href='${env.BUILD_URL}console'>${env.BUILD_URL}console</a></p>
                """,
                mimeType: 'text/html',
                attachLog: true
            )
        }
    }
}
