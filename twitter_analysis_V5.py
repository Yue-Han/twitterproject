####required files: a list of the tweets files, the tweets files, positive-words, negative-words
####save "tweets",postive,negative,list in to the same folder --- path

##import packages##
import time
from datetime import date
from datetime import datetime
from nltk.util import ngrams
import nltk
from nltk.corpus import stopwords
import re
import os
import csv
from pymining import itemmining

#load list of terms to give set.
def loadLexicon(fname,lex):
    f=open(fname)
    for line in f:
        line=line.strip()
        if line.startswith(';') or len(line)==0: continue
        lex.add(line) 
    f.close()

#load the positive and negative lexicons
pos=set()
neg=set()
loadLexicon('positive-words.txt',pos)
loadLexicon('negative-words.txt',neg)

#set English stop words#
english_stopwords = stopwords.words('english')

##twitter analysis##
def twitter_analysis(path,files):
    tweets=[]
    words=[]
    bigrams=[]
    hashtags=[]
    mentions=[]
    twitterpic=[]
    instagrampic=[]
    otherUrls=[]
    positive_terms=[]
    negative_terms=[]
    usefulwords=[]

    #read input files and save tweets#
    f=open(str(path)+'/tweets/'+str(files)+'.txt_parsed.txt_final.txt')
    for line in f:
        if line.startswith('@@@'):
            try:
                tweet=line.strip().lower().split('\t')[3]
            except IndexError:
                tweet=" "
            tweets.append(tweet)
            
            #words#
            terms=tweet.split()
            words.append(terms)

            ##useful words##
            usefulword=[]
            for term in terms:
                if term in english_stopwords: continue          
                else: usefulword.append(term)
            usefulwordt=tuple(usefulword)
            usefulwords.append(usefulwordt)            
            usefulwordst=tuple(usefulwords)
            
            #two grams#
            twograms=ngrams(terms, 2)
            tgs=[]
            for twogram in twograms:
                joined='_'.join(twogram)
                tgs.append(joined) ##the original code will return genrator so I changed##
            bigrams.append(tgs)

            #hash tags#
            myHashtags=re.findall('#[^ ]+',tweet)
            hashtags.append(myHashtags)

            #mentions#
            myMentions=re.findall('@[^ ]+',tweet)
            mentions.append(myMentions)

            #twitter pic#
            myTp=re.findall('pic.twitter.com/[^ ]+',tweet)
            twitterpic.append(myTp)

            #instagram pic#
            myIp=re.findall('http://instagram.com/p/[^ ]+',tweet)
            instagrampic.append(myIp)            
            
            #other Url#
            otherUrl=re.findall('http://[^ ]+',tweet)
            other=[]
            for Url in otherUrl:
                if "http://instagram.com/p/" not in Url:
                    other.append(Url)
            otherUrls.append(other)
          
            #positive words#
            myPos=[]
            for term in terms:
                if term in english_stopwords: continue          
                if term in pos:myPos.append(term)
            positive_terms.append(myPos)

            #negative words#
            myNeg=[]
            for term in terms:
                if term in english_stopwords: continue          
                if term in neg:myNeg.append(term)
            negative_terms.append(myNeg)

##twitter_analysis('/Users/yuehan/Desktop/twitter','tial.txt_parsed.txt_final.txt')##This is for demo analysis

    ##save csv files##
    newpath = str(path)+'/text_results/'
    if not os.path.exists(newpath): os.makedirs(newpath)
    
    with open(str(path)+'/text_results/'+str(files)+'_textresults.csv','wb') as f1:
        w=csv.writer(f1)
        row1=['tweets','words','bigrams','hashtags','mentions','twitterpic','instagrampic','otherUrls','positive_terms','negative_terms']
        w.writerow(row1)
        for v in range(0,len(tweets)):
            tweetss=tweets[v]
            wordss=words[v]
            wordss=','.join(wordss)
            bigramss=bigrams[v]
            bigramss=','.join(bigramss)
            hashtagss=hashtags[v]
            hashtagss=','.join(hashtagss)
            mentionss=mentions[v]
            mentionss=','.join(mentionss)
            twitterpics=twitterpic[v]
            twitterpics=','.join(twitterpics)
            instagrampics=instagrampic[v]
            instagrampics=','.join(instagrampics)
            otherUrlss=otherUrls[v]
            otherUrlss=','.join(otherUrlss)
            positive_termss=positive_terms[v]
            positive_termss=','.join(positive_termss)
            negative_termss=negative_terms[v]
            negative_termss=','.join(negative_termss)

            w.writerow([tweetss,wordss,bigramss,hashtagss,mentionss,twitterpics,instagrampics,otherUrlss,positive_termss,negative_termss])

    ##find frequent Item Sets (which shows up more than 3 times, I tried with 5 and some will have blank sets)
    relim_input = itemmining.get_relim_input(usefulwordst)
    report = itemmining.relim(relim_input, min_support=3)
    ##print report.keys()
    newpath = str(path)+'/frequentsets/'
    if not os.path.exists(newpath): os.makedirs(newpath)
    writer=csv.writer(open(str(path)+'/frequentsets/'+str(files)+'_frequentsets.csv','wb'))
    for key,value in report.items():
        if "', '" in str(key):
            key=str(key)
            key=key.replace("frozenset(['","")
            key=key.replace("'])","")
            key=key.replace('frozenset(["','')
            key=key.replace('"])','')
            key=key.replace("',",",")
            key=key.replace('",',',')
            key=key.replace(', "',', ')
            key=key.replace(", '",", ")
            writer.writerow([key,value])
        else:
            pass


