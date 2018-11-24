import pyrebase
config = {
  "apiKey": "AIzaSyDoA4NvBBH4EC1rwmEfUUYu9yEx6DgdDoE",
  "authDomain": "twitterdb-a95d1.firebaseapp.com",
  "databaseURL": "https://twitterdb-a95d1.firebaseio.com",
  "storageBucket": "twitterdb-a95d1.appspot.com",
  "serviceAccount": "twitterdb-a95d1-5187a5d44730.json"
}

firebase = pyrebase.initialize_app(config)

auth = firebase.auth()
#authenticate a user
user = auth.sign_in_with_email_and_password("jdominicm@gmail.com", "superContrasena")
db = firebase.database()

import json

credentials = {}  
credentials['CONSUMER_KEY'] = "loRgP75jsSKw2plXgcLSGloLe"
credentials['CONSUMER_SECRET'] = "bXRKV4EWwIIFVMV3zfg780LEnuvJIWYSYGWoNFxF1JnYKUWybS"
credentials['ACCESS_TOKEN'] = "890631462902534144-UKE8NbdUxulaqk8GxXNERC8vmgdkeK8"
credentials['ACCESS_SECRET'] = "pXukSnt2raA3IAYFPAwzgmadPkMrIEv44Wb19HEVKI8oo"

# Save the credentials object to file
with open("twitter_credentials.json", "w") as file:  
    json.dump(credentials, file)

# Import the Twython class
from twython import Twython  
import json

# Load credentials from json file
with open("twitter_credentials.json", "r") as file:  
    creds = json.load(file)

# Instantiate an object
python_tweets = Twython(creds['CONSUMER_KEY'], creds['CONSUMER_SECRET'])

# Create our query
query = {'q': '#naim',
        'lang': 'es',
        }

result = python_tweets.search(**query)
for result in result['statuses']:
    db.child("tweets").push(result, user['idToken'])

    
# Create our query
query = {'q': '#santalucia',
        'lang': 'es',
        }

result = python_tweets.search(**query)
for result in result['statuses']:
    db.child("tweets").push(result, user['idToken'])
    
# Create our query
query = {'q': '#texcoco',
        'lang': 'es',
        }

result = python_tweets.search(**query)
for result in result['statuses']:
    db.child("tweets").push(result, user['idToken'])
    
# Create our query
query = {'q': '#aicm',
        'lang': 'es',
        }

result = python_tweets.search(**query)
for result in result['statuses']:
    db.child("tweets").push(result, user['idToken'])


tokens = list()
names = list()
users = db.child("tweets").get(user['idToken'])
for user in users.each():
    tokens.append(user.key())


import botometer

mashape_key = "3NIK3WFrd1msh8cQDYhLJZ0kr9FIp19C5GUjsn6IQICWtA8Fxk"

twitter_app_auth = {
    'consumer_key': 'loRgP75jsSKw2plXgcLSGloLe',
    'consumer_secret': 'bXRKV4EWwIIFVMV3zfg780LEnuvJIWYSYGWoNFxF1JnYKUWybS',
    'access_token': '890631462902534144-UKE8NbdUxulaqk8GxXNERC8vmgdkeK8',
    'access_token_secret': 'pXukSnt2raA3IAYFPAwzgmadPkMrIEv44Wb19HEVKI8oo',
  }

bom = botometer.Botometer(wait_on_ratelimit=True,
                          mashape_key=mashape_key,
                          **twitter_app_auth)

for token in tokens:
    name = db.child("tweets").child(token).child('user').child('screen_name').get(user['idToken'])
    result = bom.check_account("@" + name.val())
    prom = (result['categories']['content'] + result['categories']['friend'] + result['categories']['network'] + result['categories']['sentiment'] + result['categories']['temporal'] + result['categories']['user'])/6
    db.child("scores").child(name.val()).set(prom, user['idToken'])


scoreNames = list()
scoreList = list()
scores = db.child("scores").get(user['idToken'])
for score in scores.each():
    scoreNames.append(score.key())
    scoreList.append(score.val())

import numpy

avg = numpy.mean(scoreList)
std = numpy.std(scoreList)

normalScores = list()

for score in scoreList:
    normalScores.append((score-avg)/std)

from scipy.stats import norm

for i in range(len(normalScores)):
    normal = norm.cdf(normalScores[i])
    if normal < -3*avg or normal > 3*avg:
        db.child("bots").child(scoreNames[i]).set(1, user['idToken'])
    else:
        db.child("bots").child(scoreNames[i]).set(0, user['idToken'])

bots = db.child('bots').get(user['idToken'])
botList = list()

for bot in bots.each():
    if bot.val() == 1:
        botList.append(bot.key())


for token in tokens:
    name = db.child("tweets").child(token).child('user').child('screen_name').get(user['idToken'])
    if name.val() not in botList:
        tweet = db.child("tweets").child(token).get(user['idToken'])
        db.child("filteredTweets").push(tweet.val(), user['idToken'])

