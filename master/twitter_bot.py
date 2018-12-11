import tweepy
import time
import shelve
import string
import nltk
import random
from datetime import date

my_username = "@bot03490095"

with shelve.open("keys") as keys:
    auth = tweepy.OAuthHandler(keys['CONSUMER_KEY'], keys['CONSUMER_SECRET'])
    auth.set_access_token(keys['ACCESS_KEY'], keys['ACCESS_SECRET'])
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


def check_subscribe(tweet, username):
    print("checking for sub\n found", tweet.strip(" .!?/").casefold())
    if tweet.strip(" .!?/").casefold() == 'subscribe':
        with shelve.open("subscribers", writeback = True) as subs:
            subs.setdefault("usernames", [])
            if username not in subs['usernames']:
                subs['usernames'].append(username)
                return "@{} Success! You have been subscribed for daily facts. Tweet UNSUBSCRIBE to stop recieving daily tweets.".format(username)
            return "@{} You are already subscribed! Hit me with a topic for a fact!".format(username)
    elif tweet.strip(" .!?/").casefold() == "unsubscribe":
         with shelve.open("subscribers", writeback = True) as subs:
            subs.setdefault("usernames", [])
            if username in subs['usernames']:
                subs['usernames'].remove(username)
                return "@{} You have been unsubscribed. Thank you for putting up with me this long!".format(username)
            return "@{} You are already unsubscribed!".format(username)
    return False


def get_relevant_fact(tweet,username):                                          # takes username and tweet
    tweet = tweet.replace(my_username,"")                                       # remove my_username from the tweet
    result = check_subscribe(tweet, username)
    if result:
        return result                                                        # return a tuple

    with shelve.open('.\\scraping\\database') as db:
            tweet = tagify(tweet)                                               # get the set of tags
            maximum = 0                                                         # set the maximum of common tags to zero
            fact_list = []                                                      # it will contain the facts which have the maximum common tags
            for i in db.keys():
                if len(tweet.intersection(db[i])) > maximum:                    # maximize the maximum
                    maximum = len(tweet.intersection(db[i]))
                    fact_list.clear()                                           # since we found the new maximum, clear the list
                    fact_list.append(i)                                         # and add the new fact to the list
                elif len(tweet.intersection(db[i])) == maximum:
                    fact_list.append(i)                                         # also add any other fact which has same common tags
            if len(fact_list) == 0:
                return '@' + username + ' Did you know? \"' + get_random_fact(username)  + '"'                              # if there was no intersection, then fetch a random tweet
            return '@' + username + ' Did you know? \"' + random.choice(fact_list)  + '"'                                    # else just choose a random fact from the list



def reply():
    print("retrieving tweets")
    last_seen_id = retrieve_last_seen(FILE_NAME)
    mentions = api.mentions_timeline(last_seen_id, tweet_mode = 'extended')
    if len(mentions) == 0:
        print("no new tweet found...")
    for mention in reversed(mentions):
        print(mention.user.screen_name,mention.id,mention.full_text)
        last_seen_id = mention.id

        fact = get_relevant_fact(mention.full_text,mention.user.screen_name)
        print("Reply:", fact)
        api.update_status(fact, mention.id)
        store_last_seen_id(last_seen_id, FILE_NAME)



def daily_update():
    with shelve.open("subscribers") as subs:
        for username in subs.get("usernames", []):                                     
            fact = get_random_fact(username)
            try:
                api.update_status('@' + username + ' Your daily fact: \"' + fact + '"')
            except:
                pass




while True:
    with shelve.open("subscribers") as subs:
        subs.setdefault("date", date.today())
        today = subs["date"]
        subs["date"] = date.today()

    if today != date.today():
        daily_update()
        today = date.today()
    reply()
    time.sleep(15)
