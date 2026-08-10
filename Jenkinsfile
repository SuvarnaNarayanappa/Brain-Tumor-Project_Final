pipeline {
    agent any

    environment {
        STORAGE_ACCOUNT   = 'btbrainmodel2026'
        STORAGE_CONTAINER = 'btcont'
        MODEL_BLOB        = 'models/bt_resnet50_model.pt'

        SOURCE_MODEL = '/home/azureuser/Brain-Tumor-Project/models/bt_resnet50_model.pt'

        ACR_NAME   = 'btbrainacr2026'
        ACR_LOGIN  = 'btbrainacr2026.azurecr.io'
        IMAGE_NAME = 'brain-tumor-detection'
        IMAGE_TAG  = 'latest'

        CONTAINER_NAME = 'bt-app'
        HOST_PORT      = '5000'
        CONTAINER_PORT = '5000'
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'GitHub checkout successful'
            }
        }

        stage('Azure Login') {
            steps {
                sh '''
                    echo "Logging in to Azure..."

                    az login --identity --allow-no-subscriptions

                    echo "Azure login successful."
                '''
            }
        }

        stage('Upload Model to Azure Blob') {
            steps {
                sh '''
                    echo "Checking model..."

                    ls -lh "$SOURCE_MODEL"

                    echo "Uploading model to Azure Blob..."

                    az storage blob upload \
                      --account-name "$STORAGE_ACCOUNT" \
                      --container-name "$STORAGE_CONTAINER" \
                      --name "$MODEL_BLOB" \
                      --file "$SOURCE_MODEL" \
                      --auth-mode login \
                      --overwrite

                    echo "Model upload completed."
                '''
            }
        }

        stage('Verify Blob') {
            steps {
                sh '''
                    echo "Verifying model in Azure Blob..."

                    az storage blob show \
                      --account-name "$STORAGE_ACCOUNT" \
                      --container-name "$STORAGE_CONTAINER" \
                      --name "$MODEL_BLOB" \
                      --auth-mode login \
                      --query "{Name:name,Size:properties.contentLength}" \
                      -o table
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    echo "Building Docker image..."

                    docker build \
                      -t "$ACR_LOGIN/$IMAGE_NAME:$IMAGE_TAG" .

                    echo "Docker image built successfully."

                    docker images "$ACR_LOGIN/$IMAGE_NAME"
                '''
            }
        }

        stage('Login to ACR') {
            steps {
                sh '''
                    echo "Logging in to Azure Container Registry..."

                    az acr login --name "$ACR_NAME"

                    echo "ACR login successful."
                '''
            }
        }

        stage('Push to ACR') {
            steps {
                sh '''
                    echo "Pushing Docker image to ACR..."

                    docker push "$ACR_LOGIN/$IMAGE_NAME:$IMAGE_TAG"

                    echo "Docker image successfully pushed to ACR."
                '''
            }
        }

        stage('Deploy Container') {
            steps {
                sh '''
                    echo "Stopping old container if it exists..."

                    docker rm -f "$CONTAINER_NAME" 2>/dev/null || true

                    echo "Pulling latest image from ACR..."

                    docker pull "$ACR_LOGIN/$IMAGE_NAME:$IMAGE_TAG"

                    echo "Starting new container..."

                    docker run -d \
                      --name "$CONTAINER_NAME" \
                      --restart unless-stopped \
                      -p 127.0.0.1:$HOST_PORT:$CONTAINER_PORT \
                      -e AZURE_STORAGE_ACCOUNT="$STORAGE_ACCOUNT" \
                      -e AZURE_STORAGE_CONTAINER="$STORAGE_CONTAINER" \
                      -e MODEL_PATH=/app/models/bt_resnet50_model.pt \
                      "$ACR_LOGIN/$IMAGE_NAME:$IMAGE_TAG"

                    echo "Container started."

                    docker ps --filter "name=$CONTAINER_NAME"
                '''
            }
        }

        stage('Health Check') {
            steps {
                sh '''
                    echo "Waiting for application to become healthy..."

                    sleep 15

                    docker inspect "$CONTAINER_NAME" \
                      --format '{{.State.Status}} | {{.State.Health.Status}}'

                    echo "Testing application..."

                    curl -f http://127.0.0.1:$HOST_PORT/ || exit 1

                    echo "Application health check successful."
                '''
            }
        }
    }

    post {
        success {
            echo '========================================='
            echo 'Brain Tumor application deployed successfully!'
            echo '========================================='
        }

        failure {
            echo '========================================='
            echo 'Deployment failed. Check the Jenkins console log.'
            echo '========================================='
        }
    }
}