#####################matching topic###################################
def topiccheck(path,files):
    topics=[]
    topicindex={}
    #load the frequent sets and create the topic dictionary#
    r=csv.reader(open(str(path)+'/frequentsets/'+str(files)+'_frequentsets.csv'))
    for rows in r:
        topics.append(rows[0])
    for t in range(0,len(topics)):
        topicindex[t]=topics[t]

    #save the topic index#
    newpath = str(path)+'/topicindex/'
    if not os.path.exists(newpath): os.makedirs(newpath)
    writer=csv.writer(open(str(path)+'/topicindex/'+str(files)+'_topicindex.csv','wb'))
    for key,value in topicindex.items():
        writer.writerow([key,value])
        

def matchtopic(path,files):
    index=[]
    topicns=[]
    topicmatch=[]
    #read the index file#
    r=csv.reader(open(str(path)+'/topicindex/'+str(files)+'_topicindex.csv'))
    for rows in r:
        index.append(rows[0])
        topicns.append(rows[1])
    
    #read the tweets#
    tweets=[]
    f=open(str(path)+'/tweets/'+str(files)+'.txt_parsed.txt_final.txt')
    for line in f:
        if line.startswith('@@@'):
            try:
                tweet=line.strip().lower().split('\t')[3]
            except IndexError:
                tweet=" "
            tweets.append(tweet)

    ##do the match for each tweet##
    for w in range(0,len(tweets)):
        topiceach=[]
        eachtweet=tweets[w]
        for t in range(0,len(topicns)):
            eachtopic=topicns[t]
            eachindex=index[t]
            eachword=eachtopic.strip().lower().split(', ')
            s=1
            for k in range(0,len(eachword)):
                if eachword[k] in eachtweet:
                    e=1
                    s=s*e
                else:
                    e=0
                    s=s*e
            if s==1:
                topiceach.append(eachindex)
            else:
                pass
        topicmatch.append(topiceach)

    ##save the file##
    newpath = str(path)+'/topicmatch_result/'
    if not os.path.exists(newpath): os.makedirs(newpath)

    with open(str(path)+'/topicmatch_result/'+str(files)+'_topicmatch.csv','wb') as f1:
        w=csv.writer(f1)
        row1=['tweets','topics']
        w.writerow(row1)
        for v in range(0,len(tweets)):
            tweetss=tweets[v]
            topicmatchs=topicmatch[v]
            w.writerow([tweetss,topicmatchs])

###########################converting time########################
def converttime(path,files):

    retweets=[]
    favorites=[]
    timestamp=[]
    timeminute=[]
    #load list of terms to give set.
    f=open(str(path)+'/tweets/'+str(files)+'.txt_parsed.txt_final.txt')
    for line in f:
        if line.startswith('@@@'):
            try:
                at=line.strip().lower().split('\t')[0]
                username=line.strip().lower().split('\t')[1]
                tweetid=line.strip().lower().split('\t')[2]
                tweet=line.strip().lower().split('\t')[3]
                
                line1=next(f)
                start=line1.strip().split('\t')[2]
                firstretweet=line1.strip().split('\t')[0]
                firstfav=line1.strip().split('\t')[1]
            except IndexError:
                tweetid=" "
                start=" "
                tweet=""
                print "tweet is blank"
            retweets.append(at)
            retweets.append(firstretweet)
            favorites.append(username)
            favorites.append(firstretweet)
            timestamp.append(tweetid)
            timeminute.append(tweet)
            timestamp.append(start)
            timeminute.append("1")
        if "2014-0" in line:
            retweet=line.strip().split('\t')[0]
            fave=line.strip().split('\t')[1]
            try:
                retime=line.strip().split('\t')[2]
                #print retime
            except IndexError:
                retime=" "
                print "time is blank"
            try:
                nowtime=datetime.strptime(retime,' %Y-%m-%d %H:%M:%S')
                firsttime=datetime.strptime(start,' %Y-%m-%d %H:%M:%S')
                timed=str(nowtime-firsttime)
                timed=timed.replace(" day, ",":")
                timed=timed.replace(' days, ',":")
                #print timed
                try:
                    d, h, m, s= [int(i) for i in timed.split(':')]
                    tmin= 24*60*d+60*h+m
                except ValueError:
                    h,m,s=[int(i) for i in timed.split(':')]
                    tmin=60*h+m+1
                #print tmin
                timeminute.append(tmin)
            except ValueError:
                timeminute.append("")
            retweets.append(retweet)
            favorites.append(fave)
            timestamp.append(retime)

    newpath = str(path)+'/timeconvert_results/'
    if not os.path.exists(newpath): os.makedirs(newpath)

    rows=zip(retweets,favorites,timestamp,timeminute)
    with open(str(path)+'/timeconvert_results/'+str(files)+'_timeconvert.csv','wb')as f:
        writer = csv.writer(f)
        for row in rows:
            writer.writerow(row)


    
##run all files##
print '"/Users/yuehan/Desktop/twitter"'
path=input('path is:')

l=[]
r = csv.reader(open(str(path)+'/list.csv'))
for rows in r:
    l.append(rows[0])
print l

for j in range(0,len(l)):
    files=l[j]
    a=twitter_analysis(path,files)
    b=topiccheck(path,files)
    c=matchtopic(path,files)
    d=converttime(path,files)
    print j

###V5 contains the function of text analysis, date converting and frequentset matching
###problems remained:
###1)
#######if term in english_stopwords: continue
#######UnicodeWarning: Unicode equal comparison failed to convert both arguments to Unicode - interpreting them as being unequal
###2)tiny.pic
#######didn't find tiny.pic. But 8 exist. But it is not necessaryly picture, some are articles, some are photos, some are videos.
