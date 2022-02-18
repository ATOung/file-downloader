"""
File Downloader from python
Don't steal any code from this script
"""

#pylint: disable=invalid-name,multiple-statements,missing-function-docstring,missing-class-docstring,line-too-long,eval-used,multiple-imports
ua=lambda: choice(["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36","Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36","Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36","Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.62"])

#Connection Test
def test():
    print(f"{cy}[T] Testing your connection")
    try:
        s=time.time()
        r.get("http://sg-speedtest.fast.net.id.prod.hosts.ooklaserver.net:8080", timeout=3)
        ping=int((round(time.time() - s, 3))*1000)
        if ping < 500: print(f"{gr}[G] Your connection is good | Ping : {ping}ms , pinged from Singapore Firstmedia speedtest server")
        elif 500 <= ping < 1000: print(f"{ye}[N] Your connection is normal | Ping : {ping}ms , pinged from Singapore Firstmedia speedtest server")
        else: print(f"{re}[B] Your connection is bad | Ping : {ping}ms , pinged from Singapore Firstmedia speedtest server")
    except ConnectTimeout:
        print(f"{re}[Err] Connection Timeout. Ping exceeds 3000ms{de}")
        sys.exit()
    except r.exceptions.ConnectionError as e:
        print(f"{re}[Err] Connection Error!{de}")
        sys.exit()

#Banner
def banner():
    print(rf"""{de} ______ _ _         _____  _
|  ____(_) |       |  __ \| |
| |__   _| | ___   | |  | | |
|  __| | | |/ _ \  | |  | | |
| |    | | |  __/  | |__| | |____
|_|    |_|_|\___   |_____/|______|
Author : https://github.com/XniceCraft
Mode : {args.mode}
""")

#Return File Size
def getsize(a):
    if a < 1024:
        v=str(a) + " Bytes"
    elif 1024 <= a < 1048576:
        v=str(round(a / 1024, 2)) + " KB"
    elif 1048576 <= a < 1073741824:
        v=str(round(a / 1048576, 2)) + " MB"
    elif a >= 1073741824:
        v=str(round(a / 1073741824, 2)) + " GB"
    return v

#Start
def start():
    if "https://" in args.url or "http://" in args.url:
        os.system(clear)
        banner()
        test()
        time.sleep(2)
        os.system(clear)
        banner()
    else:
        print(f"{re}[Err] Invalid URL scheme. There is no http/https in URL{de}")
        sys.exit()

#Download Function
def download(name, num, url, pos, resume=False):
    data=r.Session().get(url,headers={"User-Agent":ua(),"Range":f"bytes={pos['start']}-{pos['end']}"},stream=True, timeout=5)
    if resume: m="ab"
    else: m="wb"    
    with open(f"{tmp}/{name}-{num}",m) as f:
        try:
            for l in data.iter_content(chunk_size=args.chunk*1024):
                f.write(l)
                dl.dlded += len(l)
            f.close()
            return True
        except (r.exceptions.ConnectionError, ChunkedEncodingError):
            f.close()
            dl.pos[num]["start"]=dl.pos[num]["start"]+os.path.getsize(f"{tmp}/{name}-{num}")
            return False

#Possible Threads to Download
def multitest(url):
    def runtest(url):
        return bool(r.Session().get(url,headers={"User-Agent":ua()},stream=True).status_code in [200,201,202,206])
    value=[]
    with concurrent.futures.ThreadPoolExecutor() as executor:
        result=[executor.submit(runtest,url) for _ in range(args.threads)]
        for future in concurrent.futures.as_completed(result):
            value.append(future.result())
    return value.count(True)

