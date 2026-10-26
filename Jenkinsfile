pipeline {
    agent any

    environment {
        HEADLESS = '1'
        CHROME_BIN = '/usr/bin/chromium'
        CHROMEDRIVER_PATH = '/usr/bin/chromedriver'
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/kasperskaaa/lab8-cicd-jenkins-behave.git'
            }
        }

        stage('Static Code Analysis') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install pylint
                    pylint --disable=C,R features/ | tee pylint_report.txt || true
                    grep "Your code has been rated at" pylint_report.txt || true
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    . venv/bin/activate
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run UI Tests') {
            steps {
                catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                    sh '''
                        . venv/bin/activate
                        behave -f allure_behave.formatter:AllureFormatter -o allure-results
                    '''
                }
            }
        }
    }

    post {
        always {
            allure includeProperties: false, jdk: '', results: [[path: 'allure-results']]
            archiveArtifacts artifacts: 'pylint_report.txt', allowEmptyArchive: true
        }
        failure {
            echo 'Pipeline failed.'
        }
    }
}
