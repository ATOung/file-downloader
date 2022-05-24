# -*- coding: utf-8 -*-
"""
File Downloader from python
Don't steal any code from this script
"""

#pylint: disable=invalid-name,multiple-statements,line-too-long,eval-used,multiple-imports,import-outside-toplevel
ua=lambda: choice(["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36","Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.62"])

class ThreadPaused(Exception):
    '''Exception for paused thread'''

def test():
    '''Test your internet ping with singapore firstmedia server.'''
    print(f"{cy}[%] Testing your connection")
    try:
        print(f"{de}{dgr}[%] Pinging to {wh}Singapore {dbl}Firstmedia speedtest server")
        s=time.time()
        r.get("http://sg-speedtest.fast.net.id.prod.hosts.ooklaserver.net:8080", timeout=3)
        ping=int((round(time.time() - s, 3))*1000)
        if ping < 500: print(f"{gr}[G] Your connection is good | Ping : {ping}ms")
        elif 500 <= ping < 1000: print(f"{ye}[N] Your connection is average | Ping : {ping}ms")
        else: print(f"{re}[B] Your connection is bad | Ping : {ping}ms")
    except (r.exceptions.ConnectTimeout,r.exceptions.ReadTimeout):
        print(f"{re}[Err] Connection Timeout. Ping exceeds 3000ms{de}")
        sys.exit()
    except r.exceptions.ConnectionError:
        print(f"{re}[Err] Connection Error!{de}")
        sys.exit()

def banner():
    '''Banner'''
    print(rf"""{de} ______ _ _         _____  _
|  ____(_) |       |  __ \| |
| |__   _| | ___   | |  | | |
|  __| | | |/ _ \  | |  | | |
| |    | | |  __/  | |__| | |____
|_|    |_|_|\___   |_____/|______|
Author : https://github.com/XniceCraft
Mode : {args.mode}
""")

def getsize(a):
    '''Return file size with its unit'''
    if a < 1024:
        v=str(a) + " Bytes"
    elif 1024 <= a < 1048576:
        v=str(round(a / 1024, 2)) + " KB"
    elif 1048576 <= a < 1073741824:
        v=str(round(a / 1048576, 2)) + " MB"
    elif a >= 1073741824:
        v=str(round(a / 1073741824, 2)) + " GB"
    return v

def start():
    '''Start'''
    if "https://" in args.url or "http://" in args.url:
        os.system(clear)
        banner()
        test()
        time.sleep(2)
        os.system(clear)
        banner()
        return
    print(f"{re}[Err] Invalid URL scheme. There is no http/https in URL{de}")
    sys.exit()

def download(name, num, url, pos, resume=False):
    '''Download function for multi and singlethread'''
    try: data=r.Session().get(url,headers={"User-Agent":ua(),"Range":f"bytes={pos['start']}-{pos['end']}"},stream=True, timeout=5)
    except (r.exceptions.ConnectionError,r.exceptions.ReadTimeout): return {"Pos":num,"Val":False}
    m="wb"
    if resume: m="ab"
    if args.mode == "multi":
        with open(f"{tmp}/{name}-{num}",m) as f:
            try:
                for l in data.iter_content(chunk_size=args.chunk*1024):
                    f.write(l)
                    rundl.dlded += len(l)
                    if kill_event.is_set(): raise KeyboardInterrupt
                f.close()
                rundl.pos[num]["start"]=rundl.pos[num]["start"]+os.path.getsize(f"{tmp}/{name}-{num}")
                return {"Pos":num,"Val":True}
            except (r.exceptions.ConnectionError, ChunkedEncodingError,r.exceptions.ReadTimeout, KeyboardInterrupt):
                f.close()
                rundl.pos[num]["start"]=rundl.pos[num]["start"]+os.path.getsize(f"{tmp}/{name}-{num}")
                return {"Pos":num,"Val":False}
    with open(f"{tmp}/{name}",m) as f:
        try:
            now=time.time()
            for l in data.iter_content(chunk_size=args.chunk*1024):
                f.write(l)
                rundl.dlded += len(l)
                try: speed=str(int(rundl.dlded / (time.time() - (now)) / 1000))
                except ZeroDivisionError: speed="0"
                done=round(100 * rundl.dlded / num,2)
                sys.stdout.write(cy+"\r"+"> [Downloading] Progress : "+str(done)+"% | Speed: "+speed+ " KB/s")
                sys.stdout.flush()
            f.close()
            _=os.path.getsize(f"{tmp}/{name}")
            rundl.dlded=_
            rundl.pos["start"]=rundl.pos["start"]+_
            return None
        except (r.exceptions.ConnectionError, ChunkedEncodingError,r.exceptions.ReadTimeout, KeyboardInterrupt) as e:
            f.close()
            _=os.path.getsize(f"{tmp}/{name}")
            rundl.dlded=_
            rundl.pos["start"]=rundl.pos["start"]+_
            raise ThreadPaused from e
    return None

