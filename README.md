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
2. Run with the correct environment variables passed in: `docker run  -p 8080:8080 -e "DB_NAME=test"testdb my_app`
 

## Tests
run tests with `pytest`
