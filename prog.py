'''File Downloader'''

#pylint: disable=line-too-long, invalid-name, eval-used, import-outside-toplevel
from math import floor
from random import choice
from platform import system as ps
from shutil import move
from re import findall
from time import time, sleep
from typing import Union
from threading import Event as tevent
import sys, os, json, argparse, concurrent.futures
if sys.version_info[0] != 3:
    print("[Err] Run with python3!")
    sys.exit()

try:
    from lxml.html import fromstring as fr
    from requests.exceptions import ChunkedEncodingError
    import requests as r, yaml
    r.urllib3.disable_warnings(category=r.urllib3.exceptions.InsecureRequestWarning)
except ModuleNotFoundError:
    print("Install required package with \'pip install -r requirements.txt\'")
    sys.exit()

kill_event=tevent()
class FileHostingNotSupported(Exception):
    '''Exception for not supported file hosting'''
    def __init__(self):
        super().__init__("File Hosting doesn't supported. Please check your url!")

class ThreadPaused(Exception):
    '''Exception for paused thread'''

def banner(mode: str) -> None:
    '''Banner'''
    print(rf"""{de} ______ _ _         _____  _
|  ____(_) |       |  __ \| |
| |__   _| | ___   | |  | | |
|  __| | | |/ _ \  | |  | | |
| |    | | |  __/  | |__| | |____
|_|    |_|_|\___   |_____/|______|
Author : https://github.com/XniceCraft
Mode : {mode}
""")

def start(mode: str, url: str) -> None:
    '''Start'''
    if "https://" in url or "http://" in url:
        os.system(clear)
        banner(mode)
        test()
        sleep(2)
        os.system(clear)
        banner(mode)
        return
    print(f"{re}[Err] Invalid URL scheme. There is no http/https in URL{de}")
    sys.exit()

def test() -> None:
    '''Test your internet ping with singapore firstmedia server.'''
    print(f"{re}[{ye}%{re}] {cy}Testing your connection{de}")
    try:
        print(f"{re}[{wh}%{re}] {ye}Pinging to Singapore Firstmedia speedtest server")
        s=time()
        r.get("http://sg-speedtest.fast.net.id.prod.hosts.ooklaserver.net:8080", timeout=3)
        s2=time()
        ping=int((round(s2 - s, 3))*1000)
        if ping < 500:
            print(f"{gr}[G] Your connection is good | Ping : {ping}ms")
        elif 500 <= ping < 1000:
            print(f"{ye}[N] Your connection is ok | Ping : {ping}ms")
        else:
            print(f"{re}[B] Your connection is bad | Ping : {ping}ms")
    except (r.exceptions.ConnectTimeout,r.exceptions.ReadTimeout):
        print(f"{re}[Err] Connection Timeout. Ping exceeds 3000ms{de}")
        sys.exit()
    except r.exceptions.ConnectionError:
        print(f"{re}[Err] Connection Error!{de}")
        sys.exit()

def ua() -> str:
    '''Return Random User-Agent'''
    return choice(["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36","Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.62"])

