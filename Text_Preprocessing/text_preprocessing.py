# -*- coding: utf-8 -*-
"""py_Text_Preprocessing.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1_JVQOvV2kzd7bf0KGCWmwKQwE7vg_yGZ

## Libraries
"""

import os
from google.colab import drive
import tensorflow as tf
import pandas as pd
import numpy as np
import string
import zipfile
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
nltk.download('all')
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

# q_basic = ['q_word_count','q_char_count','q_avg_word']
# a_basic = ['r_word_count','r_char_count','r_avg_word','s_word_count','s_char_count','s_avg_word']
# q_pos_basic = ['q_nouns','q_adjectives','q_verbs']
# q_pos_adv = ['q_nouns_vs_length','q_adjectives_vs_length','q_verbs_vs_length',
#              'q_nouns_vs_words','q_adjectives_vs_words','q_verbs_vs_words']
# a_pos_basic = ['r_nouns','r_adjectives','r_verbs','s_nouns','s_adjectives','s_verbs',]
# a_pos_adv = ['r_nouns_vs_length','r_adjectives_vs_length','r_verbs_vs_length',
#              'r_nouns_vs_words','r_adjectives_vs_words','r_verbs_vs_words',
#              's_nouns_vs_length','s_adjectives_vs_length','s_verbs_vs_length',
#              's_nouns_vs_words','s_adjectives_vs_words','s_verbs_vs_words']
# similarity = ['Jaccard','bm25']
# rouge1 = ['r1_f','r1_p','r1_r']
# rouge2 = ['r2_f','r2_p','r2_r']
# rougel = ['rlcs_f','rlcs_p','rlcs_r']
# new_pos1 = ['s_verbs_vs_r_verbs','s_nouns_vs_r_nouns','s_adjectives_vs_r_adjectives',
#             's_word_count_vs_r_word_count','s_nouns_vs_words_vs_r_nouns_vs_words',
#             's_verbs_vs_words_vs_r_verbs_vs_words','s_adjectives_vs_words_vs_r_adjectives_vs_words']
# new_pos2 = ['rd_word_diff','rs_noun_vs_words_diff','rs_verb_vs_words_diff','rs_adjectives_vs_words_diff']
# ibm_feat = ['precision','recall','F1_score']
# q_tags = ['how_flag','what_flag','why_flag','who_flag','which_flag','when_flag','where_flag','whom_flag']

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
  
def get_basic_POS(df,columns):
    
    for column in columns: 
      print("Generating Basic POS Features for "+ column)
      df[column[0]+'_nouns'], df[column[0]+'_adjectives'], df[column[0]+'_verbs'] = zip(*df[column].apply(lambda comment: tag_part_of_speech(comment)))
      
    return df  
  
def get_advanced_POS(df,columns):
    
    for column in columns: 
      print("Generating Advanced POS Features for "+ column)
      df[column[0]+'_nouns_vs_length'] = df[column[0]+'_nouns'] / df[column[0]+'_char_count']
      df[column[0]+'_adjectives_vs_length'] = df[column[0]+'_adjectives'] / df[column[0]+'_char_count']
      df[column[0]+'_verbs_vs_length'] = df[column[0]+'_verbs'] /df[column[0]+'_char_count']
      df[column[0]+'_nouns_vs_words'] = df[column[0]+'_nouns'] / df[column[0]+'_word_count']
      df[column[0]+'_adjectives_vs_words'] = df[column[0]+'_adjectives'] / df[column[0]+'_word_count']
      df[column[0]+'_verbs_vs_words'] = df[column[0]+'_verbs'] / df[column[0]+'_word_count']
      
    return df

def get_Jaccard(df,columns):
  df['Jaccard'] = df['q_avg_word']
  for i in df.index:
    a = set(df[columns[0]][i].split()) 
    b = set(df[columns[1]][i].split())
    c = a.intersection(b)
    df['Jaccard'][i] = float(len(c)) / (len(a) + len(b) - len(c))
  return df

def get_TFIDF(df,columns):
  d = []
  for column in columns:
    l = []
    for i in df.index:
      l.append(df[column][i])
    tfidf = TfidfVectorizer(min_df = 1, max_df = 4.5, ngram_range=(1,2))
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

def fab(row, types):
    if(row['r_'+types]!=0):
        return row['s_'+types]/row['r_'+ types]
    else:
        return 0
def get_new_POS1(data):
  data['s_verbs_vs_r_verbs'] = data.apply(lambda x : fab(x,"verbs"), axis = 1)
  data['s_nouns_vs_r_nouns'] = data.apply(lambda x : fab(x,"nouns"), axis = 1)
  data['s_adjectives_vs_r_adjectives'] = data.apply(lambda x : fab(x,"adjectives"), axis = 1)
  data['s_word_count_vs_r_word_count'] = data['s_word_count']/data['r_word_count']
  data['s_nouns_vs_words_vs_r_nouns_vs_words'] = data.apply(lambda x : fab(x, "nouns_vs_words"), axis = 1)
  data['s_verbs_vs_words_vs_r_verbs_vs_words'] = data.apply(lambda x : fab(x, "verbs_vs_words"), axis = 1)
  data['s_adjectives_vs_words_vs_r_adjectives_vs_words'] = data.apply(lambda x : fab(x, "adjectives_vs_words"), axis = 1)
  return data

def get_new_POS2(data):
  data['rs_word_diff'] = data['r_word_count'] - data['s_word_count']
  data['rs_noun_vs_words_diff'] = data['r_nouns_vs_words'] - data['s_nouns_vs_words']
  data['rs_verb_vs_words_diff'] = data['r_verbs_vs_words'] - data['s_verbs_vs_words']
  data['rs_adjectives_vs_words_diff'] = data['r_adjectives_vs_words'] - data['s_adjectives_vs_words']
  return data

def get_question_tags(df):
  tags = ['how', 'what', 'why', 'who', 'which','when','where','whom']
  for tag in tags:
    df[tag+"_flag"] = df['question'].apply(lambda x: bool(x.split().count(tag)))
  return df

q = "How are you?"
r = "I am good."
s = "Dying bro. Ellame reject bro."
#l = [[q,r,s]]
columns = ['question','ref_answer','stu_answer']
data = pd.DataFrame([[q,r,s]],columns = columns)

columns = ['question','ref_answer','stu_answer']

temp = get_basic_features(data,columns)

cleaning_tasks = ['lemma','num']
temp = clean(temp,cleaning_tasks,columns)

temp = get_basic_POS(temp,columns)
temp = get_advanced_POS(temp,columns)

sim_columns = ['ref_answer','stu_answer']
temp = get_Jaccard(temp,sim_columns)

temp['bm25'] = 0

sim_columns = ['ref_answer','stu_answer']
scores = get_Rogue(temp,sim_columns)
r1 = pd.DataFrame(scores)['rouge-1'].apply(pd.Series)
r2 = pd.DataFrame(scores)['rouge-2'].apply(pd.Series)
r3 = pd.DataFrame(scores)['rouge-l'].apply(pd.Series)
r = pd.concat([r1,r2,r3] , axis = 1, )
r.columns = ['r1_f','r1_p','r1_r','r2_f','r2_p','r2_r','rlcs_f','rlcs_p','rlcs_r']
temp = pd.concat([temp,r],axis = 1)

temp = get_new_POS1(temp)
temp = get_new_POS2(temp)


temp['precision'] = 0
temp['recall'] = 0
temp['F1_score'] = 0

temp = get_question_tags(temp)

temp.drop(['question','ref_answer','stu_answer','Row_no'], axis=1, inplace=True)
temp.columns