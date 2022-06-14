from flask_login import current_user
from website import create_app
from flask import render_template, request, send_file
import tweepy 
import pandas as pd
from textblob import TextBlob
import re
import matplotlib.pyplot as plt

app = create_app()

@app.route('/')
def home():
    return render_template('home.html', user = current_user)

@app.route('/sentiment', methods = ['GET','POST'])
def sentiment():

    userid = request.form.get('userid')
    hashtag = request.form.get('hashtag')

    if userid == "" and hashtag == "":
        error = "Please Enter any one value"
        return render_template('home.html', error=error, user = current_user)
    
    if not userid == "" and not hashtag == "":
        error = "Both entry not allowed"
        return render_template('home.html', error=error, user = current_user)

    #Entering the keys to authenticate with the Twitter API
    consumerKey = "Insert key here"
    consumerSecret = "Insert key here"
    accessToken = "Insert key here"
    accessTokenSecret = "Insert key here"
   
    
    authenticate = tweepy.OAuthHandler(consumerKey, consumerSecret)
    authenticate.set_access_token(accessToken, accessTokenSecret)
    api = tweepy.API(authenticate, wait_on_rate_limit = True)

    def cleanTxt(text):
        text = re.sub('@[A-Za-z0–9]+', '', text) #Removing @mentions
        text = re.sub('#', '', text) # Removing '#' hash tag
        text = re.sub('RT[\s]+', '', text) # Removing RT
        text = re.sub('https?:\/\/\S+', '', text) # Removing hyperlink
        return text

    def getSubjectivity(text):
        return TextBlob(text).sentiment.subjectivity

    def getPolarity(text):
        return TextBlob(text).sentiment.polarity

    def getAnalysis(score):
            if score < 0:
                return 'Negative'
            elif score == 0:
                return 'Neutral'
            else:
                return 'Positive'

    if userid == "":
        # hashtag coding
        msgs = []
        msg =[]
        for tweet in tweepy.Cursor(api.search_tweets, q=hashtag).items(100):
            msg = [tweet.text] 
            msg = tuple(msg)                    
            msgs.append(msg)

        df = pd.DataFrame(msgs)
        df['Tweets'] = df[0].apply(cleanTxt)
        df.drop(0, axis=1, inplace=True)
        df['Subjectivity'] = df['Tweets'].apply(getSubjectivity)
        df['Polarity'] = df['Tweets'].apply(getPolarity)
        df['Analysis'] = df['Polarity'].apply(getAnalysis)
        positive = df.loc[df['Analysis'].str.contains('Positive')]
        negative = df.loc[df['Analysis'].str.contains('Negative')]
        neutral = df.loc[df['Analysis'].str.contains('Neutral')]

        positive_per = round((positive.shape[0]/df.shape[0])*100, 1)
        negative_per = round((negative.shape[0]/df.shape[0])*100, 1)
        neutral_per = round((neutral.shape[0]/df.shape[0])*100, 1)

        def piechart():
            labels = ['Positive [' + str(positive_per) + '%]', 'Negative [' + str(
                negative_per) + '%]', 'Neutral [' + str(neutral_per) + '%]']
            sizes = [positive_per, negative_per, neutral_per]
            colors = ['#4cbb17', '#e8000d', '#ffff00']
            patches, texts = plt.pie(sizes, colors=colors, startangle=90)
            plt.legend(patches, labels)
            plt.title("Piechart of the " + userid + " twitter account")
            
            plt.savefig("website/static/plot.png",transparent=True)

        def bargraph():

            data = {'Postitive': positive_per,
                    'Negative': negative_per, 'Neutral': neutral_per}
            sentiments = list(data.keys())
            values = list(data.values())

            fig = plt.figure(figsize=(10, 7))

            plt.bar(sentiments, values, color=['#4cbb17', '#e8000d', '#ffff00'],
                    width=0.4)

            plt.xlabel("Percentages from the Result of analysis")
            plt.ylabel("percentages %")
            plt.title("Bar graph of the " + userid + " twitter account")
            plt.savefig("website/static/plot2.png",transparent=True)

        def linegraph():

            data = {'Postitive': positive_per,
                    'Negative': negative_per, 'Neutral': neutral_per}
            moods = list(data.keys())
            values = list(data.values())

            fig = plt.figure(figsize=(10, 7))

            plt.plot(moods, values)
            plt.ylabel("percentages %")
            plt.title("Line graph of the " + userid + " twitter account")

            plt.savefig("website/static/plot3.png",transparent=True)

        return render_template('sentiment.html', name=hashtag, positive=positive_per, negative=negative_per, neutral=neutral_per, piechart=piechart(), bargraph=bargraph(), linegraph = linegraph(), user=current_user)    
    else:
        # user coding
        username = "@"+userid

        post = api.user_timeline(screen_name=userid, count = 200, lang ="en", tweet_mode="extended")
        twitter = pd.DataFrame([tweet.full_text for tweet in post], columns=['Tweets'])

        twitter['Tweets'] = twitter['Tweets'].apply(cleanTxt)
        twitter['Subjectivity'] = twitter['Tweets'].apply(getSubjectivity)
        twitter['Polarity'] = twitter['Tweets'].apply(getPolarity)
        
        twitter['Analysis'] = twitter['Polarity'].apply(getAnalysis)
        positive = twitter.loc[twitter['Analysis'].str.contains('Positive')]
        negative = twitter.loc[twitter['Analysis'].str.contains('Negative')]
        neutral = twitter.loc[twitter['Analysis'].str.contains('Neutral')]

        positive_per = round((positive.shape[0]/twitter.shape[0])*100, 1)
        negative_per = round((negative.shape[0]/twitter.shape[0])*100, 1)
        neutral_per = round((neutral.shape[0]/twitter.shape[0])*100, 1)
        average_per = round((positive_per+negative_per)/2 + neutral_per,1)
               
        user = api.get_user(screen_name=userid)
        followers_count = user.followers_count

        def piechart():
            labels = ['Positive [' + str(positive_per) + '%]', 'Negative [' + str(
                negative_per) + '%]', 'Neutral [' + str(neutral_per) + '%]']
            sizes = [positive_per, negative_per, neutral_per]
            colors = ['#4cbb17', '#e8000d', '#ffff00']
            patches, texts = plt.pie(sizes, colors=colors, startangle=90)
            plt.legend(patches, labels)
            plt.title("Piechart of the " + userid + " twitter account")
            
            plt.savefig("website/static/plot.png",transparent=True)

        def bargraph():

            data = {'Postitive': positive_per,
                    'Negative': negative_per, 'Neutral': neutral_per}
            sentiments = list(data.keys())
            values = list(data.values())

            fig = plt.figure(figsize=(10, 7))

            plt.bar(sentiments, values, color=['#4cbb17', '#e8000d', '#ffff00'],
                    width=0.4)

            plt.xlabel("Percentages from the Result of analysis")
            plt.ylabel("percentages %")
            plt.title("Bar graph of the " + userid + " twitter account")
            plt.savefig("website/static/plot2.png",transparent=True)

        def linegraph():

            data = {'Postitive': positive_per,
                    'Negative': negative_per, 'Neutral': neutral_per}
            moods = list(data.keys())
            values = list(data.values())

            fig = plt.figure(figsize=(10, 7))

            plt.plot(moods, values)
            plt.ylabel("percentages %")
            plt.title("Line graph of the " + userid + " twitter account")

            plt.savefig("website/static/plot3.png",transparent=True)

        return render_template('sentiment.html', name=username, positive=positive_per, negative=negative_per, neutral=neutral_per, followers=followers_count, average=average_per, piechart=piechart(), bargraph=bargraph(), linegraph = linegraph(), user=current_user)


@app.route('/visualization')
def visualize():

    return render_template('visualization.html', user = current_user)

app.run(debug=True)    