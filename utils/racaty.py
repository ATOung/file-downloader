#pylint: disable=missing-function-docstring,missing-module-docstring,C0301,C0103
import requests as r
from lxml.html import fromstring as fr
from utils.exceptions import DirectLinkError

def get_direct_link(html, url):
    try:
        tmp=fr(html).xpath("//form[@id=\"getExtoken\"]/input/@value")
        d=f"op={tmp[0]}&id={tmp[1]}&rand={tmp[2]}&referer=&method_free=&method_premium=1"
        _=r.post(url,headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"},data=d).text
        return fr(_).xpath("//a[@id='uniqueExpirylink']/@href")[0]
    except IndexError:
        raise DirectLinkError from None
