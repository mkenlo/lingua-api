from manager import Manager
from pymongo import MongoClient
import json
from pprint import pprint


manager = Manager()

client = MongoClient('mongodb://localhost:27017/')

my_db = client.linguadb


@manager.command
def populateDB():
    """populate the Database"""
    with open('db/languages.json') as f:
        data = json.load(f)
        print("1. Seeding Collection languages")
        my_db.languages.insert_many(data)
    with open('db/sentences.json') as f:
        data = json.load(f)
        print("2. Seeding Collection sentences")
        my_db.sentences.insert_many(data)


@manager.command
def dropDB():
    """ drop all DATABASE contents"""
    my_db.languages.drop()
    print("Dropping Database")


if __name__ == '__main__':
    manager.main()