def multitest(url):
    '''Return how many threads server can accept'''
    def runtest(url):
        return bool(r.Session().get(url,headers={"User-Agent":ua()},stream=True,timeout=10).status_code in [200,201,202,206])
    try:
        value=[]
        with concurrent.futures.ThreadPoolExecutor() as executor:
            result=[executor.submit(runtest,url) for _ in range(args.threads)]
            for future in concurrent.futures.as_completed(result):
                value.append(future.result())
        return value.count(True)
    except r.exceptions.ConnectionError:
        print(f"{re}[Err] Connection Error{de}")
        sys.exit()
    except r.exceptions.ReadTimeout:
        print(f"{re}[Err] Connection Timeout after 10000ms")
        sys.exit()

def multidl_handler(name, u, tmpsize, resume=False, thres=None):
    '''Handle the multithreaded download'''
    if resume:
        print(f"{ye}> [Info] Resuming")
        with concurrent.futures.ThreadPoolExecutor() as executor:
            failedthread=[i+1 for i in range(len(thres)) if not thres[i]]
            run=[executor.submit(download,name,_,u,rundl.pos[_],True) for _ in failedthread]
            now=time.time()
            try:
                while False in [i.done() for i in run]:
                    time.sleep(1)
                    try: speed=str(int(rundl.dlded / (time.time() - (now+1)) / 1000))
                    except ZeroDivisionError: speed="0"
                    done=round(100 * rundl.dlded / tmpsize,2)
                    sys.stdout.write(cy+"\r"+"> [Downloading] Progress : "+str(done)+"% | Speed: "+speed+ " KB/s")
                    sys.stdout.flush()
            except KeyboardInterrupt:
                print(f"\n{re}[I] Interrupted")
                kill_event.set()
    elif not resume:
        print(f"{ye}> [Info] Downloading")
        with concurrent.futures.ThreadPoolExecutor() as executor:
            run=[executor.submit(download,name,_+1,u,rundl.pos[_+1]) for _ in range(args.threads)]
            now=time.time()
            try:
                while False in [i.done() for i in run]:
                    time.sleep(1)
                    try: speed=str(int(rundl.dlded / (time.time() - (now+1)) / 1000))
                    except ZeroDivisionError: speed="0"
                    done=round(100 * rundl.dlded / tmpsize,2)
                    sys.stdout.write(cy+"\r"+"> [Downloading] Progress : "+str(done)+"% | Speed: "+speed+ " KB/s")
                    sys.stdout.flush()
            except KeyboardInterrupt:
                print(f"\n{re}[I] Interrupted")
                kill_event.set()
    return run

#Return Lxml Data
def mediafire(url):
    '''Return mediafire'''
    try:
        newurl=fr(r.get(url,headers={"User-Agent":ua()}).text).xpath('//a[@id="downloadButton"]/@href')[0]
    except IndexError:
        print(f"{re}[X] File not found")
        sys.exit()
    data=r.head(newurl,headers={"User-Agent":ua(),"Connection":"keep-alive"})
    rawsize=int(data.headers['content-length'])
    name=findall('filename="(.+)"',data.headers['Content-Disposition'])[0]
    return [newurl,rawsize,name]

