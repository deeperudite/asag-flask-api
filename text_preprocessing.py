# -*- coding: utf-8 -*-
import os
from google.colab import drive
import tensorflow as tf
import pandas as pd
import numpy as np
import string
import zipfile
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.tokenize import word_tokenize,sent_tokenize
from nltk import pos_tag
from nltk.corpus import stopwords
from nltk.tokenize import TweetTokenizer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer
porter = PorterStemmer()
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

!pip3 install rouge==0.3.1 
from rouge import Rouge
!pip3 install textblob
from textblob import TextBlob

def clean(df,tasks,columns):
  
  for column in columns:
      #Lowercase conversion
      df[column] = df[column].apply(lambda x: x.lower())
      print(column+": Converted to lowercase")

      #Tokenization
      df[column] = df[column].apply(word_tokenize)
      df[column] = df[column].apply(lambda x: " ".join(x))
      print(column+": Tokenized")

      if('- ' in tasks):
        #Split a-b into a and b
        df[column] = df[column].str.replace('-',' ')
        print(column+": - Replaced")

      elif('-_' in tasks):
        #Split a-b into a and b
        df[column] = df[column].str.replace('-','_')
        print(column+": - Replaced")

      if('punct' in tasks):
        #Removing punctuations
        df[column] = df[column].str.replace('[^\w\s]',' ')
        print(column+": Removed punctions ")

      if('num' in tasks):
        #Replacing numbers
        df[column] = df[column].str.replace('[0-9]','#')
        print(column+": Replaced Numbers ")

      if('stop' in tasks):
        #Removing Stop Words
        df[column] = df[column].apply(lambda x: " ".join([w for w in x.split() if w not in stop_words]))
        print(column+": StopWords Removed")

      if('lemma' in tasks):
        #Lemmatization - root words
        df[column] = df[column].apply(lambda x: " ".join([lemmatizer.lemmatize(word,pos='v') for word in x.split()]))
        print(column+": Root words Lemmatized")

    
  df['Row_no'] = df.index 
  print("Null values:",df.isnull().values.any())
  #print(df.head())
  return df

def avg_word(sentence):
  words = sentence.split()
  return (sum(len(word) for word in words)/len(words))


def get_basic_features(df,columns):
  
  for column in columns:
    df[column[0]+'_word_count'] = df[column].apply(lambda x: len(str(x).split(" ")))
    print(column+"Word Count Done")
    df[column[0]+'_char_count'] = df[column].str.len()
    print(column+"Char Count Done")
    df[column[0]+'_avg_word'] = df[column].apply(lambda x: avg_word(x))
    print(column+"Avg Word Length Done")

  return df

def tag_part_of_speech(text):
    text_splited = text.split(' ')
    text_splited = [''.join(c for c in s if c not in string.punctuation) for s in text_splited]
    text_splited = [s for s in text_splited if s]
    pos_list = pos_tag(text_splited)
    noun_count = len([w for w in pos_list if w[1] in ('NN','NNP','NNPS','NNS')])
    adjective_count = len([w for w in pos_list if w[1] in ('JJ','JJR','JJS')])
    verb_count = len([w for w in pos_list if w[1] in ('VB','VBD','VBG','VBN','VBP','VBZ')])
    return[noun_count, adjective_count, verb_count]
  
def get_POS(df,columns):
    
    for column in columns: 
      print("Generating POS Features for "+ column)
      df[column[0]+'_nouns'], df[column[0]+'_adjectives'], df[column[0]+'_verbs'] = zip(*df[column].apply(lambda comment: tag_part_of_speech(comment)))
      df[column[0]+'_nouns_vs_length'] = df[column[0]+'_nouns'] / df[column[0]+'_char_count']
      df[column[0]+'_adjectives_vs_length'] = df[column[0]+'_adjectives'] / df[column[0]+'_char_count']
      df[column[0]+'_verbs_vs_length'] = df[column[0]+'_verbs'] /df[column[0]+'_char_count']
      df[column[0]+'_nouns_vs_words'] = df[column[0]+'_nouns'] / df[column[0]+'_word_count']
      df[column[0]+'_adjectives_vs_words'] = df[column[0]+'_adjectives'] / df[column[0]+'_word_count']
      df[column[0]+'_verbs_vs_words'] = df[column[0]+'_verbs'] / df[column[0]+'_word_count']
      
    return df

def get_TFIDF(df,columns):
  d = []
  for column in columns:
    l = []
    for i in df.index:
      l.append(df[column][i])
    tfidf = TfidfVectorizer(min_df = 2, max_df = 4.5, ngram_range=(1,2))
    features =  tfidf.fit_transform(l)
    d.append( pd.DataFrame( features.todense(), columns=tfidf.get_feature_names()) )
  return d

def get_Rogue(df,columns):
  rouge = Rouge()
  l1=[]
  l2=[]
  for i in df.index:
    l1.append(df[columns[0]][i])
    l2.append(df[columns[1]][i])
  return pd.DataFrame( rouge.get_scores(l1,l2) )

def get_Jaccard(df,columns):
  df['Jaccard'] = df['q_avg_word']
  for i in df.index:
    a = set(df[columns[0]][i].split()) 
    b = set(df[columns[1]][i].split())
    c = a.intersection(b)
    df['Jaccard'][i] = float(len(c)) / (len(a) + len(b) - len(c))
  return df

columns = ['question','ref_answer','stu_answer']


# q = "How are you?"
# r = "I am good."
# s = "Dying bro. Ellame reject bro."
# data = pd.DataFrame([[q,r,s]],columns = columns)

temp = get_basic_features(data,columns)

cleaning_tasks = ['lemma','num']
temp = clean(temp,cleaning_tasks,columns)

temp = get_POS(temp,columns)

columns = ['question','ref_answer','stu_answer']
tfidf = get_TFIDF(temp,columns)

sim_columns = ['ref_answer','stu_answer']
scores = get_Rogue(temp,sim_columns)

sim_columns = ['ref_answer','stu_answer']
temp = get_Jaccard(temp,sim_columns)