class DL:
    '''Main class to handle the download'''
    def __init__(self, chunk: int, mode: str, threads: int, url: str, tmp_dir: str, complete_dir: str, direct: bool=False, resume: Union[bool, dict]=False):
        #Temporary directory
        self.tmp_dir=tmp_dir
        #Completed download directory
        self.complete_dir=complete_dir
        #File name
        self.fname: str=None
        #File size with its unit
        self.modified_size: str=None
        #File size on bytes
        self.rawsize: Union[int, None]=None
        #Url grab result
        self.url_grab: str=None
        #Bytes that already downloaded
        self.downloaded_bytes: int=0
        #Array of boolean that returned from multithread_list
        self.threads_data_list=[]
        #Array of position number and boolean value
        self.multithread_list=[]
        #User input url
        self.url=url
        #Multithreaded or singlethreaded
        self.mode=mode
        #Chunk size
        self.chunk=chunk
        #Resume or not
        self.resume=resume
        #Return direct url or not
        self.direct=direct
        #File download position
        self.download_pos={}
        self.data={'threads': threads, "can_paused": 'Yes'}
        #Self.host
        if "mediafire.com" in url:
            self.host="mediafire"
        elif "solidfiles.com" in url:
            self.host="solidfiles"
        elif "tusfiles.com" in url:
            self.host="tusfiles"
        elif "bayfiles.com" in url or "anonfiles.com" in url:
            self.host="anonbayfiles"
        elif "racaty.net" in url:
            self.host="racaty"
        elif "zippyshare.com" in url:
            self.host="zippyshare"
        elif "hxfile.co" in url:
            self.host="hxfile"
        else:
            raise FileHostingNotSupported
        if isinstance(resume, dict):
            self.fname=resume["name"]
            self.downloaded_bytes=resume["downloaded"]
            self.rawsize=resume["rawsize"]
            self.download_pos=resume["download_pos"]
            if mode == "multi":
                self.multithread_list=resume["threads_result"]
                self.threads_data_list=[i["Val"] for i in self.multithread_list]

    def ai(self):
        '''Calculate where the thread start and stop'''
        for i in range(self.data['threads']):
            if i == 0:
                self.download_pos[1]={"start":0, "end":floor(self.rawsize/self.data['threads'])}
            elif i+1 == self.data['threads']:
                self.download_pos[i+1]={"start":floor(self.rawsize/self.data['threads'])*i+1, "end":self.rawsize}
            else:
                self.download_pos[i+1]={"start":floor(self.rawsize/self.data['threads'])*i+1, "end":floor(self.rawsize/self.data['threads'])*(i+1)}

    def download(self, pos: Union[dict, None]=None, thread_number: Union[int, None]=None):
        '''Download function for multi and singlethread'''
        try:
            if self.mode == 'multi' or bool(self.mode == 'single' and self.resume):
                resp=r.Session().get(self.url_grab, headers={"User-Agent":ua(), "Range":f"bytes={pos['start']}-{pos['end']}"}, stream=True, timeout=5, verify=False)
            elif self.mode == 'single':
                resp=r.Session().get(self.url_grab, headers={"User-Agent":ua()}, stream=True, timeout=5, verify=False)
            if not self.resume:
                io_mode="wb"
            elif self.resume:
                io_mode="ab"
                if self.mode == 'multi':
                    self.download_pos[thread_number]["start"]-=os.path.getsize(f"{self.tmp_dir}/{self.fname}-{thread_number}")
        except (r.exceptions.ConnectionError, r.exceptions.ReadTimeout):
            if self.mode == "single":
                return {"Pos":1,"Val":False}
            return {"Pos":thread_number,"Val":False}
        if self.mode == "multi":
            with open(f"{self.tmp_dir}/{self.fname}-{thread_number}",io_mode) as f:
                try:
                    for l in resp.iter_content(chunk_size=self.chunk*1024):
                        f.write(l)
                        self.downloaded_bytes += len(l)
                        if kill_event.is_set():
                            raise KeyboardInterrupt
                    f.close()
                    self.download_pos[thread_number]["start"]+=os.path.getsize(f"{self.tmp_dir}/{self.fname}-{thread_number}")
                    return {"Pos":thread_number,"Val":True}
                except (r.exceptions.ConnectionError, ChunkedEncodingError,r.exceptions.ReadTimeout, KeyboardInterrupt):
                    f.close()
                    self.download_pos[thread_number]["start"]+=os.path.getsize(f"{self.tmp_dir}/{self.fname}-{thread_number}")
                    return {"Pos":thread_number,"Val":False}
        with open(f"{self.tmp_dir}/{self.fname}",io_mode) as f:
            try:
                start_timer=time()
                for data_value in resp.iter_content(chunk_size=self.chunk*1024):
                    try:
                        f.write(data_value)
                        self.downloaded_bytes += len(data_value)
                        if self.downloaded_bytes != 0:
                            speed=int(self.downloaded_bytes / (time() - (start_timer)) / 1000)
                        else:
                            speed=0
                        if self.rawsize is None:
                            done="Unavailable"
                        else:
                            done=f"{round(100 * self.downloaded_bytes / self.rawsize,2)}%"
                        sys.stdout.write(f"{cy}\r> [Downloading] Progress : {done} | Speed: {speed} KB/s")
                        sys.stdout.flush()
                    except KeyboardInterrupt as e:
                        if self.downloaded_bytes is not None:
                            raise KeyboardInterrupt from e
                f.close()
                if self.downloaded_bytes is not None:
                    _=os.path.getsize(f"{self.tmp_dir}/{self.fname}")
                    self.downloaded_bytes=_
                    self.download_pos["start"]+=self.download_pos["start"]+_
            except (r.exceptions.ConnectionError, ChunkedEncodingError, r.exceptions.ReadTimeout, KeyboardInterrupt) as e:
                f.close()
                if self.rawsize is None:
                    print(f"{re}[!] Download Error{de}")
                    sys.exit(1)
                _=os.path.getsize(f"{self.tmp_dir}/{self.fname}")
                self.downloaded_bytes=_
                self.download_pos["start"]+=_
                raise ThreadPaused from e

    def finish(self):
        '''Handle when the download finished'''
        if self.resume and os.path.isfile(f"{self.tmp_dir}/{self.fname}.log"):
            os.remove(f"{self.tmp_dir}/{self.fname}.log")
        if self.mode == "multi":
            with open(f"{self.tmp_dir}/{self.fname}","ab") as file:
                for i in range(self.data['threads']):
                    with open(f"{self.tmp_dir}/{self.fname}-{i+1}","rb") as h:
                        file.write(h.read())
                    h.close()
                    os.remove(f"{self.tmp_dir}/{self.fname}-{i+1}")
            file.close()
        move(rf"{self.tmp_dir}/{self.fname}",rf"{self.complete_dir}/{self.fname}")
        print(f"{gr}\n> [Finished] Success download {self.fname}{de}")

    def multidl_handler(self):
        '''Handle the multithreaded download'''
        if self.resume:
            print(f"{ye}> [Info] Resuming")
            with concurrent.futures.ThreadPoolExecutor() as executor:
                failedthread=[val["Pos"] for val in self.multithread_list if not val["Val"]]
                run=[executor.submit(self.download, self.download_pos[_], _) for _ in failedthread]
                now=time()
                try:
                    old_downloaded_bytes=self.downloaded_bytes
                    while False in [i.done() for i in run]:
                        sleep(1)
                        try:
                            speed=int((self.downloaded_bytes-old_downloaded_bytes) / (time() - (now+1)) / 1000)
                        except ZeroDivisionError:
                            speed=0
                        done=f"{round(100 * self.downloaded_bytes / self.rawsize,2)}%"
                        sys.stdout.write(f"{cy}\r> [Downloading] Progress : {done} | Speed: {speed} KB/s")
                        sys.stdout.flush()
                except KeyboardInterrupt:
                    kill_event.set()
                    sys.stdout.write(f"{cy}\r> [Downloading] Progress : {done} | Speed: {speed} KB/s")
                    print(f"\n{re}[I] Interrupted")
        elif not self.resume:
            print(f"{ye}> [Info] Downloading")
            with concurrent.futures.ThreadPoolExecutor() as executor:
                run=[executor.submit(self.download, self.download_pos[thread+1], thread+1) for thread in range(self.data['threads'])]
                now=time()
                try:
                    while False in [i.done() for i in run]:
                        sleep(1)
                        try:
                            speed=int(self.downloaded_bytes / (time() - (now+1)) / 1000)
                        except ZeroDivisionError:
                            speed=0
                        done=f"{round(100 * self.downloaded_bytes / self.rawsize, 2)}%"
                        sys.stdout.write(f"{cy}\r> [Downloading] Progress : {done} | Speed: {speed} KB/s")
                        sys.stdout.flush()
                except KeyboardInterrupt:
                    kill_event.set()
                    sys.stdout.write(f"{cy}\r> [Downloading] Progress : {done} | Speed: {speed} KB/s")
                    print(f"\n{re}[I] Interrupted")
        return run

    @staticmethod
    def multithreaded_test(url, threads):
        '''Test how much threads server can handle'''
        def runtest(req_session_obj, url):
            return bool(req_session_obj.get(url, headers={"User-Agent":ua()}, stream=True, timeout=10, verify=False).status_code in [200,201,202,206])
        try:
            with r.Session() as req:
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    result=[executor.submit(runtest, req, url) for _ in range(threads)]
                    value=[future.result() for future in concurrent.futures.as_completed(result)]
            return value.count(True)
        except r.exceptions.ConnectionError:
            print(f"{re}[Err] Connection Error{de}")
            sys.exit()
        except r.exceptions.ReadTimeout:
            print(f"{re}[Err] Connection Timeout after 10000ms")
            sys.exit()

    def paused(self):
        '''Paused Handler'''
        self.resume=True
        if self.mode == "single":
            print(f"{gr}\r\n> Download paused. Resume, exit or remove(res/e/rem)?")
            ask=input("> ")
            if ask.lower() == "e" or ask.lower() == "exit":
                with open(f"{self.tmp_dir}/{self.fname}.log", "w", encoding="utf-8") as f:
                    f.write(str(yaml.safe_dump({"Source":self.url,"Size":self.rawsize, "Name":self.fname, "Downloaded":self.downloaded_bytes, "Threads":1, "Mode":self.mode, "Download-Pos": self.download_pos})))
                f.close()
                print(f"{gr}[>] Exit{de}")
                sys.exit()
            elif ask.lower() == "rem" or ask.lower() == "remove":
                os.remove(f"{self.tmp_dir}/{self.fname}")
                print(f"{gr}Sucessfully remove {self.fname}{de}")
                sys.exit()
            os.system(clear)
            banner(self.mode)
            self.run()
        elif self.mode == "multi":
            kill_event.clear()
            print(f"\r{gr}> {self.threads_data_list.count(False)} thread(s) failed. Try again, exit or remove(t/e/r)?")
            ask=input("> ")
            if ask.lower() == "e" or ask.lower() == "exit":
                with open(f"{self.tmp_dir}/{self.fname}.log","w",encoding="utf-8") as f:
                    f.write(str(yaml.safe_dump({"Source":self.url,"Size":self.rawsize, "Name":self.fname, "Downloaded":self.downloaded_bytes, "Threads":self.data["threads"], "Mode":self.mode, "Download-Pos": self.download_pos, "Threads-Result":self.multithread_list})))
                f.close()
                print(f"{gr}[>] Exit{de}")
                sys.exit()
            elif ask.lower() == "r" or ask.lower() == "resume":
                for i in range(self.data['threads']):
                    os.remove(f"{self.tmp_dir}/{self.fname}-{i+1}")
                print(f"{re}> {gr}File {cy}{self.fname} {gr}was successfully removed{de}")
                return
            os.system(clear)
            banner(self.mode)
            self.downloaded_bytes=0
            for i in range(self.data['threads']):
                self.downloaded_bytes+=os.path.getsize(f"{self.tmp_dir}/{self.fname}-{i+1}")
            self.run()

    def run(self):
        '''Handle the entire process'''
        get_url=Grabber(self.url)
        for key, value in {"mediafire":get_url.mediafire,"solidfiles":get_url.solidfiles,"tusfiles":get_url.tusfiles,"anonbayfiles":get_url.anonbayfiles,"racaty":get_url.racaty,"zippyshare":get_url.zippyshare,"hxfile":get_url.hxfile}.items():
            if self.host == key:
                try:
                    grab_result=value()
                    if not self.resume:
                        self.url_grab, self.rawsize, self.fname=grab_result
                    elif self.resume:
                        self.url_grab=grab_result[0]
                    del grab_result
                    break
                except IndexError:
                    print(f"{re}[X] File not found")
                    sys.exit(1)
        del get_url
        if self.direct:
            print(f"{gr}>>> [{wh}={gr}] Link : {cy}{self.url_grab}{de}")
            return
        if self.rawsize is None:
            self.data['can_paused']="No"
            self.mode="single"
            self.modified_size="null"
        else:
            self.modified_size=Prog.getsize(self.rawsize)
        print(f"""{de}> [INFO] Filename : {self.fname}
         Size : {self.modified_size}
         Pausable : {self.data['can_paused']}""")
        if self.mode == "single":
            if not self.resume:
                print(f"{ye}> [Info] Downloading")
                try:
                    self.download_pos={"start":0,"end":self.rawsize}
                    self.download()
                    self.finish()
                    sys.exit()
                except ThreadPaused:
                    self.paused()
            print(f"{ye}> [Info] Resuming")
            try:
                self.download(pos=self.download_pos)
                self.finish()
                sys.exit()
            except ThreadPaused:
                self.paused()
        elif self.mode == "multi":
            if not self.resume:
                self.data['threads']=self.multithreaded_test(self.url, self.data['threads'])
                self.ai()
            try:
                run=self.multidl_handler()
            except KeyboardInterrupt:
                pass
            self.multithread_list=sorted([i.result() for i in concurrent.futures.as_completed(run)], key=lambda p: p["Pos"])
            self.threads_data_list=[i["Val"] for i in self.multithread_list]
            if all(self.threads_data_list):
                print(f"\r\n{de}> Assembling file into one solid file. Please wait!",end="")
                self.finish()
                return
            self.paused()

