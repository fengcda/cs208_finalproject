from flask import Flask
from flask import request
from flask_cors import CORS
import json
import pymongo
import search
import os

mon = os.environ.get("MONGO_URL")
if mon:
    MONGO_URL = str(os.environ.get("MONGO_URL"))
else:
    MONGO_URL = 'mongodb://localhost:27017'
# MONGO_URL = 'mongodb://localhost:27017'

app = Flask(__name__)
CORS(app)

@app.route('/', methods = ['GET', 'POST'])
def index():
    if request.method != 'POST':
        return 'Use Post Method'
    term = request.form['term']
    subreddit = request.form['subreddit']
    keyword, product = search.search(term, subreddit)
    if not product[keyword]['posts']:
        return 'No Results'

    print('[Database] Saving')
    db = pymongo.MongoClient(MONGO_URL).redditDatabase
    reddit = db[keyword]
    query = reddit[product[keyword]['subreddit']]
    query.insert_many(product[keyword]['posts'])
    print('[Database] Saved')
    
    return term + '\n' + subreddit

if __name__ == '__main__':
    app.run(host = '0.0.0.0')
