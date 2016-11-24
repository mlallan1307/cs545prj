
from senticnet4 import senticnet

import numpy as np
import re
import copy

def get_lines(fn):
  lines = []
  with open(fn) as handle:
    for l in handle:
      lines.append(l)
  return lines

#############################################################3

def load_sentiment(fn):
  lines = get_lines(fn)
  senti = {}
  for l in lines:
    if not l.startswith('#'):
      ls = l.split(',')
      words = ls[4].split()
      for i in range(len(words)):
        tmp = words[i]
        tmp = re.sub(r'#\d*', '', tmp)
        if tmp in senti:
          senti[tmp][0] += float(ls[2]) # positive
          senti[tmp][1] += float(ls[3]) # negative
          senti[tmp][2] += 1
        else:
          senti[tmp] = [float(ls[2]), float(ls[3]), 1]

  rtn = {}
  for k, v in senti.items():
    pos = v[0]/v[2]
    neg = v[1]/v[2]
    if pos == 0 and neg == 0:
      continue
    rtn[k] = [pos, neg]
  return rtn


def load_sentiment_senticnet():
  senti = {}

  for k, v in senticnet.items():
    revK = ' '.join(k.split('_'))
    data = [float(v[0]), float(v[1]), float(v[2]), float(v[3]), float(v[7])]
    if revK in senti:
      print("Dup:", revK, k)
      exit()
    senti[revK] = data
  return senti

#############################################################3

def load_stockData(fn):
  lines = get_lines(fn)
  stocks = {}
  for l in lines:
    if not l.startswith('Date'):
      ls = l.split(',')
      stocks[ls[0]] = float(ls[4]) - float(ls[1])
  '''
  values = np.array([])
  # calculate std
  for k, v in stocks.items():
    values = np.append(values, v)
  d0 = np.std(values)*0.1
  d1 = np.std(values)
  '''
  for k, v in stocks.items():
    c = 0
    if v > 0:
      c = 1
    '''
    if v > d1:
      c = 2
    elif v < (-1*d1):
      c = -2
    elif v > d0:
      c = 1
    elif v < (-1*d0):
      c = -1
    '''
    stocks[k] = c
  return stocks

#############################################################3

def load_newsReddit(fn):
  lines = get_lines(fn)
  news = {}
  prev_day = {}
  lines_new = []
  lc = ''
  for l in lines:
    if not l.startswith('Date'):
      if re.search(r'^20\d{2}-\d{2}-\d{2}', l):
        lines_new.append(re.sub('\n', '', l))
      else:
        lines_new[-1] += re.sub('\n', '', l)

  for i, l in enumerate(lines_new):
    ls = l.split(',')
    n = l[len(ls[0])+1:]
    rm1_list = r'\'s|^b\'|^\"b\'|^\"b\"'
    rm_list = r'"|\'|\.|,|:|\t|\||;|\?|\!|\$|^b|\[|\]|\(|\)|\\r|\\n|\\'
    sp_list = r'\s+-\s+|-\s+|--+'
    n = n.strip()
    n = re.sub(rm1_list, '', n)
    n = re.sub(rm_list, '', n)
    n = re.sub(sp_list, ' ', n)
    n = n.lower()
    n = n.strip()
    if ls[0] in news:
      news[ls[0]].append(n)
    else:
      news[ls[0]] = [n]
      if i < len(lines_new)-1:
        prev_day[(lines_new[i-1].split(','))[0]] = ls[0]

  counts = {}
  for k, v in news.items():
    words = {}
    for n in v:
      w = n.split()
      for cw in w:
        cw = cw.lower()
        if cw in words:
          words[cw] += 1
        else:
          words[cw] = 1
    counts[k] = words
  return counts, prev_day


def load_newsReddit_senticnet(fn):
  lines = get_lines(fn)
  news = {}
  prev_day = {}
  lines_new = []
  lc = ''
  for l in lines:
    if not l.startswith('Date'):
      if re.search(r'^20\d{2}-\d{2}-\d{2}', l):
        lines_new.append(re.sub('\n', '', l))
      else:
        lines_new[-1] += re.sub('\n', '', l)

  for i, l in enumerate(lines_new):
    ls = l.split(',')
    n = l[len(ls[0])+1:]
    rm1_list = r'\'s|^b\'|^\"b\'|^\"b\"'
    rm_list = r'"|\'|\.|,|:|\t|\||;|\?|\!|\$|^b|\[|\]|\(|\)|\\r|\\n|\\'
    sp_list = r'\s+-\s+|-\s+|--+'
    n = n.strip()
    n = re.sub(rm1_list, '', n)
    n = re.sub(rm_list, '', n)
    n = re.sub(sp_list, ' ', n)
    n = n.lower()
    n = n.strip()
    if ls[0] in news:
      news[ls[0]].append(n)
    else:
      news[ls[0]] = [n]
      if i < len(lines_new)-1:
        prev_day[(lines_new[i-1].split(','))[0]] = ls[0]

  return news, prev_day

#############################################################3

def combine_data(sentiment, stocks, news):
  rtn = []
  for date, words in news.items():
    if date not in stocks:
      continue
    pos = 0
    neg = 0
    for word, freq in words.items():
      if word in sentiment:
        pos += (sentiment[word][0])*freq
        neg += (sentiment[word][1])*freq
    rtn.append([date, str(pos), str(neg), str(stocks[date])])
  return rtn