#Download Handler
class dl:
    dlded=0
    pos={}
    def __init__(self, url):
        self.url=url
        self.resume=False
        self.tmpsize=0
        self.u=""
        self.name=""
        self.provider=""

    def ai(self):
        for i in range(args.threads):
            if i == 0: dl.pos[1]={"start":0, "end":floor(self.tmpsize/args.threads)}
            elif i+1 == args.threads: dl.pos[i+1]={"start":floor(self.tmpsize/args.threads)*i+1, "end":self.tmpsize}
            else: dl.pos[i+1]={"start":floor(self.tmpsize/args.threads)*i+1, "end":floor(self.tmpsize/args.threads)*(i+1)}

    def finish(self):
        if args.mode == "multi":
            with open(f"{tmp}/{self.name}","ab") as f:
                for i in range(args.threads):
                    with open(f"{tmp}/{self.name}-{i+1}","rb") as h:
                        f.write(h.read())
                    h.close()
                    os.remove(f"{tmp}/{self.name}-{i+1}")
            f.close()
        move(rf'{tmp}/{self.name}',rf"{complete}/{self.name}")
        print(f"{gr}\n> [Finished] Success download {self.name}{de}")

    #Pause function for singlethreaded
    def paused(self, provider):
        dl.dlded=os.path.getsize(f"{tmp}/{self.name}")
        self.resume=True
        print(f"{gr}\r\n> Download paused. Resume or Exit (r/e)?")
        ask=input("> ")
        if ask.lower() == "r" or ask.lower() == "resume" or ask.lower() == "y":
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
            elif provider == "hxfile":
                self.hxfile()
        else:
            os.remove(f"{tmp}/{self.name}")
            print(f"{re}> {gr}File {cy}{self.name} {gr}was successfully removed")

    def start(self):
        size=getsize(self.tmpsize)
        print(f"""{de}> [INFO] Filename : {self.name}
         Size : {size}""")
        if args.mode == "single":
            if not self.resume:
                data=r.Session().get(self.u,headers={"User-Agent":ua()},stream=True)
                print(f"{ye}> [Starting] Downloading")
                with open(f"{tmp}/{self.name}", "wb") as f:
                    try:
                        now=time.time()
                        for l in data.iter_content(chunk_size=args.chunk*1024):
                            dl.dlded += len(l)
                            f.write(l)
                            try:
                                speed=str(int(dl.dlded / (time.time() - (now)) / 1000))
                            except ZeroDivisionError:
                                speed="0"
                            done=round(100 * dl.dlded / self.tmpsize,2)
                            sys.stdout.write(cy+"\r"+"> [Downloading] Progress : "+str(done)+"% | Speed: "+speed+ " KB/s")
                            sys.stdout.flush()
                        f.close()
                        self.finish()
                    except (KeyboardInterrupt, ChunkedEncodingError) as e:
                        f.close()
                        if isinstance(e, ChunkedEncodingError): print(f"{re}\n[!] Connection Error",end="")
                        self.paused(self.provider)

            else:
                data=r.Session().get(self.u,headers={"User-Agent":ua(),"Range":f"bytes={str(dl.dlded)}-"},stream=True)
                print(f"{ye}> [Resume] Resuming...")
                with open(f"{tmp}/{self.name}", "ab") as f:
                    try:
                        now=time.time()
                        for l in data.iter_content(chunk_size=args.chunk*1024):
                            dl.dlded += len(l)
                            f.write(l)
                            try:
                                speed=str(int(dl.dlded / (time.time() - (now)) / 1000))
                            except ZeroDivisionError:
                                speed="0"
                            done=round(100 * dl.dlded / self.tmpsize,2)
                            sys.stdout.write(cy+"\r"+"> [Downloading] Progress : "+str(done)+"% | Speed: "+speed+ " KB/s")
                            sys.stdout.flush()
                        f.close()
                        self.finish()
                    except (KeyboardInterrupt, ChunkedEncodingError) as e:
                        f.close()
                        if isinstance(e, ChunkedEncodingError): print(f"{re}\n[!] Connection Error",end="")
                        self.paused(self.provider)

        elif args.mode == "multi":
            print(f"{ye}> [Starting] Downloading")
            args.threads=multitest(self.u)
            self.ai()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                run=[executor.submit(download,self.name,_+1,self.u,dl.pos[_+1]) for _ in range(args.threads)]
                now=time.time()
                while False in [i.done() for i in run]:
                    try:
                        time.sleep(1)
                        try:
                            speed=str(int(dl.dlded / (time.time() - (now+1)) / 1000))
                        except ZeroDivisionError:
                            speed="0"
                        done=round(100 * dl.dlded / self.tmpsize,2)
                        sys.stdout.write(cy+"\r"+"> [Downloading] Progress : "+str(done)+"% | Speed: "+speed+ " KB/s")
                        sys.stdout.flush()
                    except KeyboardInterrupt: pass
            while True:
                res=[i.result() for i in concurrent.futures.as_completed(run)]
                if all(res):
                    print(f"\r\n{de}> Assembling file into one solid file. Please wait!",end="")
                    self.finish()
                    break
                else:
                    print(f"{gr}\r\n> {res.count(False)} thread(s) (is/are) failed.Try again or Exit (t/e)?")
                    ask=input("> ")
                    if ask.lower() == "t" or ask.lower() == "y":
                        self.resume=True
                        os.system(clear)
                        banner()
                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            failedthread=[i+1 for i in range(len(res)) if res[i] == False]
                            run=[executor.submit(download,self.name,_,self.u,dl.pos[_],True) for _ in failedthread]
                            now=time.time()
                            while False in [i.done() for i in run]:
                                try:
                                    time.sleep(1)
                                    try:
                                        speed=str(int(dl.dlded / (time.time() - (now+1)) / 1000))
                                    except ZeroDivisionError:
                                        speed="0"
                                    done=round(100 * dl.dlded / self.tmpsize,2)
                                    sys.stdout.write(cy+"\r"+"> [Downloading] Progress : "+str(done)+"% | Speed: "+speed+ " KB/s")
                                    sys.stdout.flush()
                                except KeyboardInterrupt: pass
                    else:
                        for i in range(args.threads):
                            os.remove(f"{tmp}/{self.name}-{i+1}")
                        print(f"{re}> {gr}File {cy}{self.name} {gr}was successfully removed")
                        break

    #Get Direct Link
    def mediafire(self):
        try:
            self.u=utils.mediafire.get_direct_link(r.get(self.url,headers={"User-Agent":ua()}).text)
        except DirectLinkError:
            print(f"{re}[X] File not found")
            return
        if args.direct:
            print(f"Link : {cy}{self.u}")
            return
        if not self.resume:
            data=r.head(self.u,headers={"User-Agent":ua(),"Connection":"keep-alive"})
            self.tmpsize=int(data.headers['content-length'])
            self.name=findall('filename="(.+)"',data.headers['Content-Disposition'])[0]
            self.provider="mediafire"
        self.start()

    def solidfiles(self):
        try:
            self.u=utils.solidfiles.get_direct_link(r.get(self.url,headers={"User-Agent":ua()}).text)
        except DirectLinkError:
            print(f"{re}[X] File not found")
            return
        if args.direct:
            print(f"Link : {cy}{self.u}")
            return
        if not self.resume:
            data=r.head(self.u,headers={"User-Agent":ua(),"Connection":"keep-alive"})
            self.tmpsize=int(data.headers['content-length'])
            self.name=r.utils.unquote((self.u).split('/')[-1])
            self.provider="solidfiles"
        self.start()

    def tusfiles(self):
        try:
            self.u=utils.tusfiles.get_direct_link(r.get(self.url,headers={"User-Agent":ua()}).text,self.url)
        except DirectLinkError:
            print(f"{re}[X] File not found")
            return
        if args.direct:
            print(f"Link : {cy}{self.u}")
            return
        if not self.resume:
            data=r.head(self.u,headers={"User-Agent":ua(),"Connection":"Keep-Alive"})
            self.name=(self.u).split("/")[-1]
            self.tmpsize=int(data.headers['content-length'])
            self.provider="tusfiles"
        self.start()

    def anonfiles(self):
        try:
            self.u=utils.anonbayfiles.get_direct_link(r.get(self.url,headers={"User-Agent":ua()}).text)
        except DirectLinkError:
            print(f"{re}[X] File not found")
            return
        if args.direct:
            print(f"Link : {cy}{self.u}")
            return
        if not self.resume:
            data=r.head(self.u,headers={"User-Agent":ua(),"Connection":"keep-alive"})
            self.name=findall('filename="(.+)"',data.headers['Content-Disposition'])[0]
            self.tmpsize=int(data.headers['content-length'])
            self.provider="anonfiles"
        self.start()

    def bayfiles(self):
        try:
            self.u=utils.anonbayfiles.get_direct_link(r.get(self.url,headers={"User-Agent":ua()}).text)
        except DirectLinkError:
            print(f"{re}[X] File not found")
            return
        if args.direct:
            print(f"Link : {cy}{self.u}")
            return
        if not self.resume:
            data=r.head(self.u,headers={"User-Agent":ua(),"Connection":"keep-alive"})
            self.name=findall('filename="(.+)"',data.headers['Content-Disposition'])[0]
            self.tmpsize=int(data.headers['content-length'])
            self.provider="bayfiles"
        self.start()

    def racaty(self):
        try:
            self.u=utils.racaty.get_direct_link(r.get(self.url,headers={"User-Agent":ua()}).text,self.url)
        except DirectLinkError:
            print(f"{re}[X] File not found")
            return
        if args.direct:
            print(f"Link : {cy}{self.u}")
            return
        if not self.resume:
            data=r.head(self.u,headers={"User-Agent":ua(),"Connection":"keep-alive"})
            self.name=(self.u).split("/")[-1]
            self.tmpsize=int(data.headers['content-length'])
            self.provider="racaty"
        self.start()

    def zippyshare(self):
        try:
            self.u=utils.zippyshare.get_direct_link(r.get(self.url,headers={"User-Agent":ua()}).text,self.url)
        except DirectLinkError:
            print(f"{re}[X] File not found")
            return
        if args.direct:
            print(f"Link : {cy}{self.u}")
            return
        if not self.resume:
            data=r.Session().head(self.u,headers={"User-Agent":ua()})
            self.name=r.utils.unquote(findall("UTF-8\'\'(.+)",data.headers['Content-Disposition'])[0])
            self.tmpsize=int(data.headers['content-length'])
            self.provider="zippyshare"
        self.start()

    def hxfile(self):
        try:
            self.u=utils.hxfile.get_direct_link(r.get(self.url,headers={"User-Agent":ua()}).text,self.url)
        except DirectLinkError:
            print(f"{re}[X] File not found")
            return
        if args.direct:
            print(f"Link : {cy}{self.u}")
            return
        if not self.resume:
            data=r.head(self.u,headers={"User-Agent":ua(),"Connection":"keep-alive"})
            self.name=(self.u).split("/")[-1]
            self.tmpsize=int(data.headers['content-length'])
            self.provider="hxfile"
        self.start()

