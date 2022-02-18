#pylint: disable=C0301,C0114,C0116,C0103,W0123
from re import findall
from lxml.html import fromstring as fr
from utils.exceptions import DirectLinkError

def get_direct_link(html, url):
    try:
        var=fr(html).xpath("//a[@id=\"dlbutton\"]/following-sibling::script/text()")[0].splitlines()[1][:-1]
        var=var.replace("document.getElementById('dlbutton').href =","")
        _=findall(r"\((.+)\)",var)[0]
        var=var.replace(f"({_})",f"\"{eval(_)}\"")
        return "https://"+(url).split("/")[2]+eval(var)
    except IndexError:
        raise DirectLinkError from None
