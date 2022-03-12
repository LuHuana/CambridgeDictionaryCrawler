from fake_useragent import UserAgent
from bs4 import BeautifulSoup as bs
import pandas as pd
import requests 
import random
import time
import json
import os
import re

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

def reformat(word):
    # print(word)
    #打开原始文件保留前两行
    r=open('html_cache/{}.html'.format(word),'r',encoding='utf-8')
    framework=bs(r,'lxml')
    page=framework.find('article') #获取页面中主要部分
    attr=framework.find('attribute') #获取页面中主要部分
    #打开新文件并覆盖
    md_file=open('md/{}.md'.format(word),'w',encoding='utf-8')
    ch_dic=True if attr.language.text=='ch' else False
    source=attr.source.text
    # print(source)
    source_dic=source_analysis(source)
    # print('# {}{}'.format(word,'[[new|]]'if source=='[CE]10-4R-1' else ''),file=md_file) #单词（一级标题）
    print('# {}'.format(word),file=md_file) #单词（一级标题）  
    if source[1:3]=='CE':
        q_type=ce_dic[source_dic['type']]        
        # print('[[{}#Test{}#{}{}]]'.format('Cambridge English '+source_dic['book'],source_dic['test'],q_type,source_dic['section']),file=md_file)
        print('[[{}-{}{}-{}]]'.format(source_dic['book'],source_dic['test'],source_dic['type'],source_dic['section']),file=md_file)
    elif source[1:3]=='IW':
        print('',file=md_file)
    elif source[1:3]=='WB':
        print('[[{}]]'.format('Words Book-Section'+source_dic['section']),file=md_file)
    print('',file=md_file)
    print('',file=md_file)
    #重定义格式
    ch_mean=page.find('span',class_='trans dtrans dtrans-se break-cj')
    ch_dic=False if ch_mean==None else True #判断英文字典
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
    # time.sleep(random.uniform(0.5,1.5))



if __name__ == '__main__':
    #读取初始信息
    with open('info.json','r',encoding='utf8')as info_file:
        info_data=json.load(info_file)
    words=info_data['cache']
    for i in range(len(words)):
        word=words[i]
        reformat(word)
    #写入信息
    cache_files=os.listdir('html_cache')
    c_files=[]
    for file in cache_files:
        c_files.append(file[:-5])
    info_data['cache']=c_files
    info_data['words number']=len(cache_files)
    with open('info.json','w',encoding='utf8')as info_file:
        json.dump(info_data,info_file,ensure_ascii=False)
