import string
import shelve
import nltk
from  time import sleep


def tagify(str1):
	str1= str1.casefold()
	if "ain't" in str1:
		str1=str1.replace("ain't", "")
	puncts = string.punctuation
	tags = nltk.word_tokenize(str1)
	stopwords = nltk.corpus.stopwords.words("english")
	return set([word for word in tags if word not in list(puncts) + stopwords+["'s", "n't"]])
with shelve.open("data") as data:
	with shelve.open("database", writeback=True) as database:
		k = 0
		for i in data.keys():
			print(len(data.values())-k,"items left")
			for j in data[i]:
				database.setdefault(j,set())
				tags = tagify(j)
				tags.add(i)
				database[j].update(tags)

			k+=1