def solidfiles(url):
    '''Return solidfiles'''
    try:
        temp=fr(r.get(url,headers={"User-Agent":ua()}).text)
        d="csrfmiddlewaretoken="+temp.xpath('//div[@class=\"buttons\"]/form/input[@name=\"csrfmiddlewaretoken\"]/@value')[0]+"&referrer="
        url=r.post("http://www.solidfiles.com"+tmp.xpath('//div[@class=\"buttons\"]/form/@action')[0],headers={"User-Agent":ua()},data=d).text
        newurl=findall('url=(.+)',fr(url).xpath("//meta[@http-equiv=\"refresh\"]/@content")[0])[0]
    except IndexError:
        print(f"{re}[X] File not found")
        sys.exit()
    data=r.head(newurl,headers={"User-Agent":ua(),"Connection":"keep-alive"})
    rawsize=int(data.headers['content-length'])
    name=r.utils.unquote(newurl.split('/')[-1])
    return [newurl,rawsize,name]

def tusfiles(url):
    '''Return tusfiles'''
    try:
        temp=fr(r.get(url,headers={"User-Agent":ua()}).text).xpath("//form[@method=\"POST\"]/input/@value")
        d=f"op={temp[0]}&id={temp[1]}&rand={temp[2]}&referer=&method_free=&method_premium=1"
        newurl=r.post(url,headers={"User-Agent":ua()},data=d,allow_redirects=False).headers["location"]
    except IndexError:
        print(f"{re}[X] File not found")
        sys.exit()
    data=r.head(newurl,headers={"User-Agent":ua(),"Connection":"Keep-Alive"})
    name=newurl.split("/")[-1]
    rawsize=int(data.headers['content-length'])
    return [newurl,rawsize,name]

def anonbayfiles(url):
    '''Return anonbay and bayfiles'''
    try:
        newurl=fr(r.get(url,headers={"User-Agent":ua()}).text).xpath('//a[@id=\"download-url\"]/@href')[0]
    except IndexError:
        print(f"{re}[X] File not found")
        sys.exit()
    data=r.head(newurl,headers={"User-Agent":ua(),"Connection":"keep-alive"})
    name=findall('filename="(.+)"',data.headers['Content-Disposition'])[0]
    rawsize=int(data.headers['content-length'])
    return [newurl,rawsize,name]

def racaty(url):
    '''Return racaty'''
    try:
        temp=fr(r.get(url,headers={"User-Agent":ua()}).text).xpath("//form[@id=\"getExtoken\"]/input/@value")
        d=f"op={temp[0]}&id={temp[1]}&rand={temp[2]}&referer=&method_free=&method_premium=1"
        _=r.post(url,headers={"User-Agent":ua()},data=d).text
        newurl=fr(_).xpath("//a[@id='uniqueExpirylink']/@href")[0]
    except IndexError:
        print(f"{re}[X] File not found")
        sys.exit()
    data=r.head(newurl,headers={"User-Agent":ua(),"Connection":"keep-alive"})
    name=newurl.split("/")[-1]
    rawsize=int(data.headers['content-length'])
    return [newurl,rawsize,name]

def zippyshare(url):
    '''Return zippyshare'''
    try:
        var=fr(r.get(url,headers={"User-Agent":ua()}).text).xpath("//a[@id=\"dlbutton\"]/following-sibling::script/text()")[0].splitlines()[1][:-1]
        var=var.replace("document.getElementById('dlbutton').href =","")
        _=findall(r"\((.+)\)",var)[0]
        var=var.replace(f"({_})",f"\"{eval(_)}\"")
        newurl="https://"+(url).split("/")[2]+eval(var)
    except IndexError:
        print(f"{re}[X] File not found")
        sys.exit()
    data=r.Session().head(newurl,headers={"User-Agent":ua()})
    name=r.utils.unquote(findall("UTF-8\'\'(.+)",data.headers['Content-Disposition'])[0])
    rawsize=int(data.headers['content-length'])
    return [newurl,rawsize,name]

def hxfile(url):
    '''Return hxfile'''
    try:
        temp=fr(r.get(url,headers={"User-Agent":ua()}).text).xpath("//form[@name=\"F1\"]/input/@value")
        d=f"op={temp[0]}&id={temp[1]}&rand={temp[2]}&referer=&method_free&method_premium=1"
        var=r.post(url,headers={"User-Agent":ua(),"content-type":"application/x-www-form-urlencoded"},data=d).text
        newurl=fr(var).xpath("//a[@class=\"btn btn-dow\"]/@href")[0]
    except IndexError:
        print(f"{re}[X] File not found")
        sys.exit()
    data=r.head(newurl,headers={"User-Agent":ua(),"Connection":"keep-alive"})
    name=newurl.split("/")[-1]
    rawsize=int(data.headers['content-length'])
    return [newurl,rawsize,name]