def get_setting():
    temp=[]
    with open("config.json","r",encoding="utf-8") as f:
        jsonvar=json.loads(f.read())
        temp.append(jsonvar["tmp_location"])
        temp.append(jsonvar["complete_location"])
        temp.append(jsonvar["chunk_size"])
        temp.append(jsonvar["thread_count"])
    return temp

if __name__ == "__main__":
    from math import floor
    from random import choice
    from platform import system as ps
    from shutil import move
    from re import findall
    from utils.exceptions import DirectLinkError
    import sys,time,os,json,argparse,concurrent.futures
    try:
        import utils.mediafire,utils.solidfiles,utils.tusfiles,utils.anonbayfiles,utils.racaty,utils.zippyshare,utils.hxfile
        import requests as r
        from requests.exceptions import ChunkedEncodingError, ConnectTimeout
    except ModuleNotFoundError:
        print("Install required package with \'pip install -r requirements.txt\'")
        sys.exit()
    if sys.version_info[0] == 3: pass
    else:
        print("Run with python3!")
        sys.exit()

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
            print("Install colorama with \'pip install colorama\'")
            sys.exit()
    else:
        re="\033[1;31m"
        gr="\033[1;32m"
        ye="\033[1;33m"
        ma="\033[1;35m"
        cy="\033[1;36m"
        de="\033[1;0m"
        clear="clear"

    tmp=get_setting()
    complete=tmp[1]

    parser=argparse.ArgumentParser()
    parser.add_argument("-p","--provider",metavar="provider",help="mediafire, solidfiles, tusfiles, anonfiles, bayfiles, racaty, zippyshare, hxfile", required=True, choices=["mediafire","solidfiles","tusfiles","anonfiles","bayfiles","racaty","zippyshare","hxfile"])
    parser.add_argument("-d","--grabdirectlink",help="Return direct download link",dest="direct",action="store_true")
    parser.add_argument("-c","--chunk",type=int,metavar="int",help="Override chunk size in config",default=tmp[2])
    parser.add_argument("-m","--mode",metavar="mode",help="Select singlethreaded or multithreaded download",choices=["single","multi"],default="single")
    parser.add_argument("-t","--threads",metavar="int",type=int,help="Override threads count in config",choices=range(2,9),default=tmp[3])
    parser.add_argument("url")
    args=parser.parse_args()
    tmp=tmp[0]

    if tmp[-1:] == "/": tmp=tmp[:-1]
    if complete[-1:] == "/": complete=complete[:-1]
    if not os.path.isdir(tmp): os.mkdir(tmp)
    if not os.path.isdir(complete): os.mkdir(complete)

    start()
    rundl=dl(args.url)
    if args.provider == "mediafire":
        rundl.mediafire()
    elif args.provider == "solidfiles":
        rundl.solidfiles()
    elif args.provider == "tusfiles":
        rundl.tusfiles()
    elif args.provider == "anonfiles":
        rundl.anonfiles()
    elif args.provider == "bayfiles":
        rundl.bayfiles()
    elif args.provider == "racaty":
        rundl.racaty()
    elif args.provider == "zippyshare":
        rundl.zippyshare()
    elif args.provider == "hxfile":
        rundl.hxfile()
else:
    raise ImportError("This script can\'t be imported, because may cause an error")
