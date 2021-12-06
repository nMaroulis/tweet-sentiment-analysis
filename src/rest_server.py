from fastapi import FastAPI, Request
import uvicorn
import sqlite3
import signal, sys
import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy.orm import sessionmaker,relationship
import json
from nlp_funcs import SentimentPredictor

HOST_IP = '127.0.0.1'
HOST_PORT = 1234

"""
Initiate Database and create a connector with SQLAlchemy as an ORM
"""
engine = db.create_engine('sqlite:///../tweets.db', echo = True)
connection = engine.connect()
metadata = db.MetaData()
Base = declarative_base()
DBSession = sessionmaker(bind=engine)
session = DBSession()
session.autocommit == True # commits to DB when flush is used


# NLP Model and Vectorizer Class as global object variable
# Global variables are generally bad practice, but for the sake of simplicity I implemented it this way
sentiment_predictor = SentimentPredictor("main")


app = FastAPI()


# The Class representation of the Tweet Table
class Tweet(Base):
	__tablename__ = 'Tweet'
   
	id = Column(Integer, primary_key=True, nullable=False, autoincrement = True)
	content = Column(String)
	sentiment = Column(String)


def insert_tweet(b):
	new_tweet = Tweet(content=b)
	session.add(new_tweet)
	session.flush() # use flush so we can get the Id of the inserted tweet
	tweet_id  = new_tweet.id
	session.commit() # commit to DB
	return tweet_id


@app.get("/")
async def root():

	print("REST :: Get /")

	return {"status": "server running"}


@app.get("/text/sentiment/{content}")
async def get_summary(content: str, q: str=None):

	print("REST :: (1) GET /text/sentiment/",content)

	if content is not None: # check if the query returned any result
		try:
			sentiment = sentiment_predictor.get_sentiment(content) # get predicted sentiment
		except ValueError as err:
			message = ('Sentiment Prediction Failed. Exception: {}'.format(err))
			response = json.dumps({status:'error', error_message:message})
			response.status_code = 400 # Bad Request
			# tweet_batch_sentiments = ['Sentiment Prediction Failed - ValueError']
			return response
	else:
		sentiment = 'Sentiment Prediction Failed'

	print("REST :: (2) GET /text/sentiment/, predicted sentiment:",sentiment)

	return {"content": content, "sentiment": sentiment}


# Batch of messages a a JSON 
@app.post("/text/sentiment/")
async def get_summary(request: Request):

	print("REST :: (1) POST /text/sentiment/",request)

	json_param = await request.json()  # parse request json payload

	# tweet_id = insert_tweet(text_body) # get inserted tweet id
	tweet_batch_sentiments = []

	if json_param is not None: # check if the query returned any result
		try:
			req_tweets = json_param['tweets']  # get json body
			for t in req_tweets:
				# predict sentiments for each of the tweets
				tweet_batch_sentiments.append(sentiment_predictor.get_sentiment(t))

		except ValueError:
			message = ('Sentiment Prediction Failed. Exception: {}'.format(err))
			response = json.dumps({status:'error', error_message:message})
			response.status_code = 400 # Bad Request
			# tweet_batch_sentiments = ['Sentiment Prediction Failed - ValueError']
			return response
	else:
		tweet_batch_sentiments = ['Sentiment Prediction Failed - JSON decoding error']

	print("REST :: (2) POST /text/sentiment/, predicted sentiments:",tweet_batch_sentiments)

	res = {'tweets': tweet_batch_sentiments} # prepare response JSON
	res=json.dumps(res)

	return {"tweets": res}



def signal_handler(sig, frame):
	# conn.close()
	print('DB :: Database Connection terminated')
	sys.exit(0)


def db_init():
	if not engine.dialect.has_table(connection, "Tweet"):  # If table don't exist, Create.
		metadata = MetaData(engine)
		# Create a table with the appropriate Columns
		Table("Tweet", metadata,
			Column('Id', Integer, primary_key=True, nullable=False, autoincrement = True),
			Column('Content', String),
			Column('Sentiment', String))
		metadata.create_all()	# Implement the creation
		print("DB :: Database created!")
	else:
		print("DB :: Database already initiated!")


if __name__=="__main__":

	signal.signal(signal.SIGINT, signal_handler) # Handle Ctrl+C exit
	db_init()  # initiate database
	# load_vectorizer_and_model() # Load ML model and the Tf-Idf vectorizer to memory
	uvicorn.run("rest_server:app",host=HOST_IP, port=HOST_PORT, reload=True, debug=True, workers=2) # run server

