from bs4 import BeautifulSoup
import requests
from pandas import DataFrame
import pandas as pd
import time
import re
import jieba
import pandas as df
import numpy
import matplotlib.pyplot as plt
import matplotlib
from wordcloud import WordCloud

def GetNowPlayingList(url):
    r = requests.get(url)
    html = r.text
    soup = BeautifulSoup(html,'lxml')
    nowplaying_movie = soup.find_all('div',attrs={'id':'nowplaying'})
    list = nowplaying_movie[0].find_all('li', class_='list-item')
    # print(list[0])
    name = [] ; score = [] ; star = [] ; release = [] ; duration = [] ;
    region = [] ;director = []; actor = []
    for item in list:
        name.append(item['data-title'])
        score.append(item['data-score'])
        star.append(item['data-star'])
        release.append(item['data-release'])
        duration.append(item['data-duration'])
        region.append(item['data-region'])
        director.append(item['data-director'])
        actor.append(item['data-actors'])
    print(name)
    print(score)
    list_info = zip(score,star,release,duration,region,director,actor)
    data = dict(zip(name,list_info))
    print(data)
    return data

def StoreTo_csv(data):
    frame = pd.DataFrame(data,index = ['score','star','release','duration','region','derector','actors'])
    frame = frame.T
    print(frame)
    frame.to_csv('movie.csv',encoding='utf-8')

def GetMovieComment(movieId,pageNum):
    requrl = 'https://movie.douban.com/subject/' + movieId + '/comments?start=' + pageNum + '&limit=20&sort=new_score&status=P'
    print(requrl)
    r = requests.get(requrl)
    html = r.text
    soup = BeautifulSoup(html,'lxml')
    comment = soup.find_all('span',attrs={'class':'short'})
    commentList = []
    for item in comment:
        # print(item)
        itemstr = str(item)
        t0 = itemstr.find('>')
        t1 = itemstr.find('/span')
        # print(t0,t1)
        itemstr = itemstr[t0+1:t1-1]
        commentList.append(itemstr)
    return commentList

def StoreTo_txt(comment_list1):
    with open("test.txt", "w", encoding='utf-8') as f:
        f.write(comment_list1)


url = 'https://movie.douban.com/cinema/nowplaying/hangzhou/'
url2 = 'https://movie.douban.com/cinema/nowplaying/beijing/'
data = GetNowPlayingList(url)
StoreTo_csv(data)
print("电影信息保存完毕！")

time.sleep(5)
movieId = '3168101' #毒液的电影id
page = 20
comment_temp = []
comment_list = []
for i in range(1,20):
    pageNum = str(page * i);
    comment_temp = GetMovieComment(movieId,pageNum)
    comment_list = comment_list + comment_temp
# print(comment_list)
s = ''
for i in range(len(comment_list)):
    s = s + comment_list[i]
pattern = re.compile(r'[\u4e00-\u9fa5]+')
filterdata = re.findall(pattern, s)
cleaned_comments = ''.join(filterdata)
StoreTo_txt(cleaned_comments)
print('影评信息保存完毕!')

segment = jieba._lcut(cleaned_comments)
print(segment)
words_df=pd.DataFrame({'segment':segment})
"""去停用词"""
stopwords=pd.read_csv("stopwords.txt",index_col=False,quoting=3,sep="\t",names=['stopword'], encoding='utf-8')#quoting=3全不引用
words_df=words_df[~words_df.segment.isin(stopwords.stopword)]
"""词频统计"""
words_stat=words_df.groupby(by=['segment'])['segment'].agg({"计数":numpy.size})
words_stat=words_stat.reset_index().sort_values(by=["计数"],ascending=False)
print(words_stat.head(30))


matplotlib.rcParams['figure.figsize'] = (10.0,5.0)
plt.rcParams['savefig.dpi'] = 300 #图片像素
plt.rcParams['figure.dpi'] = 300 #分辨率
wordcloud = WordCloud(font_path='SimHei.ttf',background_color='white',max_font_size=60)
word_frequence = {x[0]:x[1] for x in words_stat.head(1000).values}
word_frequence_list = []
for key in word_frequence:
    temp = (key,word_frequence[key])
    word_frequence_list.append(temp)

wordcloud = wordcloud.fit_words(dict(word_frequence_list))
plt.imshow(wordcloud)
plt.savefig("result.jpg")