filteredTokens = list()
users = db.child("filteredTweets").get(user['idToken'])
for user in users.each():
    filteredTokens.append(user.key())

for filteredToken in filteredTokens:
    hashtags = db.child("filteredTweets").child(filteredToken).child("entities").child("hashtags").get(user['idToken'])
    if hashtags.val() != None:
        for hashtag in hashtags.val():
            if hashtag['text'].lower() == "santalucia" or hashtag['text'].lower() == "santalucía":
                tweet = db.child("filteredTweets").child(filteredToken).get(user['idToken'])
                db.child("santaLuciaTweets").push(tweet.val(), user['idToken'])
            elif hashtag['text'].lower() == "naim" or hashtag['text'].lower() == "texcoco":
                tweet = db.child("filteredTweets").child(filteredToken).get(user['idToken'])
                db.child("texcocoTweets").push(tweet.val(), user['idToken'])

tweets = db.child("tweets").get(user['idToken'])
for token in tokens:
    name = db.child("tweets").child(token).child('user').child('screen_name').get(user['idToken'])
    if name.val() in botList:
        realName = db.child("tweets").child(token).child('user').child('name').get(user['idToken'])
        imageURL = db.child("tweets").child(token).child('user').child('profile_image_url').get(user['idToken'])
        desc = db.child("tweets").child(token).child('user').child('description').get(user['idToken'])
        db.child("botAccounts").child(name.val()).child("name").set(name.val(), user['idToken'])
        db.child("botAccounts").child(name.val()).child("realName").set(realName.val(), user['idToken'])
        db.child("botAccounts").child(name.val()).child("image").set(imageURL.val(), user['idToken'])
        db.child("botAccounts").child(name.val()).child("description").set(desc.val(), user['idToken'])


santaLuciaTokens = list()
users = db.child("santaLuciaTweets").get(user['idToken'])
for user in users.each():
    santaLuciaTokens.append(user.key())

texcocoTokens = list()
users = db.child("texcocoTweets").get(user['idToken'])
for user in users.each():
    texcocoTokens.append(user.key())

for santaLuciaToken in santaLuciaTokens:
    tweet = db.child('santaLuciaTweets').child(santaLuciaToken).child("text").get(user['idToken'])
    name = db.child('santaLuciaTweets').child(santaLuciaToken).child("user").child("screen_name").get(user['idToken'])
    realName = db.child('santaLuciaTweets').child(santaLuciaToken).child("user").child("name").get(user['idToken'])
    imageURL = db.child('santaLuciaTweets').child(santaLuciaToken).child("user").child("profile_image_url").get(user['idToken'])
    followers = db.child('santaLuciaTweets').child(santaLuciaToken).child("user").child("followers_count").get(user['idToken'])
    desc = db.child('santaLuciaTweets').child(santaLuciaToken).child("user").child("description").get(user['idToken'])
    db.child("santaLuciaUsers").child(name.val()).child("name").set(name.val(), user['idToken'])
    db.child("santaLuciaUsers").child(name.val()).child("realName").set(realName.val(), user['idToken'])
    db.child("santaLuciaUsers").child(name.val()).child("image").set(imageURL.val(), user['idToken'])
    db.child("santaLuciaUsers").child(name.val()).child("followers").set(followers.val(), user['idToken'])
    db.child("santaLuciaUsers").child(name.val()).child("tweet").set(tweet.val(), user['idToken'])
    db.child("santaLuciaUsers").child(name.val()).child("description").set(desc.val(), user['idToken'])

for texcocoToken in texcocoTokens:
    tweet = db.child('texcocoTweets').child(texcocoToken).child("text").get(user['idToken'])
    name = db.child('texcocoTweets').child(texcocoToken).child("user").child("screen_name").get(user['idToken'])
    realName = db.child('texcocoTweets').child(texcocoToken).child("user").child("name").get(user['idToken'])
    imageURL = db.child('texcocoTweets').child(texcocoToken).child("user").child("profile_image_url").get(user['idToken'])
    followers = db.child('texcocoTweets').child(texcocoToken).child("user").child("followers_count").get(user['idToken'])
    desc = db.child('texcocoTweets').child(texcocoToken).child("user").child("description").get(user['idToken'])
    db.child("texcocoUsers").child(name.val()).child("name").set(name.val(), user['idToken'])
    db.child("texcocoUsers").child(name.val()).child("realName").set(realName.val(), user['idToken'])
    db.child("texcocoUsers").child(name.val()).child("image").set(imageURL.val(), user['idToken'])
    db.child("texcocoUsers").child(name.val()).child("followers").set(followers.val(), user['idToken'])
    db.child("texcocoUsers").child(name.val()).child("tweet").set(tweet.val(), user['idToken'])
    db.child("texcocoUsers").child(name.val()).child("description").set(desc.val(), user['idToken'])

f = open("texcocoTweets.txt", "w+")
textVal = ""
for texcocoToken in texcocoTokens:
    text = db.child("texcocoTweets").child(texcocoToken).child("text").get(user['idToken'])
    textVal += text.val()
    textVal+= "\n"

print(textVal)

