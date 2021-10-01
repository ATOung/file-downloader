"""
File Downloader from python
Don't steal any code from this script
"""

#IMPORT MODULE
from random import choice
from platform import system as ps
import sys,re as ru,time,os,json,shutil
try:
    from lxml.html import fromstring as fr
    import requests as r
except ModuleNotFoundError:
    print("Install required package with 'pip install -r requirements.txt'")
    sys.exit(1)
if sys.version_info[0] == 3: pass
else:
    print("Run with python3!")
    sys.exit(1)

#SETTING
setting=json.load(open("config.json","r"))
tmp=setting["tmp_location"]
complete=setting['complete_location']
chunk=setting["chunk_size"]
if type(chunk) != int: raise ValueError("Chunk Size must be an integer")
if tmp[-1:] == "/": tmp=tmp[:-1]
if complete[-1:] == "/": complete=complete[:-1]
if not os.path.isdir(tmp): os.mkdir(tmp)
if not os.path.isdir(complete): os.mkdir(complete)

#COLOR CODE
if ps() == 'Windows':
    try:
        from colorama import init, Fore, Style
        init()
        re=Fore.RED + Style.BRIGHT
        gr=Fore.GREEN + Style.BRIGHT
        ye=Fore.YELLOW + Style.BRIGHT
        cy=Fore.CYAN + Style.BRIGHT
        ma=Fore.MAGENTA + Style.BRIGHT
        de=Fore.RESET + Style.BRIGHT
        clear="cls"
    except ModuleNotFoundError:
        print("Install colorama with 'pip install colorama'")
        sys.exit()
else:
    re="\033[1;31m"
    gr="\033[1;32m"
    ye="\033[1;33m"
    ma="\033[1;35m"
    cy="\033[1;36m"
    de="\033[1;0m"
    clear="clear"

#USER AGENT
class ua:
    def get():
        return choice(["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 Edg/90.0.818.51",'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36','Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36','Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36','Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'])

#CONNECTION TEST
def test():
    print(f"{cy}[T] Testing your connection")
    start=time.time()
    r.get("http://sg-speedtest.fast.net.id.prod.hosts.ooklaserver.net:8080")
    ping=int((round(time.time() - start, 3))*1000)
    if ping < 500: print(f"{gr}[G] Your connection is good | Ping : {ping}ms , pinged from Singapore Firstmedia speedtest server")
    elif 500 <= ping < 1000: print(f"{ye}[N] Your connection is normal | Ping : {ping}ms , pinged from Singapore Firstmedia speedtest server")
    else: print(f"{re}[B] Your connection is bad | Ping : {ping}ms , pinged from Singapore Firstmedia speedtest server")

#BANNER
def banner():
    print(rf"""{de} ______ _ _         _____  _      
|  ____(_) |       |  __ \| |     
| |__   _| | ___   | |  | | |     
|  __| | | |/ _ \  | |  | | |     
| |    | | |  __/  | |__| | |____ 
|_|    |_|_|\___   |_____/|______|
Author : https://github.com/XniceCraft
""")

#GETFILESIZE
def getsize(a):
    if a < 1024:
        return str(a) + " Bytes"
    elif 1024 <= a < 1048576:
        return str(round(a / 1024, 2)) + " KB"
    elif 1048576 <= a < 1073741824:
        return str(round(a / 1048576, 2)) + " MB"
    elif 1073741824 <= a :
        return str(round(a / 1073741824, 2)) + " GB"

#START
def start():
    os.system(clear)
    banner()
    test()
    time.sleep(2)
    os.system(clear)
    banner()

