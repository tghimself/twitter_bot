import tweepy
import time
import shelve
import string
import nltk

CONSUMER_KEY = ''
CONSUMER_SECRET = ''
ACCESS_KEY = ''
ACCESS_SECRET = ''

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

FILE_NAME = 'last_seen_id.txt'

def retrieve_last_seen(filename):
    with open(filename,'r') as file:
        last_seen_id = int(file.read().strip())
    return last_seen_id

def store_last_seen_id(last_seen_id,filename):
    with open(filename,'w') as file:
        file.write(str(last_seen_id))
    return

def tagify(str1):
    str1= str1.casefold()                                                       # for comparison
    if "ain't" in str1:                                                         # tokenize didn't seem to remove this one
        str1=str1.replace("ain't", "")
    puncts = string.punctuation
    tags = nltk.word_tokenize(str1)                                             # split the string well
    stopwords = nltk.corpus.stopwords.words("english")
    return set([word for word in tags if word not in list(puncts) + stopwords+["'s", "n't"]])   #return a  set of tags

def get_random_fact(username):
    with shelve.open('.\\scraping\\database') as db:                            # open the shelve file
        fact = random.choice(list(db.keys()))
        if len(fact) + len('@' + username) > 260:
            return get_random_fact(username)
        print("responding with a random fact")
        return fact


def get_relevant_fact(tweet,username):                                          # takes username and tweet
    with shelve.open('.\\scraping\\database') as db:
            tweet = tagify(tweet)                                               # get the set of tags
            maximum = 0                                                         # set the maximum of common tags to zero
            fact = ""
            fact_list = []                                                      # it will contain the facts which have the maximum common tags
            for i in db.keys():
                if len(tweet.intersection(db[i])) > maximum:                    # maximize the maximum
                    maximum = len(tweet.intersection(db[i]))
                    fact_list.clear()                                           # since we found the new maximum, clear the list
                    fact_list.append(i)                                         # and add the new fact to the list
                elif len(tweet.intersection(db[i])) == maximum:                 
                    fact_list.append(i)                                         # also add any other fact which has same common tags
            if fact == "":
                return get_random_fact(username)                                # if there was no intersection, then fetch a random tweet
            return random.choice(fact_list)                                     # else just choose a random fact from the list



def reply():
    print("retrieving tweets")
    last_seen_id = retrieve_last_seen(FILE_NAME)
    mentions = api.mentions_timeline(last_seen_id, tweet_mode = 'extended')
    if len(mentions) == 0:
        print("no new tweet found...")
    for mention in reversed(mentions):
        print(mention.id,mention.full_text)
        last_seen_id = mention.id
        store_last_seen_id(last_seen_id, FILE_NAME)
        fact = get_relevant_fact(mention.full_text,mention.user.screen_name)
        api.update_status('@' + mention.user.screen_name + ' Did you know? \"' + fact + '"', mention.id)

while True:
    reply()
    time.sleep(15)
