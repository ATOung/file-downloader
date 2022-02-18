#pylint: disable=C0301,C0103,C0114,C0116
import requests as r
from lxml.html import fromstring as fr
from utils.exceptions import DirectLinkError

def get_direct_link(html,url):
    try:
        tmp=fr(html).xpath("//form[@name=\"F1\"]/input/@value")
        d=f"op={tmp[0]}&id={tmp[1]}&rand={tmp[2]}&referer=&method_free&method_premium=1"
        var=r.post(url,headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36","content-type":"application/x-www-form-urlencoded"},data=d).text
        return fr(var).xpath("//a[@class=\"btn btn-dow\"]/@href")[0]
    except IndexError:
        raise DirectLinkError from None
