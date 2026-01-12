pipeline {
    agent any
    
    environment {
        COMPOSE_FILE = 'docker-compose.prod.yml'
        SERVICE_NAME = 'smart-ai'
        APP_PORT = '5000'
        PATH = "/var/jenkins_home/bin:${env.PATH}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                script {
                    sh '''
                        echo "Working directory: $(pwd)"
                        echo "PATH: $PATH"
                        echo "Checking docker-compose:"
                        which docker-compose || echo "docker-compose not found in PATH"
                        docker-compose --version || echo "docker-compose command failed"
                        
                        echo "Contents:"
                        ls -la
                        echo "Looking for required files:"
                        ls -la Dockerfile docker-compose.prod.yml || echo "Some files missing"
                    '''
                }
            }
        }
        
        stage('Environment Setup') {
            steps {
                script {
                    withCredentials([string(credentialsId: 'groq-api-key', variable: 'GROQ_API_KEY')]) {
                        sh '''
                            echo "Creating .env file from Jenkins secrets..."
                            cat > .env << EOF
# Smart Recruitment AI Environment Variables
GROQ_API_KEY=${GROQ_API_KEY}
FLASK_ENV=production
FLASK_DEBUG=False
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=./temp_uploads
SECRET_KEY=$(openssl rand -hex 32)
LOG_LEVEL=INFO
PYTHONUNBUFFERED=1
EOF
                            echo ".env file created successfully"
                            
                            # Create required directories
                            mkdir -p results cv_chroma_db data temp_uploads
                            echo "Required directories created"
                            
                            # Verify API key is set (show first 10 characters only for security)
                            echo "GROQ API Key configured: ${GROQ_API_KEY:0:10}..."
                        '''
                    }
                }
            }
        }
        
        stage('Stop Previous Deployment') {
            steps {
                script {
                    sh '''
                        echo "Stopping existing deployment..."
                        docker-compose -f ${COMPOSE_FILE} down || true
                        echo "Previous deployment stopped"
                    '''
                }
            }
        }
        
        stage('Build and Deploy') {
            steps {
                script {
                    sh '''
                        echo "Building and deploying application..."
                        docker-compose -f ${COMPOSE_FILE} up -d --build
                        echo "Application deployed successfully"
                    '''
                }
            }
        }
        
        stage('Health Check') {
            steps {
                script {
                    sh '''
                        echo "Waiting for application to start..."
                        sleep 15
                        
                        # Check if service is running
                        if ! docker-compose -f ${COMPOSE_FILE} ps | grep -q "Up"; then
                            echo "Service failed to start!"
                            echo "Service status:"
                            docker-compose -f ${COMPOSE_FILE} ps
                            echo "Service logs:"
                            docker-compose -f ${COMPOSE_FILE} logs
                            exit 1
                        fi
                        
                        # Test application health endpoint
                        max_attempts=30
                        attempt=0
                        
                        echo "Testing application health..."
                        while [ $attempt -lt $max_attempts ]; do
                            if curl -f http://localhost:${APP_PORT}/health > /dev/null 2>&1; then
                                echo "✓ Application health check passed!"
                                curl -s http://localhost:${APP_PORT}/health | python3 -m json.tool || echo "Health check response received"
                                break
                            fi
                            
                            attempt=$((attempt + 1))
                            echo "Health check attempt $attempt/$max_attempts..."
                            sleep 3
                        done
                        
                        if [ $attempt -eq $max_attempts ]; then
                            echo "✗ Application health check failed after $max_attempts attempts"
                            echo "Container logs:"
                            docker-compose -f ${COMPOSE_FILE} logs ${SERVICE_NAME}
                            exit 1
                        fi
                    '''
                }
            }
        }
        
        stage('Cleanup') {
            steps {
                script {
                    sh '''
                        echo "Cleaning up unused Docker resources..."
                        docker image prune -f
                        docker volume prune -f
                        docker network prune -f
                        echo "Cleanup completed"
                    '''
                }
            }
        }
    }
    
    post {
        always {
            script {
                sh '''
                    echo "=== Deployment Status ==="
                    docker-compose -f ${COMPOSE_FILE} ps
                    
                    # Clean up .env file for security
                    rm -f .env
                    echo ".env file cleaned up"
                '''
            }
        }
        
        success {
            script {
                sh '''
                    echo "🎉 Deployment successful!"
                    echo ""
                    echo "=== Service Information ==="
                    echo "Application URL: http://localhost:${APP_PORT}"
                    echo "Health Check: http://localhost:${APP_PORT}/health"
                    echo ""
                    echo "=== Management Commands ==="
                    echo "View logs: docker-compose -f ${COMPOSE_FILE} logs -f"
                    echo "Stop service: docker-compose -f ${COMPOSE_FILE} down"
                    echo "Restart service: docker-compose -f ${COMPOSE_FILE} restart"
                    echo ""
                    echo "=== Recent Logs ==="
                    docker-compose -f ${COMPOSE_FILE} logs --tail=20
                '''
            }
        }
        
        failure {
            script {
                sh '''
                    echo "❌ Deployment failed!"
                    echo ""
                    echo "=== Service Status ==="
                    docker-compose -f ${COMPOSE_FILE} ps
                    echo ""
                    echo "=== Service Logs ==="
                    docker-compose -f ${COMPOSE_FILE} logs
                    echo ""
                    echo "=== Troubleshooting ==="
                    echo "1. Verify GROQ API key is configured in Jenkins credentials"
                    echo "2. Check Docker service is running"
                    echo "3. Check port ${APP_PORT} availability"
                    
                    # Clean up .env file even on failure
                    rm -f .env
                '''
            }
        }
    }
}