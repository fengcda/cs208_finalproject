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

    keyword = term.replace(' ', '-')
    db = pymongo.MongoClient(MONGO_URL).redditDatabase
    first = True
    level1 = db[keyword]
    if level1:
        level2 = level1[subreddit]
        entries = level2.find()
        if entries:
            result = ''
            for entry in entries:
                if entry:
                    if first:
                        result = '<div id = "title">Found in Database</div>\n'
                        first = False
                    result += '<div id = "title">' + entry['title'] + '</div>'
                    result += '<a href = "' + entry['url'] + '">' + entry['url'] + '</a>'
                    result += '<div id = "date">' + entry['date'] + '</div>\n'
            if not first:
                return result

    product = search.search(keyword, subreddit)

    if not product[keyword]['posts']:
        return 'No Results'

    print('[Database] Saving')
    query = level1[product[keyword]['subreddit']]
    query.insert_many(product[keyword]['posts'])
    print('[Database] Saved')
    
    result = '<div id = "title">Scraping Results</div>\n'
    for entry in product[keyword]['posts']:
        result += '<div id = "title">' + entry['title'] + '</div>'
        result += '<a href = "' + entry['url'] + '">' + entry['url'] + '</a>'
        result += '<div id = "date">' + entry['date'] + '</div>\n'

    return result

if __name__ == '__main__':
    app.run(host = '0.0.0.0')
