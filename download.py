#IMPORT MODULE
import random as ra,sys,platform,re as ru,time,os,json,shutil
try:
    from bs4 import BeautifulSoup as Bs
    import requests as r,lxml.html as lh
except ModuleNotFoundError:
    print("Install required package with 'pip install -r requirements.txt'")
    sys.exit(1)
try:
    import google.colab
    COLAB = True
except:
    COLAB = False
if sys.version_info[0] == 3: pass
else:
    print("Run with python3!")
    sys.exit(1)

#SETTING
setting=json.load(open("config.json","r"))
tmp=setting["tmp_location"]
complete=setting['complete_location']
if tmp[-1:] == "/":
    tmp=tmp[:-1]
if complete[-1:] == "/":
    complete=complete[:-1]

#COLOR CODE
if platform.system() == 'Windows':
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
        return ra.choice(["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 Edg/90.0.818.51",'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36','Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36','Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36','Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'])

#CONNECTION TEST
def test():
    print(f"{cy}[T] Testing your connection")
    start=time.time()
    r.get("http://sg-speedtest.fast.net.id.prod.hosts.ooklaserver.net:8080",headers={"Accept-Encoding":"gzip, compress, br"})
    ping=int((round(time.time() - start, 3))*1000)
    if ping < 500:
        print(f"{gr}[G] Your connection is good | Ping : {ping}ms , pinged from Singapore Firstmedia speedtest server")
    elif 500 <= ping < 1000:
        print(f"{ye}[N] Your connection is normal | Ping : {ping}ms , pinged from Singapore Firstmedia speedtest server")
    else:
        print(f"{re}[B] Your connection is bad | Ping : {ping}ms , pinged from Singapore Firstmedia speedtest server")

