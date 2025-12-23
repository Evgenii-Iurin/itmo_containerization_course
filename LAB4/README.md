## Инструкция по запуску Lab4 в Minikube

- Официальная инструкция по установке Minikube: https://minikube.sigs.k8s.io/docs/start/?arch=%2Fmacos%2Fx86-64%2Fstable%2Fbinary+download


### Выполнено
Развернут в Minikube сервис в связке: Flask-приложение + PostgreSQL.

Архитектура состоит из двух сервисов:

1. **PostgreSQL**  
   Развернули Postgres Deployment с PVC (1Gi) для хранения данных.  
   Настроили Secret для учётных данных БД.  
   Сервис типа ClusterIP (`postgres-service`) обеспечивает внутреннее подключение от Flask.

2. **Flask-приложение**  
   Использовали кастомный образ `my_flask_image:latest`, собранный из локального Dockerfile.  
   Добавили init-контейнер, который ждёт готовности PostgreSQL и создаёт таблицу `test_init`.  
   Основной контейнер с liveness/readiness HTTP-пробами на `/health`.  
   Сервис типа NodePort (`flask-service`) даёт внешний доступ.


### 0. Запуск Minikube
```bash
minikube start
```

### 1. Подготовка Docker-образа

```bash
eval $(minikube docker-env)

docker build -t my_flask_image:latest .
```

### 2. Применение манифестов

```bash
kubectl apply -f pg_secret.yml
kubectl apply -f pg_pvc.yml
kubectl apply -f pg_deployment.yml
kubectl apply -f pg_service.yml

kubectl wait --for=condition=ready pod -l app=lab4,component=db --timeout=120s

kubectl apply -f flask_deployment.yml
kubectl apply -f flask_service.yml
```

### 3. Проверка статуса подов

```bash
kubectl get pods
```

![get pods](images/image.png)

### 4. Запуск приложения

```bash
minikube service flask-service
```

![minikube service flask-service](images/image2.png)

### 5. Проверка эндпоинтов

```bash
curl http://127.0.0.1:59133
curl http://127.0.0.1:59133/health
curl http://127.0.0.1:59133/db/test
```

![curls](images/image3.png)