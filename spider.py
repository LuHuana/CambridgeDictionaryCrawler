#For Windows:
import sys
sys.path.append('E:\Work_Programs\\codes\\剑桥字典')
from refomat import *

from logging import info
from ssl import CERT_NONE
import pandas as pd
import requests 
from bs4 import BeautifulSoup as bs
import json
import os
import time
import random
from fake_useragent import UserAgent
import re

def fake_ua():
    return {'User-Agent': UserAgent().random}

def interrupt_prevention(finished_word):
    #更新info.json
    cache_files=os.listdir('html_cache')
    c_files=[]
    for file in cache_files:
        c_files.append(file[:-5])
    info_data['cache']=c_files
    info_data['words number']=len(cache_files)
    with open('config/info.json','w',encoding='utf8')as info_file:
        json.dump(info_data,info_file,ensure_ascii=False)
    #更新word.xlsx
    for i in range(words.shape[0]):
        if words.loc[i]['word']==finished_word:
            break
    words_int.drop(i,inplace = True)
    words_int.to_excel('words.xlsx',index=False)

def generate_attribute(a_word,a_language,a_source):
    #补全词典属性从v
    soup=bs('<attribute></attribute>','html.parser')
    attr=soup.attribute

    word=soup.new_tag('word')
    word.append(a_word)
    language=soup.new_tag('language')
    language.append(a_language)
    source=soup.new_tag('source')
    source.append(a_source)

    attr.append(word)
    attr.append(language)
    attr.append(source)
    return attr


source_format={
     'CE':r'^(?P<book>[0-9]{1,2})-(?P<test>[1234])(?P<type>[LRW])-(?P<section>[1234])'  # Cambridge English '12-4R-2'
    ,'IW':r'^(?P<book>\s{0})'                                                           # Indipendent Word
    ,'WB':r'^(?P<section>[0-9]*)-(?P<page>[0-9]*)'                                      # Word Book '10-123'
}
ce_dic={'L':'Listening','R':'Reading'}
def source_analysis(source):
    return re.search(source_format[source[1:3]],source[4:]).groupdict()

# def words_concat(tag):
#     sentence=''
#     for word in tag.children:
#         # print(other)
#         sentence+=word.string
#         # print(type(other))
#     return sentence

#读取初始信息
with open('config/info.json','r',encoding='utf8')as info_file:
    info_data=json.load(info_file)

words=pd.read_excel('words.xlsx',sheet_name="Sheet1") #读取待处理单词
words_int=words.copy()

for i in range(words.shape[0]):
    word=words.loc[i]['word']
    source=words.loc[i]['source']
    print(word)
    #检测单词是否在缓存中，若有直接跳过
    if word in info_data['cache']:
        print('exsist in cache!\n')
        interrupt_prevention(word)
        continue
    #爬取
    url,ch_dic='https://dictionary.cambridge.org/dictionary/english-chinese-simplified/{}'.format(word),True
    # print(url)
    try:
        r=requests.get(url,headers=fake_ua())
    except:
        print('Please check the network!\n')
        continue
    # print('get page')
    r.encoding=r.apparent_encoding
    page=bs(r.text,'html.parser').find('article') #获取页面中主要部分
    if page==None:
        #查英文字典
        url,ch_dic='https://dictionary.cambridge.org/dictionary/english/{}'.format(word),False
        # print(url)
        try:
            r=requests.get(url,headers=fake_ua())
        except:
            print('Please check the network!\n')
            continue
        # print('get page')
        r.encoding=r.apparent_encoding
        page=bs(r.text,'html.parser').find('article') #获取页面中主要部分
        if page==None:
            print('Please check the spell!\n')
            continue
    attr=generate_attribute(word,'ch' if ch_dic else 'en',source)
    framework=bs('<html></html>','html.parser')
    fw=framework.html
    fw.append(attr)
    fw.append(page)

    #写入缓存
    with open('html_cache/{}.html'.format(word),'w',encoding='utf-8') as html_cache:
        html_cache.write(str(fw))
    interrupt_prevention(word)
    #sleep
    time.sleep(random.uniform(0.5,1.5))
    reformat(word)
    continue


    #寻找属性
    md_file=open('md/{}.md'.format(word),'w',encoding='utf-8') #打开md文件
    print('# {}[[new|]]'.format(word),file=md_file) #单词（一级标题）
    source_dic=source_analysis(source)
    #出处（外链）
    if source[1:3]=='CE':
        q_type=ce_dic[source_dic['type']]        
        print('[[{}#Test{}#{}{}]]'.format('Cambridge English'+source_dic['book'],source_dic['test'],q_type,source_dic['section']),file=md_file)
    elif source[1:3]=='IW':
        0
    elif source[1:3]=='WB':
        print('[[{}]]'.format('Words Book-Section'+source_dic['section']),file=md_file)
    print('\n',file=md_file) # 词根词缀、相似词语预留
    #格式
    frames=page.find_all('div',class_='pr entry-body__el')
    count_frame=1
    for frame in frames:
        pos=frame.find('span',class_='pos dpos').text #词性 part of speech
        print('## {:d}. {} (_{}_)'.format(count_frame,word,pos),file=md_file) #词性和出处（外链）
        blocks=frame.find_all('div',class_='def-block ddef_block') #寻找词义区块
        count_block=1
        for block in blocks:
            en_mean=block.find('div',class_='def ddef_d db').text
            ch_mean=block.find('span',class_='trans dtrans dtrans-se break-cj').text if ch_dic else ''
            en_mean,ch_mean=en_mean.replace('\n'," "),ch_mean.replace('\n'," ")
            print('### {:d}.{:d}. {}\n#### {}'.format(count_frame,count_block,en_mean,ch_mean),file=md_file) #中英文翻译
            example_centences=block.find_all('div',class_='examp dexamp')
            for cen in example_centences:
                en_cen=cen.find('span',class_='eg deg').text
                ch_cen=cen.find('span',class_='trans dtrans dtrans-se hdb break-cj').text if ch_dic else ''
                en_cen,ch_cen=en_cen.replace('\n'," "),ch_cen.replace('\n'," ")
                print('- {}\n {}'.format(en_cen,ch_cen),file=md_file) #例句及翻译
            count_block+=1
        count_frame+=1
    url='https://dictionary.cambridge.org/dictionary/{}/{}'.format('english-chinese-simplified' if ch_dic else 'english',word)
    print('\n<a href="{}">[Link]Cambridge Dictionary: {}</a>'.format(url,word),file=md_file)
    print()
    
    md_file.close()

#写入信息
cache_files=os.listdir('html_cache')
c_files=[]
for file in cache_files:
    c_files.append(file[:-5])
info_data['cache']=c_files
info_data['words number']=len(cache_files)
with open('config/info.json','w',encoding='utf8')as info_file:
    json.dump(info_data,info_file,ensure_ascii=False)

#断点保护
#重复单词

