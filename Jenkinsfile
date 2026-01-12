pipeline {
    agent any
    
    environment {
        COMPOSE_FILE = 'docker-compose.prod.yml'
        SERVICE_NAME = 'smart-ai'
        APP_PORT = '5000'
    }
    
    stages {
        stage('Checkout') {
            steps {
                script {
                    // Check current directory structure
                    sh '''
                        echo "Working directory: $(pwd)"
                        echo "Contents:"
                        ls -la
                        echo "Looking for required files:"
                        ls -la Dockerfile docker-compose.prod.yml .env.template || echo "Some files missing"
                    '''
                }
            }
        }
        
        stage('Environment Check') {
            steps {
                script {
                    // Verify .env file exists
                    sh '''
                        if [ ! -f .env ]; then
                            echo "Error: .env file not found!"
                            echo "Please create .env file from .env.template and configure your API keys"
                            if [ -f .env.template ]; then
                                echo "Found .env.template - you can copy it to .env and configure"
                                echo "Contents of .env.template:"
                                cat .env.template
                            fi
                            exit 1
                        fi
                        echo ".env file found"
                        
                        # Create required directories
                        mkdir -p results cv_chroma_db data temp_uploads
                        echo "Required directories created"
                    '''
                }
            }
        }
        
        stage('Stop Previous Deployment') {
            steps {
                script {
                    // Stop and remove existing services
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
                    // Build and deploy using docker-compose
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
                    // Wait for service to be ready and perform health check
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
                    // Clean up unused Docker resources
                    sh '''
                        echo "Cleaning up unused Docker resources..."
                        
                        # Remove unused images (keep recent ones)
                        docker image prune -f
                        
                        # Remove unused volumes (be careful with this)
                        docker volume prune -f
                        
                        # Remove unused networks
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
                // Show deployment status
                sh '''
                    echo "=== Deployment Status ==="
                    docker-compose -f ${COMPOSE_FILE} ps
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
                    echo "1. Check .env file configuration"
                    echo "2. Verify Docker service is running"
                    echo "3. Check port ${APP_PORT} availability"
                '''
            }
        }
    }
}