# Local Docker Infrastructure — Mebelmart Tests

## Порты

| Сервис   | URL                        | Описание                       |
|----------|----------------------------|--------------------------------|
| Jenkins  | http://localhost:8080      | CI/CD, расписание, ручной запуск|
| Allure   | http://localhost:5050      | Отчёты|


---

## Быстрый старт

```cmd
cd mebelmart-testing
docker compose -f docker-setup/docker-compose.yml up -d
```

Проверить что всё запустилось:
```cmd
docker compose -f docker-setup/docker-compose.yml ps
```

### Jenkins Pipeline
```groovy
pipeline {
    agent any

    triggers {
        cron('H 9 * * 1-5')
    }

    parameters {
        choice(
            name: 'BROWSER',
            choices: ['chromium', 'firefox'],
            description: 'Browser'
        )
        choice(
            name: 'HEADLESS',
            choices: ['true', 'false'],
            description: 'true = headless | false = headed demo'
        )
        string(
            name: 'PYTEST_ARGS',
            defaultValue: '',
            description: 'Extra args, e.g. -k test_price_filter'
        )
    }

    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '20'))
    }

    stages {

        stage('Build Test Image') {
            steps {
                sh '''
                    docker build \
                        --no-cache \
                        -t mebelmart-tests \
                        -f /workspace/docker-setup/tests/Dockerfile \
                        /workspace
                '''
            }
        }
        
        stage('Clear Previous Results') {
            steps {
                sh """
                    docker run --rm \
                        -v mebelmart_allure_results:/data \
                        alpine sh -c "rm -rf /data/* && echo 'Results cleared'"
                """
            }
        }
        
        stage('Run Tests') {
            steps {
                sh """
                    docker run --rm \
                        -v ${HOST_WORKSPACE}:/app \
                        -v mebelmart_allure_results:/app/allure-results \
                        -e HEADLESS=true \
                        mebelmart-tests \
                        /app/tests --browser=chromium \
                        --alluredir=/app/allure-results -v --tb=short \
                        ${params.PYTEST_ARGS}
                """
                sh """
                    docker run --rm \
                        -v ${HOST_WORKSPACE}:/app \
                        -v mebelmart_allure_results:/app/allure-results \
                        -e HEADLESS=true \
                        mebelmart-tests \
                        /app/tests --browser=firefox \
                        --alluredir=/app/allure-results -v --tb=short \
                        ${params.PYTEST_ARGS}
                """
            }
        }

        stage('Refresh Allure Report') {
            steps {
                sh """
                    curl -s "http://mebelmart-allure:5050/allure-docker-service/generate-report" \
                        || echo 'Allure refresh skipped'
                """
            }
        }
    }

    post {
        always {
            echo "Done. Allure: http://localhost:5050"
        }
    }
}
```


---

## Запуск тестов

### Через Jenkins

**Ручной запуск:**
- Open Item `mebelmart-tests` → Build with Parameters
- Выбрать BROWSER, HEADLESS, опционально PYTEST_ARGS
- Build Now

**По расписанию:**
- Автоматически каждый будний день в 09:00
- Настраивается в Jenkinsfile в блоке `triggers { cron(...) }`

### Напрямую через Docker

```cmd
# Headless (обычный CI-запуск)
docker compose -f docker-setup/docker-compose.yml run --rm ^
    -e BROWSER=chromium -e HEADLESS=true ^
    tests --alluredir=allure-results -v

# Headed (демо-режим — браузер виден через noVNC)
docker compose -f docker-setup/docker-compose.yml run --rm ^
    -e BROWSER=chromium -e HEADLESS=false ^
    tests --alluredir=allure-results -v

# Один конкретный тест
docker compose -f docker-setup/docker-compose.yml run --rm ^
    -e HEADLESS=true ^
    tests -k test_price_filter -v
```

---

## Просмотр отчётов Allure

Открыть http://localhost:5050/allure-docker-service/projects/default/reports/latest/index.html

---

## Остановка

```cmd
docker compose -f docker-setup/docker-compose.yml down
```

Остановить и удалить все данные:
```cmd
docker compose -f docker-setup/docker-compose.yml down -v
```
