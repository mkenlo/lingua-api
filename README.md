This is a small API written in python

## Requirements
1. Python 3.6 +
2. Sanic
3. Kafka-python
4. Pymongo
5. Manage.py


## Database
- Make sure you have [MongoDB] running.

## To run
1. Build docker image : `docker build -t my_app .`
2. Run with the correct environment variables passed in: `docker run  -p 8080:8080 -e "DB_NAME=testdb" my_app`
 

## Tests
run tests with `pytest`

## Running with kubernetes.

1. install minikube
2. Install istio [https://istio.io/docs/setup/getting-started/]
3. launch mongo db with `kubectl apply -f mogodb.yaml`
4. launch app with `kubectl apply -f linguaapi.yaml`
5. launch istio gateway `kubectl apply -f gateway.yaml`
6. launch istio virtual service `kubectl apply -f gateway_service.yaml`
7. access the service with `$(minikube ip)`

After changing code, run the following:
docker build -t gcr.io/groundtruthbackend/backend .
docker push gcr.io/groundtruthbackend/backend