class Grabber:
    '''Grab url from site'''
    def __init__(self, url: str):
        self.url=url

    def mediafire(self) -> list:
        '''Return mediafire'''
        newurl=fr(r.get(self.url,headers={"User-Agent":ua()}).text).xpath('//a[@id="downloadButton"]/@href')[0]
        data=r.head(newurl,headers={"User-Agent":ua(),"Connection":"keep-alive"})
        try:
            rawsize=int(data.headers['content-length'])
        except KeyError:
            rawsize=None
        name=findall('filename="(.+)"',data.headers['Content-Disposition'])[0]
        return [newurl,rawsize,name]

    def solidfiles(self) -> list:
        '''Return solidfiles'''
        temp=fr(r.get(self.url,headers={"User-Agent":ua()}).text)
        d="csrfmiddlewaretoken="+temp.xpath('//div[@class=\"buttons\"]/form/input[@name=\"csrfmiddlewaretoken\"]/@value')[0]+"&referrer="
        url=r.post("http://www.solidfiles.com"+temp.xpath('//div[@class=\"buttons\"]/form/@action')[0],headers={"User-Agent":ua()},data=d).text
        newurl=findall('url=(.+)',fr(url).xpath("//meta[@http-equiv=\"refresh\"]/@content")[0])[0]
        data=r.head(newurl,headers={"User-Agent":ua(),"Connection":"keep-alive"})
        try:
            rawsize=int(data.headers['content-length'])
        except KeyError:
            rawsize=None
        name=r.utils.unquote(newurl.split('/')[-1])
        return [newurl,rawsize,name]

    def tusfiles(self) -> list:
        '''Return tusfiles'''
        temp=fr(r.get(self.url,headers={"User-Agent":ua()}).text).xpath("//form[@method=\"POST\"]/input/@value")
        d=f"op={temp[0]}&id={temp[1]}&rand={temp[2]}&referer=&method_free=&method_premium=1"
        newurl=r.post(self.url,headers={"User-Agent":ua()}, data=d, allow_redirects=False).headers["location"]
        data=r.head(newurl,headers={"User-Agent":ua(),"Connection":"Keep-Alive"})
        try:
            rawsize=int(data.headers['content-length'])
        except KeyError:
            rawsize=None
        name=newurl.split("/")[-1]
        return [newurl,rawsize,name]

    def anonbayfiles(self) -> list:
        '''Return anonbay and bayfiles'''
        newurl=fr(r.get(self.url, headers={"User-Agent":ua()}).text).xpath('//a[@id=\"download-url\"]/@href')[0]
        data=r.head(newurl,headers={"User-Agent":ua(),"Connection":"keep-alive"})
        try:
            rawsize=int(data.headers['content-length'])
        except KeyError:
            rawsize=None
        name=findall('filename="(.+)"',data.headers['Content-Disposition'])[0]
        return [newurl,rawsize,name]

    def racaty(self) -> list:
        '''Return racaty'''
        temp=fr(r.get(self.url,headers={"User-Agent":ua()}).text).xpath("//form[@id=\"getExtoken\"]/input/@value")
        d=f"op={temp[0]}&id={temp[1]}&rand={temp[2]}&referer=&method_free=&method_premium=1"
        _=r.post(self.url,headers={"User-Agent":ua()},data=d).text
        newurl=fr(_).xpath("//a[@id='uniqueExpirylink']/@href")[0]
        data=r.head(newurl,headers={"User-Agent":ua(),"Connection":"keep-alive"},verify=False)
        try:
            rawsize=int(data.headers['content-length'])
        except KeyError:
            rawsize=None
        name=newurl.split("/")[-1]
        return [newurl,rawsize,name]

    def zippyshare(self) -> list:
        '''Return zippyshare'''
        var=fr(r.get(self.url,headers={"User-Agent":ua()}).text).xpath("//a[@id=\"dlbutton\"]/following-sibling::script/text()")[0].splitlines()[1][:-1]
        var=var.replace("document.getElementById('dlbutton').href =","")
        _=findall(r"\((.+)\)",var)[0]
        var=var.replace(f"({_})",f"\"{eval(_)}\"")
        newurl="https://"+(self.url).split("/")[2]+eval(var)
        data=r.Session().head(newurl,headers={"User-Agent":ua()})
        try:
            rawsize=int(data.headers['content-length'])
        except KeyError:
            rawsize=None
        name=r.utils.unquote(findall("UTF-8\'\'(.+)",data.headers['Content-Disposition'])[0])
        return [newurl,rawsize,name]

    def hxfile(self):
        '''Return hxfile'''
        temp=fr(r.get(self.url,headers={"User-Agent":ua()}).text).xpath("//form[@name=\"F1\"]/input/@value")
        d=f"op={temp[0]}&id={temp[1]}&rand={temp[2]}&referer=&method_free&method_premium=1"
        var=r.post(self.url,headers={"User-Agent":ua(),"content-type":"application/x-www-form-urlencoded"},data=d).text
        newurl=fr(var).xpath("//a[@class=\"btn btn-dow\"]/@href")[0]
        data=r.head(newurl,headers={"User-Agent":ua(),"Connection":"keep-alive"})
        try:
            rawsize=int(data.headers['content-length'])
        except KeyError:
            rawsize=None
        name=newurl.split("/")[-1]
        return [newurl,rawsize,name]

