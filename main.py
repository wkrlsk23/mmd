import os
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

BASEMP3URL = "https://mabinogi.nexon.com/page/pds/music_list.asp?page="
PAGENUM = 3
songlistpage = []
songs = []

def time_calculator(raw_time):
    result = ""
    raw_time = int(raw_time)
    hours = int(raw_time / 3600)
    minute = int(raw_time / 60)
    sec = raw_time % 60
    if hours:
        result += "{0}시 ".format(hours)
    if minute:
        result += "{0}분 ".format(minute)
    result += "{0}초".format(sec)
    return result

def downloadwithurl(url):
    # 다운받을 이미지 url
    url = "https://mabinogi.vod.nexoncdn.co.kr/music/NPC_Eochaid.mp3"
    # time check
    start = time.time()
    # curl 요청
    os.system("curl " + url + " > test.mp3")
    # 이미지 다운로드 시간 체크
    print(time.time() - start)

def getsonglists(soup):
    result = []
    songurls = soup.find('ul', {'class': 'ab_list'}).find_all('li')
    titlelists = soup.find_all('div',{'class': 'ab_title'})
    songcounts = soup.find_all('span',{'class': 'ab_count'})
    urls = ["https://mabinogi.nexon.com/page/pds/"+s.find('a')['href'] for s in songurls]
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
    infos = [i.text.strip().replace(u'\xa0', u' ') for i in infolists]
    for i in range(len(titles)):
        result.append([sl[0],titles[i],infos[i],urls[i]])
    return result

if __name__ == "__main__":
    p_start = time.time()
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
    print("프로그램 종료\n (걸린 시간 : {0})\n".format(time_calculator(time.time() - p_start)))

    __driver.quit()
