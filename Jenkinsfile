pipeline {
    agent any

    environment {
        STORAGE_ACCOUNT = 'btbrainmodel2026'
        STORAGE_CONTAINER = 'btcont'
        MODEL_BLOB = 'models/bt_resnet50_model.pt'

        SOURCE_MODEL = '/home/azureuser/Brain-Tumor-Project/models/bt_resnet50_model.pt'
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
                    az login --identity --allow-no-subscriptions
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
                      -t brain-tumor-detection:latest .

                    echo "Docker image built successfully."

                    docker images brain-tumor-detection:latest
                '''
            }
        }
    }
}
