pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                echo 'GitHub checkout successful'
            }
        }

        stage('Environment Test') {
            steps {
                sh 'whoami'
                sh 'java -version'
                sh 'docker --version'
                sh 'az --version'
            }
        }
    }
}
