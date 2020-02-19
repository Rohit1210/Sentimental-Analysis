from django.shortcuts import render
from django.http import HttpResponse
#Twitter API : tweepy
import tweepy as tw
#textblob API : Textblob
#TextBlob perform simple natural language processing tasks.
from textblob import TextBlob #library for processing textual data
#import pandas as pd
#import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import re
import csv
import datetime as datetime
import sys,os
import statistics
import socket
#graphs lib
import plotly.offline as opy
import plotly.graph_objs as go
from django.views.generic import TemplateView
#==============================
#Custom User_Exception

class User_Exception(Exception):
    def __init__(self,msg):
        self.msg=msg

# Get API From Tweepy 

CONSUMER_KEY = ""
CONSUMER_SECRET = ""
ACCESS_TOKEN = ""
ACCESS_TOKEN_SECRET = ""
try:
    auth = tw.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tw.API(auth,wait_on_rate_limit=True)
except tw.TweepError as msg:
    print(msg)

figure=None
#remove_url from tweets
def remove_url(txt):
    return " ".join(re.sub("([^0-9A-Za-z \t])|(\w+:\/\/\S+)", "", txt).split())
# Collect tweets
# --> twitter don't give access to dig too old history
# --> Cursor is a object which store tweets containing searched item
x=True
pos =[]
neg =[]
neu =[]
psum=0
lsum=0
nsum=0
try:
    x == True
    def collect_tweets(search_words,date_since,num): # function to search "tweets" inbound of time
        csvFile = open('currenttweets.csv', 'w')
        csvWriter = csv.writer(csvFile)
        for tweet in tw.Cursor(api.search, #call search function of twitter search
                            q=search_words,
                            count= 280, #Tweet Limit to load
                            lang="en", # define english language
                            since=date_since).items(num):
            tweet = tweet.text.encode(encoding = 'utf-8')
            tweet = re.sub(r'\W+', ' ', str(tweet)) #By Python definition '\W == [^a-zA-Z0-9_], which excludes all numbers, letters and _
            tweet = TextBlob(tweet)
            tweet = tweet.correct()
            tweet = tweet.sentences
            if tweet == []:
                pass
            else:
                csvWriter.writerow(tweet)
        if x == False:
            raise User_Exception("Internet connection failed")
except User_Exception as msg:
    print(msg)


# Data is loaded in List and CSV and filter function works on text means string 
def read_tweets():
    try:
        l=[]
    
        sen_values = []
        a=0
        b=0
        c=0
        with open('currenttweets.csv','r')as f:
            data = csv.reader(f)
            for row in data:
                #print(type(row))
                val = TextBlob(str(row))
                pol_val,sub_val = val.sentiment.polarity , val.sentiment.subjectivity
                val=val.sentiment
                if pol_val == 0.0:
                    c=c+1
                    neu.append(pol_val)
                elif pol_val < 0.0:
                    b=b+1
                    neg.append(pol_val)
                else:
                    a=a+1
                    pos.append(pol_val)
                sen_values.append(val)
                l.append(row)
                #print("Value: ",pol_val,"\t",sub_val,"-->","Tweet: ",row)
            # score = statistics.mean(sen_values[0])
            # print(score)
            try:
                for i in pos:
                    print('pos :',i)
                for i in neu:
                    print('neu :',i)
                for i in neg:
                    print('neg :',i)
            except BaseException as e:
                print(e)
            #Each word in the lexicon has scores for:
            psum = sum(pos)
            lsum = sum(neg)
            nsum = sum(neu)
            score = psum+lsum+nsum
            # score = statistics.mean(score)
            #print(psum,lsum,nsum)
            if(score == 0):
                label = "Neutral"
            elif(score <=0.0):
                label = "Negative"
            elif(score >=0.0):
                label = "Positive"
            #print('Score :', score, 'Level :', label)
            # piechart(a,b,c)
            return score,label,l,sen_values
    except BaseException as e:
        print(e)
# ============================= 
# Create your views here.

def index(request):
    if request.method == 'POST':
        search=request.POST.get('search','')
        date=request.POST.get('date','')
        text=request.POST.get('text','100')
        num=int(text)
        collect_tweets(search+" -filter:retweets",date,num)
        read_tweets()
        score,lable,tweet,val= read_tweets()
        data = zip(val,tweet)
        params = {'score':score,'lable':lable,'data':data}
        #return render(request,'analysis/index.html')
        return render(request,'analysis/result.html',params)
    else:
        return render(request,'analysis/index.html')


#graphs

class Graph(TemplateView):
    template_name = 'graph.html'
    def get_context_data(self,**kwargs,):
        context = super(Graph, self).get_context_data(**kwargs)
        # N = 1000
        # random_x = np.random.randn(N)
        # random_y = np.random.randn(N)

        # # Create a trace
        # trace = go.Scatter(
        #     x = random_x,
        #     y = random_y,
        #     mode = 'markers'
        # )
        # data=go.Data([trace])
        # layout=go.Layout(title="Meine Daten", xaxis={'title':'x1'}, yaxis={'title':'x2'})
        # figure=go.Figure(data=data,layout=layout)
        try:
            a=0
            b=0
            c=0
            with open('currenttweets.csv','r')as f:
                data = csv.reader(f)
                for row in data:
                    #print(type(row))
                    val = TextBlob(str(row))
                    pol_val,sub_val = val.sentiment.polarity , val.sentiment.subjectivity
                    val=val.sentiment
                    if pol_val == 0.0:
                        c=c+1
                        neu.append(pol_val)
                    elif pol_val < 0.0:
                        b=b+1
                        neg.append(pol_val)
                    else:
                        a=a+1
                label = ['Positive','Negative','Neutral']
                response = [a,b,c]
                figure = go.Figure(data=[go.Pie(labels=label, values=response)])
                div = opy.plot(figure, auto_open=False, output_type='div')
                context['graph'] = div
                return context
        except BaseException as e:
                print(e)

def chart(request):
    g = Graph()
    context = g.get_context_data()
    return render(request,'analysis/graph.html',context)