def combine_data_senticnet(sentiment, stocks, news):
  rtn = []
  for date, dayNews in news.items():
    if date not in stocks:
      continue
    v = np.zeros(5)
    for word, value in sentiment.items():
      for story in dayNews:
        v = np.add(v, np.multiply(story.count(word), value))
    rtn.append([date, str(v[0]), str(v[1]), str(v[2]), str(v[3]), str(v[4]), str(stocks[date])])
  return rtn

#############################################################3

def combine_data_prev(sentiment, stocks, news, prev_day):
  rtn = []
  for date, words in news.items():
    if date not in stocks:
      continue
    pos = 0
    neg = 0
    for word, freq in words.items():
      if word in sentiment:
        pos += (sentiment[word][0])*freq
        neg += (sentiment[word][1])*freq
    pos_p = 0
    neg_p = 0
    for word, freq in news[prev_day[date]].items():
      if word in sentiment:
        pos_p += (sentiment[word][0])*freq
        neg_p += (sentiment[word][1])*freq
    rtn.append([date, str(pos), str(neg), str(pos_p), str(neg_p), str(stocks[date])])
  return rtn


def combine_data_prev_senticnet(sentiment, stocks, news, prev_day):
  rtn = []
  for date, dayNews in news.items():
    if date not in stocks:
      continue
    v = np.zeros(5)
    v_p = np.zeros(5)
    for word, value in sentiment.items():
      for story in dayNews:
        v = np.add(v, np.multiply(story.count(word), value))
      for story in news[prev_day[date]]:
        v_p = np.add(v_p, np.multiply(story.count(word), value))
    rtn.append([date,
                str(v[0]), str(v[1]), str(v[2]), str(v[3]), str(v[4]),
                str(v_p[0]), str(v_p[1]), str(v_p[2]), str(v_p[3]), str(v_p[4]),
                str(stocks[date])])
  return rtn

#############################################################3

def print_dataset(data, fn):
  with open(fn, 'w') as handle:
    handle.write('#Date,news positivity,news negativity,stock change\n')
    d = copy.deepcopy(data)
    d.sort(key=lambda x: x[0])
    for l in d:
      handle.write(','.join(l))
      handle.write('\n')


def print_dataset_prev(data, fn):
  with open(fn, 'w') as handle:
    handle.write('#Date,news positivity,news negativity,yesterday news positivity, yesterday news negativity,stock change\n')
    d = copy.deepcopy(data)
    d.sort(key=lambda x: x[0])
    for l in d:
      handle.write(','.join(l))
      handle.write('\n')


def print_dataset_prev_only(data, fn):
  with open(fn, 'w') as handle:
    handle.write('#Date,yesterday news positivity, yesterday news negativity,stock change\n')
    d = copy.deepcopy(data)
    d.sort(key=lambda x: x[0])
    for l in d:
      ln = [l[0]]
      ln.extend(l[3:])
      handle.write(','.join(ln))
      handle.write('\n')

#############################################################3

def print_dataset_senticnet(data, fn):
  with open(fn, 'w') as handle:
    handle.write('#Date,'\
                 'news pleasantness,news attention,news sensitivity,news aptitude,news polarity,'\
                 'stock change\n')
    d = copy.deepcopy(data)
    d.sort(key=lambda x: x[0])
    for l in d:
      handle.write(','.join(l))
      handle.write('\n')


def print_dataset_prev_senticnet(data, fn):
  with open(fn, 'w') as handle:
    handle.write('#Date,'\
                 'news pleasantness,news attention,news sensitivity,'\
                 'news aptitude,news polarity,'\
                 'prev news pleasantness,prev news attention,prev news sensitivity,'\
                 'prev news aptitude,prev news polarity,'\
                 'stock change\n')

    d = copy.deepcopy(data)
    d.sort(key=lambda x: x[0])
    for l in d:
      handle.write(','.join(l))
      handle.write('\n')


def print_dataset_prev_only_senticnet(data, fn):
  with open(fn, 'w') as handle:
    handle.write('#Date,'\
                 'prev news pleasantness,prev news attention,prev news sensitivity,'\
                 'prev news aptitude,prev news polarity,'\
                 'stock change\n')
    d = copy.deepcopy(data)
    d.sort(key=lambda x: x[0])
    for l in d:
      ln = [l[0]]
      ln.extend(l[6:])
      handle.write(','.join(ln))
      handle.write('\n')

#############################################################3

if __name__ == "__main__":
  senti = load_sentiment('SentiWordNet.csv')
  stocks = load_stockData('DJIA_table.csv')
  news_reddit, prev_day = load_newsReddit('RedditNews.csv')
  combined = combine_data(senti, stocks, news_reddit)
  combined_p = combine_data_prev(senti, stocks, news_reddit, prev_day)

  print_dataset(combined, 'stockSentimentA.csv')
  exit()
  print_dataset_prev(combined_p, 'stockSentimentAWithPrev.csv')
  print_dataset_prev_only(combined_p, 'stockSentimentAOnlyPrev.csv')

  #############################################################3

  senti = load_sentiment_senticnet()
  stocks = load_stockData('DJIA_table.csv')
  news_reddit, prev_day = load_newsReddit_senticnet('RedditNews.csv')
  # The below takes 7 hours to run
  combined = combine_data_senticnet(senti, stocks, news_reddit)
  combined_p = combine_data_prev_senticnet(senti, stocks, news_reddit, prev_day)

  print_dataset_senticnet(combined, 'stockSentimentB.csv')
  print_dataset_prev_senticnet(combined_p, 'stockSentimentBWithPrev.csv')
  print_dataset_prev_only_senticnet(combined_p, 'stockSentimentBOnlyPrev.csv')
