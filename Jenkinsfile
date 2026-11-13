pipeline {
    agent any
    triggers {
        pollSCM('H/5 * * * *')
    }

    stages {
        stage('Python syntax') {
            steps {
                sh 'python3 -m py_compile web/app.py checker/checker.py'
            }
        }
        stage('Static analysis') {
            steps {
                sh 'python3 -m pyflakes web/app.py checker/checker.py'
            }
        }

    }
    
}
