#pylint: disable=line-too-long, import-error, invalid-name
from typing import Union
from re import findall, sub, match
from pathlib import Path
from lxml.html import fromstring
from zippyshare_downloader import extract_info as zippyinfo
import requests as req
try:
    from downloader import FileDownloader, FileInfoBase, ua
except ModuleNotFoundError:
    from .downloader import FileDownloader, FileInfoBase, ua
req.urllib3.disable_warnings(category=req.urllib3.exceptions.InsecureRequestWarning)

__all__ = (
    'File','Parser',
    'UnsupportedFileHostingError','extract_info',
    'setup_download','ua'
)

class UnsupportedFileHostingError(Exception):
    """Exception for unsupported file hosting"""
    def __init__(self):
        super().__init__("File hosting not supported. Make sure your url is correct.")

class File(FileInfoBase):
    """File information"""
    def __init__(self, data: dict) -> None:
        super().__init__(data)
        self.__data=data

    def __repr__(self) -> str:
        return f"<{self.host} name={self.name} size={self.fmt_size}>"

    def download(self,
        file_name: str=None,
        complete_dir: str=None,
        temp_dir: str=None,
        start_download: bool=True,
        **kwargs) -> FileDownloader:
        """
        Function to setup your download

        Parameters
        ----------
        file_name: str
            You can adjust the file name
        complete_dir: str
            Location to store finished download
        temp_dir: str
            Location to store temporary file
        start_download: bool
            If the start download is False, this function only return FileDownloader class and doesn't start the download
        """
        if file_name is None:
            file_name=self.name
        temp_obj=(Path(".")/(temp_dir if temp_dir else '')/f"{file_name}.temp")
        complete_obj=(Path(".")/(complete_dir if complete_dir else '')/file_name)
        try:
            complete_obj.parent.mkdir(exist_ok=True, parents=True)
            temp_obj.parent.mkdir(exist_ok=True, parents=True)
        except PermissionError as e:
            raise PermissionError("Make sure this program has access create temporary/complete folder!") from e
        file_download=FileDownloader(
            self.__data,
            temp_obj,
            complete_obj,
            **kwargs
        )
        if start_download:
            file_download.download()
        return file_download

