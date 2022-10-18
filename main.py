from email.mime import application
from genericpath import isfile
import os
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

EXCEPTTEXT = {"\\" : '', "/" : '', ":" : '',"*" : '',"?" : '',"\"" : '',"<" : '',">" : '',"|" : ''}
BASEMP3URL = "https://mabinogi.nexon.com/page/pds/music_list.asp?page="
BASEMABURL = "https://mabinogi.nexon.com/page/pds/"
PAGENUM = 3
songlistpage = []
songs = []
resulturls = './mabinogi_mp3/'

def replace_except(text,dic):
    result = text
    for i, j in dic.items():
        result = result.replace(i,j)
    return result

def time_calculator(raw_time):
    result = ""
    hours = int(raw_time / 3600)
    minute = int(raw_time / 60)
    sec = raw_time % 60
    if hours:
        result += "{0}시 ".format(hours)
    if minute:
        result += "{0}분 ".format(minute)
    result += "{0:0.1f}초".format(sec)
    return result

def createFolder(path):
    try:
        if not os.path.exists(path):
            os.makedirs(path)
    except OSError:
        print ("디렉토리 생성에 실패하였습니다.\n")

def downloadwithurl(url,name):
    if os.path.isfile(name+".mp3") is False:
        os.system("curl -s " + url + " > " +"\""+ name + ".mp3" + "\"")

def getsonglists(soup):
    result = []
    songurls = soup.find('ul', {'class': 'ab_list'}).find_all('li')
    titlelists = soup.find_all('div',{'class': 'ab_title'})
    songcounts = soup.find_all('span',{'class': 'ab_count'})
    urls = [BASEMABURL+s.find('a')['href'] for s in songurls]
    titles = [t.text.strip() for t in titlelists]
    counts = [c.text.replace('곡','') for c in songcounts]
    for i in range(len(titles)):
        result.append([titles[i],urls[i],counts[i]])
    return result

def getsong(soup,sl):
    result = []
    songurls = soup.find('ul',{'class':'mp_list'}).find_all('a',{'herf':'#'})
    titlelists = soup.find_all('span',{'class': 'mp_txt'})
    infolists = soup.find_all('span',{'class': 'mp_icons'})
    urls = [u["data-src"] for u in songurls]
    titles = [t.text.strip() for t in titlelists]
    infos = [i.text.strip().replace(u'\xa0', u' ').replace('\n','') for i in infolists]
    for i in range(len(titles)):
        result.append([sl[0],titles[i],infos[i],urls[i]])
    return result

if __name__ == "__main__":
    p_start = time.time()
    if os.path.isfile('result.txt') is False:
        print("이전 결과를 찾지 못하였습니다.\n")
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('window-size=1920x1080')
        options.add_argument("--disable-gpu")
        options.add_argument("--log-level=3")
        __driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        print("Driver ON!\n")

        start = time.time()
        for t in range(PAGENUM):
            __driver.delete_all_cookies()
            __driver.get(BASEMP3URL+str(t+1))
            __driver.find_element(by=By.TAG_NAME, value='body').send_keys(Keys.END)
            soup = BeautifulSoup(__driver.page_source, 'lxml')
            songlistpage += getsonglists(soup)
        print("페이지 초기화 종료\n (걸린 시간 : {0})\n".format(time_calculator(time.time() - start)))

        start = time.time()
        for ts in range(len(songlistpage)):
            __driver.delete_all_cookies()
            __driver.get(songlistpage[ts][1])
            __driver.find_element(by=By.TAG_NAME, value='body').send_keys(Keys.END)
            soup = BeautifulSoup(__driver.page_source, 'lxml')
            songs += getsong(soup,songlistpage[ts])
        print("곡 리스팅 종료\n (걸린 시간 : {0})\n".format(time_calculator(time.time() - start)))

        with open('result.txt','w',encoding='utf-8') as f:
            for s in songs:
                f.write("{0};{1};{2};{3}\n".format(s[0],s[1],s[2],s[3]))
            f.close()
        print("프로그램 종료\n (총 걸린 시간 : {0})\n".format(time_calculator(time.time() - p_start)))

        __driver.quit()
    else:
        print("이전 결과를 찾았습니다.\n")
        data = []
        with open('result.txt','r',encoding='utf-8') as f:
            while True:
                t = f.readline()
                if t == "":

                    break
                data.append(t.split(';'))
            f.close()
        if data == []:
            os.remove('result.txt')
            print("이전 결과가 잘못되었습니다. 프로그램을 다시 실행해주세요.\n")
            quit()
        createFolder(resulturls)
        titlelist = []
        for d in data :
            if not d[0] in titlelist:
                titlelist.append(d[0])
        for t in titlelist:
            createFolder(resulturls+replace_except(t,EXCEPTTEXT))
            q_start = time.time()
            for d in data :
                if d[0] == t :
                    downloadwithurl(d[3].replace('\n',''),resulturls+replace_except(t,EXCEPTTEXT)+'/'+replace_except(d[1],EXCEPTTEXT))
            f = time.time() - q_start
            if f > 0.1 :
                print(f"{t} 그룹 다운로드 완료.({time_calculator(f)})")
        print("프로그램 종료\n (총 걸린 시간 : {0})\n".format(time_calculator(time.time() - p_start)))
        