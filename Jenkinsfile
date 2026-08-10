pipeline {
    agent any

    environment {
        // Azure Blob Storage
        STORAGE_ACCOUNT   = 'btbrainmodel2026'
        STORAGE_CONTAINER = 'btcont'
        MODEL_BLOB        = 'models/bt_resnet50_model.pt'

        // Model location on Azure VM
        SOURCE_MODEL = '/home/azureuser/Brain-Tumor-Project/models/bt_resnet50_model.pt'

        // Azure Container Registry
        ACR_NAME   = 'btbrainacr2026'
        ACR_LOGIN  = 'btbrainacr2026.azurecr.io'
        IMAGE_NAME = 'brain-tumor-detection'
        IMAGE_TAG  = 'latest'

        // Docker container
        CONTAINER_NAME = 'bt-app'
        HOST_PORT      = '5000'
        CONTAINER_PORT = '5000'
    }

    stages {

        stage('Checkout Code') {
            steps {
                echo 'GitHub checkout completed.'
            }
        }

        stage('Upload Model (.pt)') {
            steps {
                sh '''
                    set -e

                    echo "========================================="
                    echo "Checking .pt model"
                    echo "========================================="

                    ls -lh "$SOURCE_MODEL"

                    echo "Uploading model to Azure Blob Storage..."

                    az storage blob upload \
                      --account-name "$STORAGE_ACCOUNT" \
                      --container-name "$STORAGE_CONTAINER" \
                      --name "$MODEL_BLOB" \
                      --file "$SOURCE_MODEL" \
                      --auth-mode login \
                      --overwrite

                    echo "Model upload completed successfully."
                '''
            }
        }

        stage('Verify Model') {
            steps {
                sh '''
                    set -e

                    echo "========================================="
                    echo "Verifying .pt model in Azure Blob Storage"
                    echo "========================================="

                    az storage blob show \
                      --account-name "$STORAGE_ACCOUNT" \
                      --container-name "$STORAGE_CONTAINER" \
                      --name "$MODEL_BLOB" \
                      --auth-mode login \
                      --query "{Name:name,Size:properties.contentLength}" \
                      -o table

                    echo "Model verification completed successfully."
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    set -e

                    echo "========================================="
                    echo "Building Docker image"
                    echo "========================================="

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
                    set -e

                    echo "========================================="
                    echo "Logging in to Azure Container Registry"
                    echo "========================================="

                    az acr login --name "$ACR_NAME"

                    echo "ACR login successful."
                '''
            }
        }

        stage('Push Image to ACR') {
            steps {
                sh '''
                    set -e

                    echo "========================================="
                    echo "Pushing Docker image to ACR"
                    echo "========================================="

                    docker push "$ACR_LOGIN/$IMAGE_NAME:$IMAGE_TAG"

                    echo "Docker image successfully pushed to ACR."
                '''
            }
        }

        stage('Deploy Container') {
            steps {
                sh '''
                    set -e

                    echo "========================================="
                    echo "Deploying Brain Tumor application"
                    echo "========================================="

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
                    set -e

                    echo "========================================="
                    echo "Checking application health"
                    echo "========================================="

                    echo "Waiting for application to become healthy..."

                    sleep 15

                    echo "Container status:"

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
            echo '''
=========================================
       DEPLOYMENT SUCCESSFUL
=========================================

GitHub
   |
   v
Jenkins
   |
   +----> Upload .pt -> Azure Blob Storage
   |
   +----> Verify Model
   |
   +----> Build Docker Image
   |
   +----> Push Image -> Azure ACR
   |
   +----> Deploy -> bt-app
   |
   +----> Health Check

=========================================
'''
        }

        failure {
            echo '''
=========================================
        DEPLOYMENT FAILED
=========================================

Check the failed Jenkins stage
and review the Console Output.

=========================================
'''
        }
    }
}