class Parser:
    """Parser class to get file info"""
    def __init__(self, url: str):
        self.url=url

    def get_info(self) -> dict:
        '''Get file info from matched file hosting'''
        for key, val in {"anonfiles.com":self.anonbayfiles,"bayfiles.com":self.anonbayfiles,"hxfile.co":self.hxfile,"mediafire.com":self.mediafire,"racaty.net":self.racaty,"solidfiles.com":self.solidfiles,"tusfiles.com":self.tusfiles,"zippyshare.com":self.zippyshare}.items():
            if key in self.url:
                try:
                    return val()
                except IndexError as err:
                    raise FileNotFoundError("File Not Found!") from err
        raise UnsupportedFileHostingError

    def anonbayfiles(self) -> dict:
        """Return Anonfiles and Bayfiles"""
        res=fromstring(req.get(self.url, headers={"User-Agent":ua()}).text)
        download_url=res.xpath('//a[@id=\"download-url\"]/@href')[0]
        fmt_size=findall(r"\((.+)\)",res.xpath('//a[@id="download-url"]')[0].text_content())[0]
        data=req.head(download_url,headers={"User-Agent":ua(),"Connection":"keep-alive"}, allow_redirects=True)
        try:
            size=int(data.headers['content-length'])
        except KeyError:
            size=None
        name=findall('filename="(.+)"',data.headers['Content-Disposition'])[0]
        return {"download_url":download_url,"fmt_size":fmt_size, "host":"anonbayfiles","name":name,"size":size,"url":self.url}

    def hxfile(self) -> dict:
        """Return Hxfile"""
        res=fromstring(req.get(self.url,headers={"User-Agent":ua()}).text)
        res1=res.xpath("//form[@name=\"F1\"]/input/@value")
        fmt_size=res.xpath("//div[@class='size']/span")[1].text
        data=f"op={res1[0]}&id={res1[1]}&rand={res1[2]}&referer=&method_free&method_premium=1"
        res2=req.post(self.url,headers={"User-Agent":ua(),"content-type":"application/x-www-form-urlencoded"},data=data).text
        download_url=fromstring(res2).xpath("//a[@class=\"btn btn-dow\"]/@href")[0]
        data=req.head(download_url,headers={"User-Agent":ua(),"Connection":"keep-alive","Accept-Encoding":"identity"})
        try:
            size=int(data.headers['content-length'])
        except KeyError:
            size=None
        name=download_url.split("/")[-1]
        return {"download_url":download_url,"fmt_size":fmt_size,"host":"hxfile","name":name,"size":size,"url":self.url}

    def mediafire(self) -> dict:
        '''Return mediafire'''
        resp=fromstring(req.get(self.url,headers={"User-Agent":ua()}).text)
        download_url=resp.xpath('//a[@id="downloadButton"]/@href')[0]
        fmt_size=findall(r"\((.+)\)",resp.xpath(r'//a[@id="downloadButton"]')[0].text_content())[0]
        data=req.head(download_url,headers={"User-Agent":ua(),"Connection":"keep-alive"})
        try:
            size=int(data.headers['content-length'])
        except KeyError:
            size=None
        name=findall('filename="(.+)"',data.headers['Content-Disposition'])[0]
        return {"download_url":download_url,"fmt_size":fmt_size,"host":"mediafire","name":name,"size":size,"url":self.url}

    def racaty(self) -> dict:
        '''Return racaty'''
        res=fromstring(req.get(self.url,headers={"User-Agent":ua()}).text)
        res1=res.xpath("//form[@id=\"getExtoken\"]/input/@value")
        fmt_size=res.xpath("//span[@id='rctyFsize']")[0].text
        data=f"op={res1[0]}&id={res1[1]}&rand={res1[2]}&referer=&method_free=&method_premium=1"
        res2=req.post(self.url,headers={"User-Agent":ua()},data=data).text
        download_url=fromstring(res2).xpath("//a[@id='uniqueExpirylink']/@href")[0]
        data=req.head(download_url,headers={"User-Agent":ua(),"Connection":"keep-alive"},verify=False)
        try:
            size=int(data.headers['content-length'])
        except KeyError:
            size=None
        name=download_url.split("/")[-1]
        return {"download_url":download_url,"fmt_size":fmt_size,"host":"racaty","name":name,"size":size,"url":self.url}

    def solidfiles(self) -> dict:
        '''Return solidfiles'''
        res=fromstring(req.get(self.url,headers={"User-Agent":ua()}).text)
        fmt_size=match("(.+)(?=-)",sub(r"(\s)+"," ",res.xpath("//section[@class='box-content meta']/p/text()")[2].replace("\xa0"," ")))[0][:-1][1:]
        data="csrfmiddlewaretoken="+res.xpath('//div[@class=\"buttons\"]/form/input[@name=\"csrfmiddlewaretoken\"]/@value')[0]+"&referrer="
        res1=req.post("http://www.solidfiles.com"+res.xpath('//div[@class=\"buttons\"]/form/@action')[0],headers={"User-Agent":ua()},data=data).text
        download_url=findall('url=(.+)',fromstring(res1).xpath("//meta[@http-equiv=\"refresh\"]/@content")[0])[0]
        data=req.head(download_url,headers={"User-Agent":ua(),"Connection":"keep-alive"})
        try:
            size=int(data.headers['content-length'])
        except KeyError:
            size=None
        name=req.utils.unquote(download_url.split('/')[-1])
        return {"download_url":download_url,"fmt_size":fmt_size,"host":"solidfiles","name":name,"size":size,"url":self.url}

    def tusfiles(self) -> dict:
        '''Return tusfiles'''
        res=fromstring(req.get(self.url,headers={"User-Agent":ua()}).text)
        res1=res.xpath("//form[@method=\"POST\"]/input/@value")
        fmt_size=findall(r"\((.+)\)",res.xpath(r"//span[@class=' text-xs']/small/b/text()")[0])[0]
        data=f"op={res1[0]}&id={res1[1]}&rand={res1[2]}&referer=&method_free=&method_premium=1"
        download_url=req.post(self.url,headers={"User-Agent":ua()}, data=data, allow_redirects=False).headers["location"]
        data=req.head(download_url,headers={"User-Agent":ua(),"Connection":"Keep-Alive"})
        try:
            size=int(data.headers['content-length'])
        except KeyError:
            size=None
        name=download_url.split("/")[-1]
        return {"download_url":download_url,"fmt_size":fmt_size,"host":"tusfiles","name":name,"size":size,"url":self.url}

    def zippyshare(self) -> dict:
        '''Return zippyshare'''
        res=zippyinfo(self.url, False)
        return {"download_url":res.download_url,"fmt_size":res.size_fmt,"host":"zippyshare","name":res.name,"size": int(res.size),"url":self.url}

def extract_info(url: str, download: bool=False, **kwargs) -> Union[File, FileDownloader]:
    """
    Extract the download info

    Returns
    -------
    File
        File class
    """
    result=Parser(url).get_info()
    file=File(result)
    if download:
        file=file.download(**kwargs)
    return file

def setup_download(url: str, **kwargs) -> FileDownloader:
    """
    Only setup for download but doesn't start it
    """
    result=Parser(url).get_info()
    file=File(result).download(start_download=False, **kwargs)
    return file