class Prog:
    '''Utilities'''
    @staticmethod
    def getsize(file_size: int) -> str:
        '''Return file size with its unit'''
        if file_size < 1024:
            modified_size=f"{file_size} Bytes"
        elif 1024 <= file_size < 1048576:
            modified_size=f"{round(file_size / 1024, 2)} KB"
        elif 1048576 <= file_size < 1073741824:
            modified_size=f"{round(file_size / 1048576, 2)} MB"
        elif file_size >= 1073741824:
            modified_size=f"{round(file_size / 1073741824, 2)} GB"
        return modified_size

    @staticmethod
    def get_paused(temporary: str, quiet: bool=False) -> None:
        '''Get list of paused download(s)'''
        from glob import glob
        list_pausedfile: list=glob(f"{temporary}/*.log")
        if not quiet:
            print(f">>> {ye}[{cy}Info{ye}] {gr}List of Paused Download\n{wh}----------------------------------\n{re}[Id]   {cy}[Name]{de}")
        with open("paused.info","w",encoding="utf-8") as f:
            f.write("{")
            for i,n in enumerate(list_pausedfile):
                if not quiet:
                    print(f"{gr}[{i+1}] {os.path.basename(n).split('.log')[0]}{de}")
                if i == 0:
                    f.write(f"\"{str(i+1)}\":\"{os.path.basename(n).split('.log')[0]}\"")
                elif i != 0 and i+1 != len(list_pausedfile):
                    f.write(f",\"{str(i+1)}\":\"{os.path.basename(n).split('.log')[0]}\"")
            f.write("}")
            f.close()

    @staticmethod
    def get_user_setting() -> list:
        '''Get config.json'''
        result=[]
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                jsonvar=json.load(f)
                result=[jsonvar[i] for i in ["tmp_location","complete_location","chunk_size","thread_count","default_mode"]]
        except (json.decoder.JSONDecodeError, KeyError, FileNotFoundError):
            print(f"""{de}>>> {re}[Err] Config file didn't found or corrupted\n{de}>>> {gr}[{wh}+{gr}] Creating new config.json!{de}""")
            with open("config.json", "w", encoding="utf-8") as f:
                json.dump({"tmp_location":"tmp","complete_location":"complete","chunk_size":128,"thread_count":4,"default_mode":"multi"},f)
                f.close()
            result=["tmp","complete",128,4,"multi"]
        return result

