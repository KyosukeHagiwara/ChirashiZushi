#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import fnmatch
import subprocess
import wget 
from bs4 import BeautifulSoup
import urllib, urllib2
import re
from time import sleep
from datetime import datetime
from tweepy.streaming import StreamListener, Stream
from tweepy.auth import OAuthHandler
from tweepy.api import API
import ConfigParser


now = datetime.now().strftime("%s")
parent = "./data/" + now
os.makedirs(parent)



# Scraping KASUMI and get Chirashi Data
def chirashi_search():
    dat = open("./data/kasumi_sakura.html", "r").read()
    kasumi_soup = BeautifulSoup(dat, "lxml")
    chirashis = []
    for chirashi in kasumi_soup.select("#chirashiList1")[0].children:
        c_id = chirashi.get("id")
        c_scheme = chirashi.select(".shufoo-scheme")[0].contents[0]
        c_url = chirashi.select(".shufoo-pdf")[0].a.get("href")
        c_data = (c_id, c_scheme, c_url)
        chirashis.append(c_data)
    return chirashis

# generate pdf data from redirect URL
def gen_chirashi_pdf(c_data, parent_path):
    target = c_data[2]
    red = urllib2.urlopen(target).read()
    red_soup = BeautifulSoup(red, "lxml")
    url = red_soup.meta.get("content").lstrip("0;URL=")
    path = parent_path + "/" + re.findall(r"[0-9]+", c_data[0])[0] + ".pdf"
    if subprocess.call(["python", "-m", "wget", "-o", path, url]) != 0:
                    print "failed: {0}".format(url)
    return path

# convert Chirashi pdf to png
def pdf_to_png(root_path):
    for dirpath, _, filenames in os.walk(root_path):
        for filename in filenames:
            if fnmatch.fnmatch(filename, u"*.pdf"):
                org_path = os.path.join(dirpath, filename)
                ppp = dirpath
                ppp_path = os.path.join(ppp, filename)
                png_path = ppp_path.replace(".pdf", ".png")
                print(png_path)

                print "convert {0} to {1}".format(org_path, png_path)

                if subprocess.call(["convert", "-density", "100", "-trim", org_path, png_path]) != 0:
                    print "failed: {0}".format(org_path)


# return twitter oath
def get_oauth():
    conf = ConfigParser.SafeConfigParser()
    conf.read("twitter.ini")
    auth = OAuthHandler(conf.get("Twitter", "CK"), conf.get("Twitter", "CS"))
    auth.set_access_token(conf.get("Twitter", "AT"), conf.get("Twitter", "AS"))
    return auth

# test tweet function
def update_tweet(text):
    auth = get_oauth()
    api = API(auth)
    api.update_status(status=text)

# tweet Chirashi images 
def chirath(root_path, scheme):
    auth = get_oauth()
    api = API(auth)
    reply_id = None
    text = unicode(scheme).encode('utf-8')  
    for dirpath, _, filenames in os.walk(root_path):
        for filename in filenames:
            if fnmatch.fnmatch(filename, "*.png"):
                st = api.update_with_media(filename=(root_path + "/" + filename), status=text, in_reply_to_status_id=reply_id)
                print(type(st))
                reply_id = st.id
                sleep(5)
        else:
            reply_id = None


# def chirath_test(filename, text=None, reply_id=None):
#     auth = get_oauth()
#     api = API(auth)
#     st = api.update_with_media(filename=filename, status="aaa", reply_id=reply_id)

if __name__ == '__main__':
    chirashis = chirashi_search()
    for chirashi in chirashis:
        now = datetime.now().strftime("%s")
        p_path = parent + "/" + now
        os.makedirs(p_path)

        gen_chirashi_pdf(chirashi, p_path)
        sleep(5)
        pdf_to_png(p_path)
        sleep(10)
        chirath(p_path, chirashi[1])
    # chirath_test("./data/icon.jpeg")
 