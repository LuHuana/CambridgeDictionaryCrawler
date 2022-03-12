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

def get_link(word):
    md=open('md/{}.md'.format(word),'r',encoding='utf-8')
    lines=[]
    for line in md:
        lines.append(line)
    md.close()
    line3=lines[3][:-1]
    linkages_,linkages=line3.split(" "),[]
    for linkage in linkages_:
        linkages.append(linkage[2:-2])
    return linkages[1:]

with open('info.json','r',encoding='utf8')as info_file:
    info_data=json.load(info_file)
words=info_data['cache']

groups=[]
exist=[]
for word in words:
    if word in exist:
        continue
    linkages=get_link(word)
    for word1 in linkages:
        linkages1=get_link(word1)
        for word2 in linkages:
            if word1==word2:
                continue
            for group in groups:
                if word1 in group and word2 in group:
                    group.append(word)
                    break
            if word2 in linkages1:
                # print(word,word1,word2)
                exist.append(word)
                exist.append(word1)
                exist.append(word2)
                groups.append([word,word1,word2])
                break

for group in groups:
    print(group)
            
#只找到核心，需要外扩