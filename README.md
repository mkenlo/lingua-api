This is a small API written in python

## Requirements
1. Python 3.6 +
2. Sanic
3. Kafka-python
4. Pymongo
5. Manage.py


## Database
- Install [MongoDB](https://docs.mongodb.com/manual/installation/)
- To seed the database, run `manage populateDB`
- To drop DB, run `manage dropDB`

## To run
0. Run Script to create DATABASES  `.\db/create.sh`
1. Create virtual environment and activate it and then `pip install -r requirements.txt`.
2. To launch the server run the command: `python run.py`

## Using Environment Variables ?
Want to use virtual environment?
1. Create a `venv` folder inside your working directory
2. Create the virtual env with `python3 -m venv venv`
3. Activate the virtual env with `. venv/bin/activate`
4. Run your project commands
5. Deactivate the env with ` desactivate`

## Tests
run tests with `pytest`