#MEDIAFIRE
class dl:
    def __init__(self, url, direct):
        self.url=url
        self.direct=direct
        self.resume=False
        self.downloaded=0
        self.tmpsize=0
        self.u=""
        self.name=""

    def paused(self, provider, downloaded):
        self.downloaded=downloaded
        print(f"{gr}\r\n> Download paused. Resume or Exit (r/e)?")
        ask=input("> ")
        if ask.lower() == "r" or ask.lower() == "resume" or ask.lower() == "y":
            self.direct=False
            self.resume=True
            os.system(clear)
            banner()
            if provider == "mediafire":
                self.mediafire()
            elif provider == "solidfiles":
                self.solidfiles()
            elif provider == "tusfiles":
                self.tusfiles()
            elif provider == "anonfiles":
                self.anonfiles()
            elif provider == "bayfiles":
                self.bayfiles()
            elif provider == "racaty":
                self.racaty()
            elif provider == "zippyshare":
                self.zippyshare()
        else:
            os.remove(f"{tmp}/{self.name}")
            print(f"{re}> {ma}File {cy}{self.name} {ma}removed")

    def finish(self):
        shutil.move(rf'{tmp}/{self.name}',rf"{complete}/{self.name}")

    def start(self,s,p):
        size=getsize(self.tmpsize)
        print(f"""{de}> [INFO] Filename : {self.name}
         Size : {size}""")
        if s=="D":
            data=r.Session().get(self.u,headers={"User-Agent":ua.get()},stream=True)
            with open(f"{tmp}/{self.name}", "wb") as f:
                print(f"{ye}> [Starting] Downloading")
                tl=self.tmpsize
                dl=0
                now=time.time()
                try:
                    for l in data.iter_content(chunk_size=chunk*1024):
                        speed=time.time() - now
                        dl += len(l)
                        done=round(100 * dl / tl,2)
                        try:
                            sys.stdout.write(cy+"\r"+"> [Downloading] Progress : "+str(done)+"% | Speed: "+str(int(dl / speed / 1000)) + " Kbps")
                        except:
                            pass
                        f.write(l)
                        sys.stdout.flush()
                    f.close()
                    self.finish()
                    print(f"\r\n{gr}> [Finished] Success download {self.name}")
                except KeyboardInterrupt:
                    f.close()
                    self.paused(p,os.path.getsize(f"{tmp}/{self.name}"))
        elif s=="R":
            data=r.Session().get(self.u,headers={"User-Agent":ua.get(),"Range":f"bytes={str(self.downloaded)}-"},stream=True)
            with open(f"{tmp}/{self.name}", "ab") as f:
                print(f"{ye}> [Resume] Resuming...")
                tl=int(data.headers['content-length'])
                dl=0
                now=time.time()
                try:
                    for l in data.iter_content(chunk_size=chunk*1024):
                        speed=time.time() - now
                        dl += len(l)
                        try:
                            sys.stdout.write(cy+"\r"+"> [Downloading] Progress : "+str(round(100 * (dl+self.downloaded) / self.tmpsize,2))+"% | Speed: "+str(int(dl / speed / 1000)) + " Kbps")
                        except:
                            pass
                        f.write(l)
                        sys.stdout.flush()
                    f.close()
                    self.finish()
                    print(f"\r\n{gr}> [Finished] Success download {self.name}")
                except KeyboardInterrupt:
                    f.close()
                    self.paused(p,os.path.getsize(f"{tmp}/{self.name}"))

    def mediafire(self):
        try:
            self.u=fr(r.get(self.url,headers={"User-Agent":ua.get()}).text).xpath('//a[@id="downloadButton"]/@href')[0]
        except IndexError:
            print(f"{re}[X] File not found")
            return
        if self.direct:
            print(f"Link : {cy}{self.u}")
            return
        else:
            if self.resume:
                self.start('R',"mediafire")
            else:
                data=r.head(self.u,headers={"User-Agent":ua.get(),"Connection":"keep-alive"})
                self.tmpsize=int(data.headers['content-length'])
                self.name=ru.findall('filename="(.+)"',data.headers['Content-Disposition'])[0]
                self.start("D","mediafire")

    def solidfiles(self):
        html=r.get(self.url,headers={"User-Agent":ua.get()}).text
        try:
            tmplh=fr(html)
            d="csrfmiddlewaretoken="+tmplh.xpath('//div[@class=\"buttons\"]/form/input[@name=\"csrfmiddlewaretoken\"]/@value')[0]+"&referrer="
            self.u=r.post("http://www.solidfiles.com"+tmplh.xpath('//div[@class=\"buttons\"]/form/@action')[0],headers={"User-Agent":ua.get()},data=d).text
            self.u=ru.findall('url=(.+)',fr(self.u).xpath("//meta[@http-equiv=\"refresh\"]/@content")[0])[0]
        except IndexError:
            print(f"{re}[X] File not found")
            return
        if self.direct:
            print(f"Link : {cy}{self.u}")
            return
        else:
            if self.resume:
                self.start('R',"solidfiles")
            else:
                data=r.head(self.u,headers={"User-Agent":ua.get(),"Connection":"keep-alive"})
                self.tmpsize=int(data.headers['content-length'])
                self.name=r.utils.unquote((self.u).split('/')[-1])
                self.start("D","solidfiles")

    def tusfiles(self):
        html=r.get(self.url,headers={"User-Agent":ua.get()}).text
        try:
            tmplh=fr(html).xpath("//form[@method=\"POST\"]/input/@value")
            d=f"op={tmplh[0]}&id={tmplh[1]}&rand={tmplh[2]}&referer=&method_free=&method_premium=1"
            self.u=r.post(self.url,headers={"User-Agent":ua.get()},data=d,allow_redirects=False).headers["location"]
        except IndexError:
            print(f"{re}[X] File not found")
            return
        if self.direct:
            print(f"Link : {cy}{self.u}")
            return
        else:
            if self.resume:
                self.start("R",'tusfiles')
            else:
                data=r.head(self.u,headers={"User-Agent":ua.get(),"Connection":"Keep-Alive"})
                self.name=(self.u).split("/")[-1]
                self.tmpsize=int(data.headers['content-length'])
                self.start("D","tusfiles")

    def anonfiles(self):
        html=r.get(self.url,headers={"User-Agent":ua.get()}).text
        try:
            self.u=fr(html).xpath('//a[@id=\"download-url\"]/@href')[0]
        except IndexError:
            print(f"{re}[X] File not found")
            return
        if self.direct:
            print(f"Link : {cy}{self.u}")
            return
        else:
            if self.resume:
                self.start("R","anonfiles")
            else:
                data=r.head(self.u,headers={"User-Agent":ua.get(),"Connection":"keep-alive"})
                self.name=ru.findall('filename="(.+)"',data.headers['Content-Disposition'])[0]
                self.tmpsize=int(data.headers['content-length'])
                self.start("D","anonfiles")

    def bayfiles(self):
        try:
            self.u=fr(r.get(self.url,headers={"User-Agent":ua.get()}).text).xpath('//a[@id="download-url"]/@href')[0]
        except IndexError:
            print(f"{re}[X] File not found")
            return
        if self.direct:
            print(f"Link : {cy}{self.u}")
            return
        else:
            if self.resume:
                self.start("R","bayfiles")
            else:
                data=r.head(self.u,headers={"User-Agent":ua.get(),"Connection":"keep-alive"})
                self.name=ru.findall('filename="(.+)"',data.headers['Content-Disposition'])[0]
                self.tmpsize=int(data.headers['content-length'])
                self.start("D","bayfiles")

    def racaty(self):
        html=r.get(self.url,headers={"User-Agent":ua.get()}).text
        try:
            tmplh=fr(html).xpath("//form[@id=\"getExtoken\"]/input/@value")
            d=f"op={tmplh[0]}&id={tmplh[1]}&rand={tmplh[2]}&referer=&method_free&method_premium=1"
            self.u=r.post(self.url,headers={"User-Agent":ua.get()},data=d).text
            self.u=fr(self.u).xpath("//div[@class=\'retryDl small mt-2\']/a/@href")[0]
        except IndexError:
            print(f"{re}[X] File not found")
            return
        if self.direct:
            print(f"Link : {cy}{self.u}")
            return
        else:
            if self.resume:
                self.start("R","racaty")
            else:
                data=r.head(self.u,headers={"User-Agent":ua.get(),"Connection":"keep-alive"})
                self.name=(self.u).split("/")[-1]
                self.tmpsize=int(data.headers['content-length'])
                self.start("D","racaty")

    def zippyshare(self):
        html=r.get(self.url,headers={"User-Agent":ua.get()}).text
        try:
            self.u=fr(html).xpath("//a[@id=\"dlbutton\"]/following-sibling::script/text()")[0].splitlines()[1]
            self.u=ru.findall("= (.+);",self.u)[0]
            tmpvar="'"+str(eval(ru.findall("\+ (.+) \+",self.u)[0]))+"'"
            self.u="https://"+(self.url).split("/")[2]+eval(ru.sub("(\(.+\))",tmpvar,self.u))
        except IndexError:
            print(f"{re}[X] File not found")
            return
        if self.direct:
            print(f"Link : {cy}{self.u}")
            return
        else:
            if self.resume:
                self.start("R","zippyshare")
            else:
                data=r.Session().head(self.u,headers={"User-Agent":ua.get()})
                self.name=r.utils.unquote(ru.findall("UTF-8\'\'(.+)",data.headers['Content-Disposition'])[0])
                self.tmpsize=int(data.headers['content-length'])
                self.start("D","zippyshare")

