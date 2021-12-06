import pickle
from joblib import dump, load
from sklearn.feature_extraction.text import TfidfVectorizer
import re
from os import path

file_path = path.abspath(__file__) # full path of this script
dir_path = path.dirname(file_path) # full path of the directory of this script


class SentimentPredictor:

	def __init__(self, sp_ip):
		self.id = sp_ip
		self.vectorizer = self.get_vectorizer()
		self.model = self.get_nlp_model()


	def get_nlp_model(self):
		
		print("NLP :: Loading NLP Model")
		nlp_model = load(dir_path+'/../models/SA_NLP_Model-os.joblib')
		# nlp_model = pickle.load(open("../models/SA_NLP_Model.pickle", "rb"))

		return nlp_model


	def get_vectorizer(self):

		print("NLP :: Loading Tf-Idf Vectorizer")
		vec = pickle.load(open(dir_path+"/../models/vectorizer_tfidf-os.pickle", "rb"))

		return vec

	def clean_text(self, txt):

		emoticons_happy = set([':-)', ':)', ':]', ':3', '=]', '=)'])

		emoticons_sad = set([':(',"=[" ,":'(", ':@', ':-(', ':[', ':-[', '>.<', ':-c',':c'])

		emoticons_surprised = set([':O', ':o', ':-o', ':-O'])

		words = txt.split()
		new_w = []
		for w in words:
			if w in emoticons_happy:
				new_w.append("happy")
			elif w in emoticons_sad:
				new_w.append("sad") 
			elif w in emoticons_surprised:
				new_w.append("surprised") 
			else:
				new_w.append(w)
		txt = " ".join(new_w)

		# txt = replace_emoticons(txt)     # replace emoticons with a word describing the emoticon
		txt = re.sub('@[^\s]+', '', txt) # remove usernames
		txt = re.sub('RT[\s]+', '', txt) # remove retweet 'RT'
		txt = re.sub('#', '', txt)       # remove '#'
		txt = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', '', txt)  # remove URLs inside the text

		return txt

	def get_sentiment(self, txt):

		txt = self.clean_text(txt)
		vec = self.vectorizer.transform([txt])
		res = self.model.predict(vec)
		if res is not None:
			try:
				res = res[0]
			except ValueError:
				res = "NLP Model Failed"
		return res