#Main handler class
class dl:
    '''Main class to handle the download'''
    def __init__(self, resume=False):
        self.resume=resume
        self.tmpsize=0
        self.name=None
        self.host=None
        self.dlded=0
        self.u=None
        self.pos={}
        self.res=None

    def ai(self):
        '''Calculate where the thread start and stop'''
        for i in range(args.threads):
            if i == 0: rundl.pos[1]={"start":0, "end":floor(self.tmpsize/args.threads)}
            elif i+1 == args.threads: rundl.pos[i+1]={"start":floor(self.tmpsize/args.threads)*i+1, "end":self.tmpsize}
            else: rundl.pos[i+1]={"start":floor(self.tmpsize/args.threads)*i+1, "end":floor(self.tmpsize/args.threads)*(i+1)}

    def finish(self):
        '''Handle when the download finished'''
        if args.command == "resume":
            os.remove(f"{tmp}/{self.name}.log")
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

    def paused(self):
        '''Handle pause for singlethreaded'''
        self.resume=True
        print(f"{gr}\r\n> Download paused. Resume, exit or remove(res/e/rem)?")
        ask=input("> ")
        if ask.lower() == "e" or ask.lower() == "exit":
            with open(f"{tmp}/{self.name}.log","w",encoding="utf-8") as f:
                f.write(f"Source: \'{args.url}\'\nSize: {self.tmpsize}\nName: \'{self.name}\'\nDownloaded: {rundl.dlded}\nThreads: 1\nMode: single\nThread-Pos: {rundl.pos}\nReturn-Pos: False")
            f.close()
            print(f"{gr}[>] Exit{de}")
            sys.exit()
        elif ask.lower() == "rem" or ask.lower() == "remove":
            os.remove(f"{tmp}/{self.name}")
            print(f"{gr}Sucessfully remove {self.name}{de}")
            sys.exit()
        os.system(clear)
        banner()
        if self.host == "mediafire":
            self.run("mediafire")
        elif self.host == "solidfiles":
            self.run("solidfiles")
        elif self.host == "tusfiles":
            self.run("tusfiles")
        elif self.host == "anonbayfiles":
            self.run("anonbayfiles")
        elif self.host == "racaty":
            self.run("racaty")
        elif self.host == "zippyshare":
            self.run("zippyshare")
        elif self.host == "hxfile":
            self.run("hxfile")

    def run(self, host):
        '''Handle the entire process'''
        self.host=host
        hostlist={
            "mediafire":mediafire,
            "solidfiles":solidfiles,
            "tusfiles":tusfiles,
            "anonbayfiles":anonbayfiles,
            "racaty":racaty,
            "zippyshare":zippyshare,
            "hxfile":hxfile
        }
        for key, value in hostlist.items():
            if host == key:
                lxmlval=value(args.url)
        if self.resume:
            self.u=lxmlval[0]
        else:
            self.u, self.tmpsize, self.name=lxmlval
        if args.direct:
            print(f"{ye}[%] Link : {cy}{self.u}")
            return
        print(f"""{de}> [INFO] Filename : {self.name}
         Size : {getsize(self.tmpsize)}""")
        if args.mode == "single":
            if not self.resume:
                print(f"{ye}> [Info] Downloading")
                try:
                    rundl.pos={"start":0,"end":self.tmpsize}
                    download(self.name,self.tmpsize,self.u,rundl.pos)
                    self.finish()
                    sys.exit()
                except ThreadPaused:
                    self.paused()
            print(f"{ye}> [Info] Resuming")
            try:
                download(self.name,self.tmpsize,self.u,rundl.pos,resume=True)
                self.finish()
                sys.exit()
            except ThreadPaused:
                self.paused()
        elif args.mode == "multi":
            if not self.resume:
                args.threads=multitest(self.u)
                self.ai()
                try: run=multidl_handler(self.name,self.u,self.tmpsize)
                except KeyboardInterrupt: pass
            while True:
                try:
                    reslist=sorted([i.result() for i in concurrent.futures.as_completed(run)], key=lambda p: p["Pos"])
                    self.res=[reslist[i]["Val"] for i in range(len(reslist))]
                    if all(self.res):
                        print(f"\r\n{de}> Assembling file into one solid file. Please wait!",end="")
                        self.finish()
                        return
                    print(f"{gr}\r\n> {self.res.count(False)} thread(s) failed. Try again, exit or remove(t/e/r)?")
                    ask=input("> ")
                    if ask.lower() == "e":
                        with open(f"{tmp}/{self.name}.log","w",encoding="utf-8") as f:
                            f.write(f"Source: \'{args.url}\'\nSize: {self.tmpsize}\nName: \'{self.name}\'\nDownloaded: {rundl.dlded}\nThreads: {args.threads}\nMode: multi\nThread-Pos: {rundl.pos}\nReturn-Pos: {self.res}")
                        f.close()
                        print(f"{gr}[>] Exit{de}")
                        sys.exit()
                    elif ask.lower() == "r":
                        for i in range(args.threads):
                            os.remove(f"{tmp}/{self.name}-{i+1}")
                        print(f"{re}> {gr}File {cy}{self.name} {gr}was successfully removed")
                        return
                except UnboundLocalError: pass
                self.resume=True
                os.system(clear)
                banner()
                try: run=multidl_handler(self.name,self.u,self.tmpsize,resume=True,thres=self.res)
                except KeyboardInterrupt: pass

