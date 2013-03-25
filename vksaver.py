#! /usr/bin/env python
# -*- coding: utf-8 -*-


# курл нужен чтобы получить линк по которому нас отослали
import pycurl
# для того чтобы забирать вывод из курла
import cStringIO
import urllib
# для парсинга страницы
import lxml.html
import os
# регулярки
import re

email = ''
password = ''
# ID нашего приложения
appID = ''

# путь куда качаем
path = "download"

if appID == '': appID = raw_input("VK Application ID: ");


def getAuthUserRawData():
    global email, password
    email = raw_input("Email: ")
    password = raw_input("Password: ")
    return

# LOGIN INTO VK.COM
def authIntoVk(email, password):
    url = 'https://login.vk.com/?act=login&amp;soft=1&amp;utf8=1&'
    
    buf = cStringIO.StringIO()

    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.FOLLOWLOCATION, 1)
    c.setopt(c.COOKIEJAR, "cookie.txt")
    c.setopt(c.COOKIEFILE, "cookie.txt")
    c.setopt(c.WRITEFUNCTION, buf.write)
    
    postFields = '_origin=https://oauth.vk.com'
    postFields += '&email=' + email + '&pass=' + password
    c.setopt(c.POSTFIELDS, postFields)
    c.setopt(c.POST, 1)
    c.perform()
    c.close()
    buf.close()
    return


# GET TOKEN
def GetTokens():
    global appID
    url = 'http://api.vkontakte.ru/oauth/authorize?'
    # тут id нашего приложения
    url += 'client_id='+appID
    url += '&scope=audio'
    url += '&redirect_uri=http://api.vk.com/blank.html'
    url += '&display=page'
    url += '&response_type=token'

    buf = cStringIO.StringIO()
    # for suppress output
    storage = cStringIO.StringIO() 
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.FOLLOWLOCATION, 1)
    c.setopt(c.COOKIEJAR, "cookie.txt")
    c.setopt(c.COOKIEFILE, "cookie.txt")
    
    c.setopt(c.HEADERFUNCTION, buf.write)
    # for suppress output
    c.setopt(c.WRITEFUNCTION, storage.write)
    
    c.perform()
    tokenURL = c.getinfo(c.EFFECTIVE_URL)
    c.close()

    buf.close()
    storage.close()
    return tokenURL

if os.path.isfile('cookie.txt') != True: getAuthUserRawData()
authIntoVk(email, password)
link = GetTokens()

access_token = re.search('access_token=([0-9A-Fa-f]+)&', link)
expires_in = re.search('expires_in=([0-9A-Fa-f]+)&', link)
user_id = re.search('user_id=([0-9A-Fa-f]+)', link)

if access_token is None: 
    print 'Не удалось, возможно не правильно указан ID приложения или что-то еще =)';
    exit()

access_token = access_token.group(1)
expires_in = expires_in.group(1)
user_id = user_id.group(1)

# PARSING!!!!!!!!

url = "https://api.vkontakte.ru/method/audio.get.xml?uid=" + user_id + "&access_token=" + access_token
page = urllib.urlopen(url)
html = page.read()

print "Список музла получен, парсим..."

artistMas = []
titleMas = []
urlMas = []
number = 0

print "Парсим на предмет исполнителей..."

doc  = lxml.html.document_fromstring(html)
for artist in doc.cssselect('artist'):
    artistMas.append(artist.text)
    number = number + 1
    
print "OK"
print "Парсим на предмет названий..."

for title in doc.cssselect('title'):
    titleMas.append(title.text)
    
print "OK"
print "Парсим на предмет ссылок..."

for urlm in doc.cssselect('url'):
    urlMas.append(urlm.text)
    
print "OK"

print "" 

if os.path.exists(path):
    "Папка уже есть, начинаем докачку"
else:
    os.makedirs(path)

print "Нам нужно скачать кучу файлов. Вычисляем количество..."
print number

answer = raw_input("Готов?: ")
if answer == "y":
    print "Пошла закачка, пошла родимая!"
else:
    print "Вот же какой трусливый! Ну и ладно!"
    exit()

for i in xrange(0, number-1):
    print "Загружается:"
    print i
    print " "
    
    filename_new = path+"/"+artistMas[i]+ " - " + titleMas[i] + ".mp3";
    if os.path.exists(filename_new):
        print "Этот файл уже загружен, переходим к следующему"
    else:				
        downCmd = "wget -P" + path + " " + urlMas[i]
        os.popen(downCmd)

        p = re.compile(r"[0-9a-zA-Z]+\.mp3$")
        filename = p.findall(urlMas[i])
        
        try:
            os.rename(path+"/"+filename[0], path+"/"+artistMas[i]+ " - " + titleMas[i] + ".mp3")
        except:
            print "Невозможно переименовать, оставляю изначальное имя файла!"
    
    print " "
    
print "Задание завершено! Удачи!"