def main() -> None:
    '''Main Function'''
    tmp_dir=Prog.get_user_setting()
    complete_dir=tmp_dir[1]

    #Argument Parser
    parser=argparse.ArgumentParser()
    subparser=parser.add_subparsers(dest="action",required=True)
    parser1=subparser.add_parser("download",help="Download a file from url")
    parser1.add_argument("-d","--grabdirectlink",help="Return direct download link",dest="direct",action="store_true")
    parser1.add_argument("-c","--chunk",type=int,metavar="int",help="Override chunk size in config",default=tmp_dir[2])
    parser1.add_argument("-m","--mode",metavar="mode",help="Select singlethreaded or multithreaded download",choices=["single","multi"],default=tmp_dir[4])
    parser1.add_argument("-t","--threads",metavar="int",type=int,help="Override threads count in config",choices=range(2,9),default=tmp_dir[3])
    parser1.add_argument("url")
    parser2=subparser.add_parser("resume",help="Resume paused download by selecting the id")
    parser2.add_argument("id", type=int, help="That file id you wanna resume")
    parser2.add_argument("-c","--chunk",type=int,metavar="int",help="Override chunk size in config", default=tmp_dir[2])
    subparser.add_parser("paused",help="Get list of paused download")
    args=parser.parse_args()

    #Check temporary and complete download folder
    tmp_dir=tmp_dir[0]
    if tmp_dir[-1:] == "/":
        tmp_dir=tmp_dir[:-1]
    if complete_dir[-1:] == "/":
        complete_dir=complete_dir[:-1]
    if not os.path.isdir(tmp_dir):
        os.mkdir(tmp_dir)
    if not os.path.isdir(complete_dir):
        os.mkdir(complete_dir)

    if args.action == "download":
        start(args.mode, args.url)
        if args.mode == "single":
            args.threads=1
        DL(args.chunk, args.mode, args.threads, args.url, tmp_dir, complete_dir, direct=args.direct).run()
    elif args.action == "resume":
        if os.path.exists("paused.info"):
            Prog.get_paused(tmp_dir, quiet=True)
        with open("paused.info", encoding="utf-8") as f:
            try:
                with open(f"{tmp_dir}/{json.load(f)[str(args.id)]}.log", encoding="utf-8") as selected_f:
                    load_yaml=yaml.safe_load(selected_f.read())
                url=load_yaml["Source"]
                rawsize=load_yaml["Size"]
                file_name=load_yaml["Name"]
                downloaded=load_yaml["Downloaded"]
                mode=load_yaml["Mode"]
                download_pos=load_yaml["Download-Pos"]
                resume_args={"name":file_name,"downloaded":downloaded,"rawsize":rawsize,"download_pos":download_pos}
                if mode == 'multi':
                    threads=load_yaml["Threads"]
                    threads_result=load_yaml["Threads-Result"]
                    resume_args["threads_result"]=threads_result
                elif mode == 'single':
                    threads=1
            except (KeyError, yaml.scanner.ScannerError):
                print(f"{re} An error occured. Try get a new list of paused download!{de}")
                sys.exit(1)
            except FileNotFoundError:
                print(f"{re}[Err] File with download {args.id} doesn't exist{de}")
                sys.exit(1)
            f.close()
        start(mode, url)
        DL(args.chunk, mode, threads, url, tmp_dir, complete_dir, resume=resume_args).run()
    elif args.action == "paused":
        Prog.get_paused(tmp_dir)

if __name__ == "__main__":
    #Program Color Code
    if ps() == 'Windows':
        try:
            from colorama import init, Fore
            init()
            wh=Fore.LIGHTWHITE_EX
            re=Fore.LIGHTRED_EX
            gr=Fore.LIGHTGREEN_EX
            ye=Fore.LIGHTYELLOW_EX
            ma=Fore.LIGHTMAGENTA_EX
            cy=Fore.LIGHTCYAN_EX
            de=Fore.RESET
            del init,Fore
            clear="cls"
        except ModuleNotFoundError:
            print("Install colorama with \'pip install colorama\'")
            sys.exit()
    else:
        wh="\033[1;37m"
        re="\033[1;31m"
        gr="\033[1;32m"
        ye="\033[1;33m"
        ma="\033[1;35m"
        cy="\033[1;36m"
        de="\033[0m"
        clear="clear"
    del ps

    main()

