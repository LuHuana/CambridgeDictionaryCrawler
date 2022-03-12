import pandas as pd
import requests 
from bs4 import BeautifulSoup as bs
import json
import os
import time
import random
from fake_useragent import UserAgent

with open('config/link.json','r',encoding='utf8')as links_file:
    links=json.load(links_file)['new']
link_bak=links[:]

words_group_new=['despoil','spoil'] # 提前输入 或是
# 逐个输入
if words_group_new==[]:
    print('input words one by one, press enter to continue while finish:')
    while True:
        word=input()
        if word=='':
            break
        words_group_new.append(word)
else:
    print('already input:')
print(words_group_new)

# 寻找已有分组
found_group=False # 未找到分组标识
for count_words_group in range(len(links)):
    words_group=links[count_words_group]
    list_and=list(set(words_group_new)&set(words_group)) # 逐个求交集
    # 交集数量大于等于3则认为可以与原始相关词汇合并
    if len(list_and)>=3:
        print('has found relative words list:')
        print(words_group)
        if input('type "yes" to merge: ')=='yes':
            found_group=True
            new_words=list(set(words_group_new)^set(list_and))
            for word in new_words:
                links[count_words_group].append(word)
            break
if not found_group:
    links.append(words_group_new)

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
        line3=lines[3][:-1]
        linkages_,linkages=line3.split(" "),[]
        for linkage in linkages_:
            linkages.append(linkage[2:-2])
        #添加新链接
        for new_link in words_group:
            if (new_link==word) or (new_link in linkages):
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
    'old':link_bak
}

with open('config/link.json','w',encoding='utf8')as links_file:
    links=json.dump(link_dic,links_file)