def get_setting():
    '''Get and return program settings'''
    temp=[]
    try:
        with open("config.json","r",encoding="utf-8") as f:
            jsonvar=json.load(f)
            temp.append(jsonvar["tmp_location"])
            temp.append(jsonvar["complete_location"])
            temp.append(jsonvar["chunk_size"])
            temp.append(jsonvar["thread_count"])
            temp.append(jsonvar["default_mode"])
    except (json.decoder.JSONDecodeError, KeyError, FileNotFoundError):
        print(f"{re}[Err] Config file didn't found or corrupted\n[!] Creating new one!{de}")
        with open("config.json","w",encoding="utf-8") as f:
            f.write("""{
    \"tmp_location\":\"tmp\",
    \"complete_location\":\"complete\",
    \"chunk_size\":128,
    \"thread_count\":4,
    \"default_mode\":\"multi\"
}""")
            f.close()
        temp=["tmp","complete",128,4,"multi"]
    return temp

def get_paused(quiet=False):
    '''Get list of paused download'''
    from glob import glob
    pausedfile=glob(f"{tmp}/*.log")
    if not quiet: print(f"{dbl}[Info] {cy}List of paused download\n\n{de}{dgr}[Id]{dre}=={dcy}[Name]{de}")
    with open("paused.info","w",encoding="utf-8") as f:
        f.write("{")
        for i,n in enumerate(pausedfile):
            if not quiet: print(f"{re}[{i+1}] {gr}{os.path.basename(n).split('.log')[0]}{de}")
            if i == 0: f.write("\""+str(i+1)+"\""+":\""+os.path.basename(n).split('.log')[0]+"\"")
            elif i != 0 and i+1 != len(pausedfile): f.write(","+"\""+str(i+1)+"\""+":\""+os.path.basename(pausedfile[i]).split('.log')[0]+"\"")
        f.write("}")
        f.close()

