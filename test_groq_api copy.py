# pipeline {
#     agent any

#     environment {
#         VPS = 'ubuntu@15.235.210.227'        // Your VPS user and IP
#         SSH_KEY = credentials('vps-ssh')     // Jenkins credential ID for VPS SSH
#     }

#     stages {
#         stage('Pull from GitHub') {
#             steps {
#                 echo "Pulling latest code from GitHub..."
#                 git branch: 'main',
#                     credentialsId: 'github-creds',   // Jenkins SSH key for GitHub
#                     url: 'git@github.com:ChanukaWelagedara/smart-recruitment-ai.git'
#             }
#         }

#         stage('Deploy to VPS') {
#             steps {
#                 echo "Deploying to VPS..."
#                 sshagent(['vps-ssh']) {
#                     sh """
#                     ssh -o StrictHostKeyChecking=no $VPS '
#                         set -e

#                         echo "Navigating to project directory..."
#                         cd ~/FYGP/smart-recruitment-ai || exit 1

#                         echo "Updating Git repository..."
#                         git fetch origin main
#                         git reset --hard origin/main
                        
#                         echo "Ensuring cv_chroma_db folder exists on VPS..."
#                         mkdir -p ~/FYGP/smart-recruitment-ai/cv_chroma_db

#                         echo "Stopping existing Docker container..."
#                         sudo docker compose down || true

#                         echo "Removing old images (optional, forces rebuild)..."
#                         sudo docker image prune -af

#                         echo "Building Docker image without cache..."
#                         sudo docker compose build --no-cache

#                         echo "Starting Docker container..."
#                         sudo docker compose up -d

#                         echo "Deployment complete!"
#                     '
#                     """
#                 }
#             }
#         }
#     }

#     post {
#         success {
#             echo "Pipeline finished successfully!"
#         }
#         failure {
#             echo "Pipeline failed. Check Jenkins logs for details."
#         }
#     }
# }