#BANNER
def banner():
    print(f"""{de} ______ _ _         _____  _      
|  ____(_) |       |  __ \| |     
| |__   _| | ___   | |  | | |     
|  __| | | |/ _ \  | |  | | |     
| |    | | |  __/  | |__| | |____ 
|_|    |_|_|\___   |_____/|______|
Author : https://github.com/XniceCraft
""")

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
    def __init__(self, url, direct, resume):
        self.url=url
        self.direct=direct
        self.resume=resume

    def getsize(self, a):
        if a < 1024:
            return str(a) + " Bytes"
        elif 1024 <= a < 1048576:
            return str(round(a / 1024, 2)) + " KB"
        elif 1048576 <= a < 1073741824:
            return str(round(a / 1048576, 2)) + " MB"
        elif 1073741824 <= a :
            return str(round(a / 1073741824, 2)) + " GB"

    def paused(self, provider, downloaded):
        self.downloaded=downloaded
        print(f"{gr}\r\n> Download paused. Resume or Exit (r/e)?")
        ask=input("> ")
        if ask.lower() == "r" or ask.lower() == "resume" or ask.lower() == "y":
            self.direct=False
            self.resume=True
            if provider == "mediafire":
                os.system(clear)
                banner()
                self.mediafire()
            elif provider == "solidfiles":
                os.system(clear)
                banner()
                self.solidfiles()
            elif provider == "tusfiles":
                os.system(clear)
                banner()
                self.tusfiles()
            elif provider == "anonfiles":
                os.system(clear)
                banner()
                self.anonfiles()
        else:
            os.remove(f"{tmp}/{self.name}")
            print(f"{re}> {ma}File {cy}{self.name} {ma}removed")
            sys.exit()

    def finish(self):
        shutil.move(rf'{tmp}/{self.name}',rf"{complete}/{self.name}")

    def start(self,s,p):
        print(f"""{de}> [INFO] Filename : {self.name}
         Size : {self.size}""")
        if s=="D":
            with open(f"{tmp}/{self.name}", "wb") as f:
                print(f"{ye}> [Starting] Downloading")
                tl=self.tmpsize
                dl=0
                now=time.time()
                try:
                    for l in (self.data).iter_content(chunk_size=int(tl/100)):
                        speed=time.time() - now
                        dl += len(l)
                        done=int(100 * dl / tl)
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
            with open(f"{tmp}/{self.name}", "ab") as f:
                print(f"{ye}> [Resume] Resuming...")
                tl=int((self.data).headers['content-length'])
                dl=0
                now=time.time()
                try:
                    for l in (self.data).iter_content(chunk_size=int(tl/100)):
                        speed=time.time() - now
                        dl += len(l)
                        try:
                            sys.stdout.write(cy+"\r"+"> [Downloading] Progress : "+str(int(100 * (dl+self.downloaded) / self.tmpsize))+"% | Speed: "+str(int(dl / speed / 1000)) + " Kbps") 
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
            u=lh.fromstring(r.get(self.url,headers={"User-Agent":ua.get()}).text).xpath('//*[@id="downloadButton"]/@href')[0]
        except IndexError:
            print(f'{re}> [X] File not found')
            sys.exit()
        if self.direct:
            print(f"Link : {cy}{u}")
        else:
            if self.resume:
                self.data=r.get(u,headers={"User-Agent":ua.get(),"Range":f"bytes={str(self.downloaded)}-","Connection":"keep-alive"},stream=True)
                self.start('R',"mediafire")
            else:
                self.data=r.get(u,headers={"User-Agent":ua.get(),"Connection":"keep-alive"},stream=True)
                self.tmpsize=int((self.data).headers['content-length'])
                self.size=self.getsize(self.tmpsize)
                self.name=ru.findall('filename="(.+)"',(self.data).headers['Content-Disposition'])[0]
                self.start("D","mediafire")

    def solidfiles(self):
        html=r.get(self.url,headers={"User-Agent":ua.get()}).text
        try:
            d="csrfmiddlewaretoken="+lh.fromstring(html).xpath('//*[@id="content"]/div/div[2]/div[2]/article[1]/section[2]/div[1]/form/input[1]/@value')[0]+"&referrer="
            u="http://www.solidfiles.com"+Bs(html,'html.parser').find("div",{'class':"buttons"}).select("form")[0].get("action")
        except IndexError:
            print(f'{re}> [X] File not found')
            sys.exit()
        u=lh.fromstring(r.post(u,headers={"User-Agent":ua.get()},data=d).text).xpath('//*[@id="content"]/div/div[2]/div[2]/article[1]/section/p/a/@href')[0]
        if self.direct == True:
            print(f"Link : {cy}{u}")
        else:
            if self.resume == True:
                self.data=r.get(u,headers={"User-Agent":ua.get(),"Range":f"bytes={str(self.downloaded)}-","Connection":"keep-alive"},stream=True)
                self.start('R',"solidfiles")
            else:
                self.data=r.get(u,headers={"User-Agent":ua.get(),"Connection":"keep-alive"},stream=True)
                self.tmpsize=int((self.data).headers['content-length'])
                self.size=self.getsize(self.tmpsize)
                self.name=r.utils.unquote(u.split('/')[-1])
                self.start("D","solidfiles")

    def tusfiles(self):
        html=r.get(self.url,headers={"User-Agent":ua.get()}).text
        try:
            tmp=Bs(str(Bs(html,"html.parser").find("form")),"html.parser").find_all("input")
            v1=f"op={lh.fromstring(tmp[0].encode()).xpath('//input/@value')[0]}&id={lh.fromstring(tmp[1].encode()).xpath('//input/@value')[0]}&rand={lh.fromstring(tmp[2].encode()).xpath('//input/@value')[0]}&referer={lh.fromstring(tmp[3].encode()).xpath('//input/@value')[0]}&method_free=&method_premium=1"
        except IndexError:
            print(f'{re}> [X] File not found')
            sys.exit()
        html1=r.post(self.url,headers={"User-Agent":ua.get()},data=v1,allow_redirects=False)
        if self.direct == True:
            print(f"Link : {cy}{html1.headers['location']}")
        else:
            if self.resume == True:
                self.data=r.get(html1.headers['location'],headers={"User-Agent":ua.get(),"Range":f"bytes={str(self.downloaded)}-","Connection":"keep-alive"},stream=True)
                self.start("R",'tusfiles')
            else:
                self.data=r.get(html1.headers['location'],headers={"User-Agent":ua.get(),"Connection":"keep-alive"},stream=True)
                self.name=html1.headers['location'].split("/")[-1]
                self.tmpsize=int((self.data).headers['content-length'])
                self.size=self.getsize(self.tmpsize)
                self.start("D","tusfiles")

    def anonfiles(self):
        html=r.get(self.url,headers={"User-Agent":ua.get()}).text
        try:
            u=lh.fromstring(html).xpath('//*[@id="download-url"]/@href')[0]
        except IndexError:
            print(f'{re}> [X] File not found')
            sys.exit()
        if self.direct == True:
            print(f"Link : {cy}{u}")
        else:
            if self.resume == True:
                self.data=r.get(u,headers={"User-Agent":ua.get(),"Connection":"keep-alive","Range":f"bytes={str(self.downloaded)}-"}, stream=True)
                self.start("R","anonfiles")
            else:
                self.data=r.get(u,headers={"User-Agent":ra.choice(ua),"Connection":"keep-alive"}, stream=True)
                self.name=ru.findall('filename="(.+)"',data.headers['Content-Disposition'])[0]
                self.tmpsize=int((self.data).headers['content-length'])
                self.size=self.getsize(self.tmpsize)
                self.start("D","anonfiles")

#MAIN
def main():
    arg=len(sys.argv)
    if arg > 3 and sys.argv[1] == "-p":
        if arg > 4 and sys.argv[4] == "-grabdirectlink":
            direct=True
        else:
            direct=False
        if sys.argv[2] == "mediafire":
            start()
            dl(sys.argv[3], direct, False).mediafire()
        elif sys.argv[2] == "solidfiles":
            start()
            dl(sys.argv[3], direct, False).solidfiles()
        elif sys.argv[2] == "tusfiles":
            start()
            dl(sys.argv[3], direct, False).tusfiles()
        elif sys.argv[2] == "anonfiles":
            start()
            anonfiles(sys.argv[3], direct, False)
        elif sys.argv[2] == "zippyshare":
            start()
            zippyshare(sys.argv[3], direct, False)
        else:
            print(f"{de}File Hosting Not Found")
    else:
        print(f'''{de}Usage : python {sys.argv[0]} [option] [url] [optional option]
  -h    Show help
  -p    mediafire, solidfiles, tusfiles, anonfiles
  Optional options:
    -grabdirectlink  Get direct download link only''')

if __name__ == '__main__':
    main()
