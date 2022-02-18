#pylint: disable=missing-function-docstring,missing-module-docstring
from lxml.html import fromstring as fr
from utils.exceptions import DirectLinkError

def get_direct_link(html):
    try:
        return fr(html).xpath('//a[@id="downloadButton"]/@href')[0]
    except IndexError:
        raise DirectLinkError from None
