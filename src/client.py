from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
import uvicorn
import requests
import json
from os import path


file_path = path.abspath(__file__) # full path of this script
dir_path = path.dirname(file_path) # full path of the directory of this script


app = FastAPI()
client_html = Jinja2Templates(directory=dir_path+"/../static/")
SERVER_URL = 'http://127.0.0.1:1234' # shouldn't be static here


@app.get("/")  # returns the client html file, inits the values of the results to '-'
def form_post(request: Request):
	
	txt_id = "-"
	txt_summ = "-"
	return client_html.TemplateResponse('client.html', context={'request': request, 'txt_id': txt_id, 'txt_summary': txt_summ})


@app.post("/submit_txt_content")
def form_post(request: Request, text_content: str= Form(...)):
   
	req = SERVER_URL + "/text/sentiment/" + text_content
	res = requests.get(req)  # send http get request in order to retrieve the sentiment for the specified text
	
	try:
		
		if res is not None:
			sentiment = res.json().get("sentiment") # get summary from json
		else:
			sentiment = "Sentiment prediction failed - JSON Response is Null"

	except ValueError:  # catch value error in the response
		sentiment = "Sentiment prediction failed - JSON Decoding has failed"
		print("REST :: Post /submit_id : JSON Decoding has failed")


	return client_html.TemplateResponse('client.html', context={'request': request, 'txt_sentiment': sentiment})



@app.post("/submit_batch_tweets")
def form_post(request: Request):

	url = SERVER_URL + "/text/sentiment/"

	# send http post for adding the given text in the request's body in the db
	# response should be the Id of the document in the DB
	batch_tweets = ['i am really happy, smile, laugh','sad :( i cry','I am really excited for the party',
	'Im really scared']
	data = {'tweets': batch_tweets}
	headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
	res = requests.post(url, data=json.dumps(data), headers=headers)

	tweet_batch = []
	try:
		if res is not None:

			tweets = res.json().get("tweets"); tweets = json.loads(tweets)

			tweets = tweets['tweets'] # get tweets list of objects

			if tweets is not None:
				i = 0
				for t in tweets:
					if i < len(batch_tweets):
						tweet_batch.append(["Tweet:",batch_tweets[i]," - Sentiment:",t])  # create the end result for the html
					i+=1
		else:
			tweet_batch.append("Error in the server response - response is Null")
	except ValueError:
		tweet_batch.append("Error in the server response - response JSON error")
		print("REST :: Post /text/sentiment : JSON Decoding has failed")


	return client_html.TemplateResponse('client.html', context={'request': request, 'tweet_batch': tweet_batch})



if __name__=="__main__":

	uvicorn.run("client:app",host='127.0.0.1', port=1235, reload=True, debug=True, workers=3) # run client server

