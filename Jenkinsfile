// Declarative pipeline: lint -> test -> build image -> smoke test -> push -> deploy.
//
// Jenkins prerequisites:
//   - Agent with Docker and Python 3 installed (label: docker)
//   - Credentials (Manage Jenkins > Credentials):
//       'dockerhub-creds'  Username/password for the registry
//       'deploy-ssh-key'   SSH private key for the deploy host (only if deploying)
//   - Plugins: Pipeline, Git, Credentials Binding, SSH Agent, JUnit, Cobertura/Coverage (optional)
pipeline {
    agent { label 'docker' }

    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '20'))
        timeout(time: 30, unit: 'MINUTES')
    }

    parameters {
        booleanParam(name: 'DEPLOY', defaultValue: false, description: 'Deploy after a successful build on main')
    }

    environment {
        REGISTRY    = 'docker.io'
        IMAGE_REPO  = 'your-dockerhub-user/flask-jenkins-app'   // <-- change me
        IMAGE_TAG   = "${env.BUILD_NUMBER}"
        DEPLOY_HOST = 'user@your-server-ip'                      // <-- change me
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Python') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements-dev.txt
                '''
            }
        }

        stage('Lint') {
            steps {
                sh '. .venv/bin/activate && flake8 app tests wsgi.py'
            }
        }

        stage('Test') {
            steps {
                sh '''
                    . .venv/bin/activate
                    pytest --junitxml=test-results.xml --cov=app --cov-report=xml
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'test-results.xml'
                    archiveArtifacts artifacts: 'coverage.xml', allowEmptyArchive: true
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build \
                        --build-arg APP_VERSION=${IMAGE_TAG} \
                        -t ${IMAGE_REPO}:${IMAGE_TAG} \
                        -t ${IMAGE_REPO}:latest .
                '''
            }
        }

        stage('Smoke Test Image') {
            steps {
                sh '''
                    docker rm -f smoke-${BUILD_NUMBER} >/dev/null 2>&1 || true
                    docker run -d --name smoke-${BUILD_NUMBER} -p 15000:5000 ${IMAGE_REPO}:${IMAGE_TAG}
                    for i in $(seq 1 15); do
                        if curl -fsS http://localhost:15000/health; then
                            echo "Smoke test passed"
                            exit 0
                        fi
                        sleep 2
                    done
                    echo "Smoke test failed"
                    docker logs smoke-${BUILD_NUMBER}
                    exit 1
                '''
            }
            post {
                always {
                    sh 'docker rm -f smoke-${BUILD_NUMBER} || true'
                }
            }
        }

        stage('Push Image') {
            when { branch 'main' }
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'REG_USER',
                    passwordVariable: 'REG_PASS'
                )]) {
                    sh '''
                        echo "$REG_PASS" | docker login ${REGISTRY} -u "$REG_USER" --password-stdin
                        docker push ${IMAGE_REPO}:${IMAGE_TAG}
                        docker push ${IMAGE_REPO}:latest
                        docker logout ${REGISTRY}
                    '''
                }
            }
        }

        stage('Deploy') {
            when {
                allOf {
                    branch 'main'
                    expression { params.DEPLOY }
                }
            }
            steps {
                sshagent(credentials: ['deploy-ssh-key']) {
                    sh '''
                        scp -o StrictHostKeyChecking=accept-new scripts/deploy.sh ${DEPLOY_HOST}:/tmp/deploy.sh
                        ssh -o StrictHostKeyChecking=accept-new ${DEPLOY_HOST} \
                            "bash /tmp/deploy.sh ${IMAGE_REPO}:${IMAGE_TAG}"
                    '''
                }
            }
        }
    }

    post {
        always {
            sh 'docker image prune -f || true'
            cleanWs()
        }
        success {
            echo "Build #${env.BUILD_NUMBER} succeeded"
        }
        failure {
            echo "Build #${env.BUILD_NUMBER} failed"
        }
    }
}
