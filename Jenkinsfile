pipeline {
    agent any

    stages {
        stage('Python syntax') {
            steps {
                sh 'python3 -m py_compile web/app.py checker/checker.py'
            }
        }
    }
}
