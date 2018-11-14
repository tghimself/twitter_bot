import tweepy
import time
import shelve
import random

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



def get_random_fact(username):
    '''returns a tweet of validfor a particular username'''
    with shelve.open('.\\scraping\\data') as fact_dict:                         # open the shelve file
        random_id = len(fact_dict.keys())                                       # store the number of topics present
        random_id = random.randint(0,random_id-1)                               # generate a random number b/w 0 and highest index a topic can have
        topic = list(fact_dict.keys())[random_id]                               # access the topic at the random index
        print("responding with a fact from", topic)       
        random_id = len(fact_dict[topic])                                       #  store the number of facts present in that topic
        random_id = random.randint(0,random_id-1)                               # generate a random number b/w 0 and highest index a fact can have
        count = 0                                                               # set counter for number of attempts
        while len(fact_dict[topic][random_id]) + len('@'+username) > 260:       # if fact is above tweet limit
            random_id = random.randint(0,random_id-1)                           # generate a new fact
            count+=1                                                            # increment the number of attempts
            if count > 50:                                                      # if attempts > 50, topic doesn't have any fact of tweet limit
                break                                                           # stop loop
        else:                                                                   
            return fact_dict[topic][random_id]                                  # if break does not occur, return fact
        return get_random_fact(username)                                        # else repeat process



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
        fact = get_random_fact(mention.user.screen_name)
        api.update_status('@' + mention.user.screen_name + ' Did you know? \"' + fact + '"', mention.id)

while True:
    reply()
    time.sleep(15)