def main():
    """Main Function"""
    arg=len(sys.argv)
    if arg > 3 and sys.argv[1] == "-p":
        direct=bool(arg > 4 and sys.argv[4] == "-grabdirectlink")
        start()
        if sys.argv[2] == "mediafire":
            dl(sys.argv[3], direct).mediafire()
        elif sys.argv[2] == "solidfiles":
            dl(sys.argv[3], direct).solidfiles()
        elif sys.argv[2] == "tusfiles":
            dl(sys.argv[3], direct).tusfiles()
        elif sys.argv[2] == "anonfiles":
            dl(sys.argv[3], direct).anonfiles()
        elif sys.argv[2] == "bayfiles":
            dl(sys.argv[3], direct).bayfiles()
        elif sys.argv[2] == "racaty":
            dl(sys.argv[3], direct).racaty()
        elif sys.argv[2] == "zippyshare":
            dl(sys.argv[3], direct).zippyshare()
        else:
            print(f"{de}File Hosting Not Found")
    else:
        print(f'''{de}Usage : python {sys.argv[0]} [option] [url] [optional option]
  -h    Show help
  -p    mediafire, solidfiles, tusfiles, anonfiles, bayfiles, racaty, zippyshare
  Optional options:
    -grabdirectlink  Get direct download link only''')

if __name__ == '__main__':
    main()
