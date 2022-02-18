#pylint: disable=C0103,C0301,C0114,C0116
from re import findall
from lxml.html import fromstring as fr
import requests as r
from utils.exceptions import DirectLinkError

def get_direct_link(html):
    try:
        tmp=fr(html)
        d="csrfmiddlewaretoken="+tmp.xpath('//div[@class=\"buttons\"]/form/input[@name=\"csrfmiddlewaretoken\"]/@value')[0]+"&referrer="
        url=r.post("http://www.solidfiles.com"+tmp.xpath('//div[@class=\"buttons\"]/form/@action')[0],headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"},data=d).text
        return findall('url=(.+)',fr(url).xpath("//meta[@http-equiv=\"refresh\"]/@content")[0])[0]
    except IndexError:
        raise DirectLinkError from None
