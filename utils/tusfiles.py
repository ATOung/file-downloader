#pylint: disable=C0301,C0114,C0116,C0103
import requests as r
from lxml.html import fromstring as fr
from utils.exceptions import DirectLinkError

def get_direct_link(html, url):
    try:
        tmp=fr(html).xpath("//form[@method=\"POST\"]/input/@value")
        d=f"op={tmp[0]}&id={tmp[1]}&rand={tmp[2]}&referer=&method_free=&method_premium=1"
        return r.post(url,headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"},data=d,allow_redirects=False).headers["location"]
    except IndexError:
        raise DirectLinkError from None
