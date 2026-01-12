pipeline {
    agent any
    
    environment {
        PATH = "/var/jenkins_home/bin:${env.PATH}"
    }
    
    stages {
        stage('Pull from GitHub') {
            steps {
                echo "Pulling latest code from GitHub..."
                // Code is automatically pulled when using SCM in Jenkins job configuration
            }
        }
        
        stage('Deploy Locally') {
            steps {
                echo "Deploying locally..."
                withCredentials([string(credentialsId: 'groq-api-key', variable: 'GROQ_API_KEY')]) {
                    sh '''
                        set -e
                        
                        echo "Creating .env file..."
                        cat > .env << EOF
GROQ_API_KEY=${GROQ_API_KEY}
EOF
                        
                        echo "Ensuring cv_chroma_db folder exists..."
                        mkdir -p cv_chroma_db results data temp_uploads
                        
                        echo "Stopping existing Docker container..."
                        docker-compose down || true
                        
                        echo "Building Docker image (using cache)..."
                        docker-compose build
                        
                        echo "Starting Docker container..."
                        docker-compose up -d
                        
                        echo "Deployment complete!"
                    '''
                }
            }
        }
    }
    
    post {
        success {
            echo "Pipeline finished successfully!"
        }
        failure {
            echo "Pipeline failed. Check Jenkins logs for details."
        }
        always {
            script {
                sh '''
                    # Clean up .env file for security
                    rm -f .env || true
                '''
            }
        }
    }
}