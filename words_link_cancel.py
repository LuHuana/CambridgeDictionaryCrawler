import pandas as pd
import requests 
from bs4 import BeautifulSoup as bs
import json
import os
import time
import random
from fake_useragent import UserAgent

with open('config/link.json','r',encoding='utf8')as links_file:
    links=json.load(links_file)['old']
link_bak=links[:]

for words_group in links:
    for word in words_group:
        # print(word)
        #打开旧文件
        md=open('md/{}.md'.format(word),'r',encoding='utf-8')
        lines=[]
        for line in md:
            lines.append(line)
        md.close()
        #获取链接单词列表
        line3=''
        #添加新链接
        for new_link in words_group:
            if new_link==word:
                continue
            line3='{} [[{}]]'.format(line3,new_link)
        line3+='\n'
        #写入文件
        # print(line3)
        lines[3]=line3
        md_new=open('md/{}.md'.format(word),'w',encoding='utf-8')
        for line in lines:
            print(line,end='',file=md_new)

# 与备份一起写入文件
link_dic={
    'new':links,
    'old':links
}

with open('config/link.json','w',encoding='utf8')as links_file:
    links=json.dump(link_dic,links_file)

print('canceled')