if __name__ == "__main__":
    from math import floor
    from random import choice
    from platform import system as ps
    from shutil import move
    from re import findall
    import sys,time,os,json,argparse,concurrent.futures
    if sys.version_info[0] != 3:
        print("[Err] Run with python3!")
        sys.exit()
    try:
        from lxml.html import fromstring as fr
        import requests as r
        import yaml
        from requests.exceptions import ChunkedEncodingError
    except ModuleNotFoundError:
        print("Install required package with \'pip install -r requirements.txt\'")
        sys.exit()

    #COLOR CODE
    if ps() == 'Windows':
        try:
            from colorama import init, Fore, Style
            init()
            dre=Fore.RED
            dgr=Fore.GREEN
            dbl=Fore.BLUE
            dcy=Fore.CYAN
            wh=Fore.WHITE
            re=Fore.RED + Style.BRIGHT
            gr=Fore.GREEN + Style.BRIGHT
            ye=Fore.YELLOW + Style.BRIGHT
            cy=Fore.CYAN + Style.BRIGHT
            ma=Fore.MAGENTA + Style.BRIGHT
            de=Fore.RESET + Style.BRIGHT
            del(init,Fore,Style)
            clear="cls"
        except ModuleNotFoundError:
            print("Install colorama with \'pip install colorama\'")
            sys.exit()
    else:
        dre="\033[31m"
        dgr="\033[32m"
        dbl="\033[34m"
        dcy="\033[36m"
        wh="\033[37m"
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
    subparser=parser.add_subparsers(dest="command",required=True)
    parser1=subparser.add_parser("download",help="Download a file from url")
    parser1.add_argument("-d","--grabdirectlink",help="Return direct download link",dest="direct",action="store_true")
    parser1.add_argument("-c","--chunk",type=int,metavar="int",help="Override chunk size in config",default=tmp[2])
    parser1.add_argument("-m","--mode",metavar="mode",help="Select singlethreaded or multithreaded download",choices=["single","multi"],default=tmp[4])
    parser1.add_argument("-t","--threads",metavar="int",type=int,help="Override threads count in config",choices=range(2,9),default=tmp[3])
    parser1.add_argument("url")
    parser2=subparser.add_parser("resume",help="Resume paused download by selecting the id")
    parser2.add_argument("id",type=int,help="That file id you wanna resume")
    parser2.add_argument("-c","--chunk",type=int,metavar="int",help="Override chunk size in config",default=tmp[2])
    parser3=subparser.add_parser("paused",help="Get list of paused download")
    args=parser.parse_args()

    tmp=tmp[0]
    if tmp[-1:] == "/": tmp=tmp[:-1]
    if complete[-1:] == "/": complete=complete[:-1]
    if not os.path.isdir(tmp): os.mkdir(tmp)
    if not os.path.isdir(complete): os.mkdir(complete)

    if args.command in ["download","resume"]:
        if args.command == "resume":
            rundl=dl(resume=True)
            if not os.path.exists("paused.info"): get_paused(quiet=True)
            with open("paused.info",encoding="utf-8") as pfile:
                try:
                    with open(f"{tmp}/{json.load(pfile)[str(args.id)]}.log",encoding="utf-8") as idfile:
                        try:
                            dyaml=yaml.safe_load(idfile.read())
                            args.url=dyaml['Source']
                            args.mode=dyaml['Mode']
                            args.threads=dyaml['Threads']
                            args.direct=False
                            rundl.dlded=dyaml["Downloaded"]
                            rundl.pos=dyaml["Thread-Pos"]
                            rundl.tmpsize=dyaml["Size"]
                            rundl.name=dyaml["Name"]
                            rundl.res=dyaml["Return-Pos"]
                        except (KeyError, yaml.scanner.ScannerError):
                            print(f"{re} An error occured. Try get a new list of paused download!{de}")
                            sys.exit()
                        idfile.close()
                except FileNotFoundError:
                    print(f"{re}[Err] File with download {args.id} doesn't exist{de}")
                    sys.exit()
                pfile.close()
                del(idfile,pfile)
        else:
            rundl=dl()
        if not args.mode in ["multi","single"]:
            print(f"{re}[Err] Download mode isn't corrent{de}")
            sys.exit()
        if args.mode == "multi":
            from threading import Event as tevent
            kill_event=tevent()
        if not isinstance(args.threads,int):
            print(f"{re}[Err] Threads value must an interger")
            sys.exit()
        start()
        if "mediafire.com" in args.url:
            rundl.run("mediafire")
        elif "solidfiles.com" in args.url:
            rundl.run("solidfiles")
        elif "tusfiles.com" in args.url:
            rundl.run("tusfiles")
        elif "bayfiles.com" in args.url or "anonfiles.com" in args.url:
            rundl.run("anonbayfiles")
        elif "racaty.net" in args.url:
            rundl.run("racaty")
        elif "zippyshare.com" in args.url:
            rundl.run("zippyshare")
        elif "hxfile.co" in args.url:
            rundl.run("hxfile")
        else:
            print(f"{re}[X] File hosting that you insert isn't supported{de}")
    elif args.command == "paused":
        get_paused()
else:
    raise ImportError("This script can\'t be imported, because may cause an error")
