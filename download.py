try:
    from bs4 import BeautifulSoup as Bs
    import requests as r,random as ra,lxml.html as lh,sys,platform,re as ru,time,os, argparse
except ModuleNotFoundError:
    print("Install required package with 'pip install -r requirements.txt'")

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
else:
    re="\033[1;31m"
    gr="\033[1;32m"
    ye="\033[1;33m"
    ma="\033[1;35m"
    cy="\033[1;36m"
    de="\033[1;0m"
    clear="clear"

#USER AGENT 
ua=[
"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 Edg/90.0.818.51",
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_3_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'
]

#CONNECTION TEST
def test():
    print(f"{cy}[T] Testing your connection")
    start=time.time()
    r.get("http://sg-speedtest.fast.net.id.prod.hosts.ooklaserver.net:8080")
    ping=int((round(time.time() - start, 3))*1000)
    if ping < 500:
        print(f"{gr}[G] Your connection is good | Ping : {ping}ms , pinged from Singapore Firstmedia speedtest server")
    elif 500 <= ping < 1000:
        print(f"{ye}[N] Your connection is normal | Ping : {ping}ms , pinged from Singapore Firstmedia speedtest server")
    else:
        print(f"{re}[B] Your connection is bad | Ping : {ping}ms , pinged from Singapore Firstmedia speedtest server")

def start():
    os.system(clear)
    print(f"""{de} ______ _ _         _____  _      
|  ____(_) |       |  __ \| |     
| |__   _| | ___   | |  | | |     
|  __| | | |/ _ \  | |  | | |     
| |    | | |  __/  | |__| | |____ 
|_|    |_|_|\___   |_____/|______|
Author : https://github.com/XniceCraft
""")
    test()
    time.sleep(2)
    os.system(clear)
    print(f"""{de} ______ _ _         _____  _      
|  ____(_) |       |  __ \| |     
| |__   _| | ___   | |  | | |     
|  __| | | |/ _ \  | |  | | |     
| |    | | |  __/  | |__| | |____ 
|_|    |_|_|\___   |_____/|______|
Author : https://github.com/XniceCraft
""")

#PAUSED DOWNLOADED
def paused(provider, downloaded, url, size):
    print(f"{gr}\r\n> Download paused. Resume or Exit (r/e)?")
    ask=input("> ")
    if ask.lower() == "r" or ask.lower() == "resume" or ask.lower() == "y":
        if provider == "mediafire":
            os.system(clear)
            print(f"""{de} ______ _ _         _____  _      
|  ____(_) |       |  __ \| |     
| |__   _| | ___   | |  | | |     
|  __| | | |/ _ \  | |  | | |     
| |    | | |  __/  | |__| | |____ 
|_|    |_|_|\___   |_____/|______|
Author : https://github.com/XniceCraft
""")
            mediafire(url, False, True, downloaded=downloaded, tmpsize=size)
        elif provider == "solidfiles":
            os.system(clear)
            print(f"""{de} ______ _ _         _____  _      
|  ____(_) |       |  __ \| |     
| |__   _| | ___   | |  | | |     
|  __| | | |/ _ \  | |  | | |     
| |    | | |  __/  | |__| | |____ 
|_|    |_|_|\___   |_____/|______|
Author : https://github.com/XniceCraft
""")
            solidfiles(url, False, True, downloaded=downloaded, tmpsize=size)
        elif provider == "tusfiles":
            os.system(clear)
            print(f"""{de} ______ _ _         _____  _      
|  ____(_) |       |  __ \| |     
| |__   _| | ___   | |  | | |     
|  __| | | |/ _ \  | |  | | |     
| |    | | |  __/  | |__| | |____ 
|_|    |_|_|\___   |_____/|______|
Author : https://github.com/XniceCraft
""")
            tusfiles(url, False, True, downloaded=downloaded, tmpsize=size)
    else:
        os.remove(name)
        print(f"{re}> {ma}File {cy}{name} {ma}removed")

#MEDIAFIRE
def mediafire(url, direct, resume, downloaded=0, tmpsize=0):
    html=r.get(url,headers={"User-Agent":ra.choice(ua)}).text
    try:
        u=lh.fromstring(html).xpath('//*[@id="downloadButton"]/@href')[0]
    except IndexError:
        print(f'{re}> [X] File not found')
        sys.exit()
    if direct == True:
        print(f"Link : {cy}{u}")
    else:
        if resume == True:
            data=r.Session().get(u,headers={"User-Agent":ra.choice(ua), "Range": f"bytes={str(downloaded)}-","Connection":"keep-alive"},stream=True)
            name=ru.findall('filename="(.+)"',data.headers['Content-Disposition'])[0]
            if tmpsize < 1024:
                size=str(tmpsize) + " Bytes"
            elif 1024 <= tmpsize < 1048576:
                size=str(round(tmpsize / 1024, 2)) + " KB"
            elif 1048576 <= tmpsize < 1073741824:
                size=str(round(tmpsize / 1048576, 2)) + " MB"
            elif 1073741824 <= tmpsize :
                size=str(round(tmpsize / 1073741824, 2)) + " GB"
            print(f"""{de}> [INFO] Filename : {name}
         Size : {size}""")
            with open(name, "ab") as f:
                print(f"{ye}> [Resume] Resuming...")
                tl=int(data.headers['content-length'])
                dl=0
                now=time.time()
                try:
                    for l in data.iter_content(chunk_size=int(tl/100)):
                        speed=time.time() - now
                        dl += len(l)
                        done = int(100 * dl / tl)  
                        sys.stdout.write(cy+"\r"+"> [Downloading] Progress : "+str(done)+"% | Speed: "+str(int(dl / speed / 1000)) + " Kbps") 
                        f.write(l)
                        sys.stdout.flush()
                    f.close()
                    print(f"\r\n{gr}> [Finished] Success download {name}")
                except KeyboardInterrupt:
                    f.close()
                    paused("mediafire",os.path.getsize(name),url,tmpsize)

        else:
            data=r.Session().get(u,headers={"User-Agent":ra.choice(ua),"Connection":"keep-alive"},stream=True)
            tmpsize=int(data.headers['content-length'])
            if tmpsize < 1024:
                size=str(tmpsize) + " Bytes"
            elif 1024 <= tmpsize < 1048576:
                size=str(round(tmpsize / 1024, 2)) + " KB"
            elif 1048576 <= tmpsize < 1073741824:
                size=str(round(tmpsize / 1048576, 2)) + " MB"
            elif 1073741824 <= tmpsize :
                size=str(round(tmpsize / 1073741824, 2)) + " GB"
            name=ru.findall('filename="(.+)"',data.headers['Content-Disposition'])[0]
            print(f"""{de}> [INFO] Filename : {name}
         Size : {size}""")
            with open(name, "wb") as f:
                print(f"{ye}> [Starting] Downloading")
                tl=int(data.headers['content-length'])
                dl=0
                now=time.time()
                try:
                    for l in data.iter_content(chunk_size=int(tl/100)):
                        speed=time.time() - now
                        dl += len(l)
                        done = int(100 * dl / tl)  
                        sys.stdout.write(cy+"\r"+"> [Downloading] Progress : "+str(done)+"% | Speed: "+str(int(dl / speed / 1000)) + " Kbps") 
                        f.write(l)
                        sys.stdout.flush()
                    f.close()
                    print(f"\r\n{gr}> [Finished] Success download {name}")
                except KeyboardInterrupt:
                    f.close()
                    paused("mediafire",os.path.getsize(name),url,tmpsize)

#SOLIDFILES
def solidfiles(url, direct, resume, downloaded=0, tmpsize=0):
    html=r.get(url,headers={"User-Agent":ra.choice(ua)}).text
    try:
        v1=lh.fromstring(html).xpath('//*[@id="content"]/div/div[2]/div[2]/article[1]/section[2]/div[1]/form/input[1]/@value')[0]
        data="csrfmiddlewaretoken="+v1+"&referrer="
        getform=Bs(html,'html.parser').find("div",{'class':"buttons"}).select("form")[0].get("action")
        url="http://www.solidfiles.com"+getform
    except IndexError:
        print(f'{re}> [X] File not found')
        sys.exit()
    html1=r.post(url,headers={"User-Agent":ra.choice(ua)},data=data).text
    u=lh.fromstring(html1).xpath('//*[@id="content"]/div/div[2]/div[2]/article[1]/section/p/a/@href')[0]
    if direct == True:
        print(f"Link : {cy}{u}")
    else:
        if resume == True:
            data=r.Session().get(u,headers={"User-Agent":ra.choice(ua), "Range": f"bytes={str(downloaded)}-","Connection":"keep-alive"},stream=True)
            if tmpsize < 1024:
                size=str(tmpsize) + " Bytes"
            elif 1024 <= tmpsize < 1048576:
                size=str(round(tmpsize / 1024, 2)) + " KB"
            elif 1048576 <= tmpsize < 1073741824:
                size=str(round(tmpsize / 1048576, 2)) + " MB"
            elif 1073741824 <= tmpsize :
                size=str(round(tmpsize / 1073741824, 2)) + " GB"
            name=r.utils.unquote(u.split('/')[-1])
            print(f"""{de}> [INFO] Filename : {name}
         Size : {size}""")
            with open(name, "ab") as f:
                print(f"{ye}> [Resume] Resuming...")
                tl=int(data.headers['content-length'])
                dl=0
                now=time.time()
                try:
                    for l in data.iter_content(chunk_size=int(tl/100)):
                        speed=time.time() - now
                        dl += len(l)
                        done = int(100 * dl / tl)
                        try:
                            sys.stdout.write(cy+"\r"+"> [Downloading] Progress : "+str(done)+"% | Speed: "+str(int(dl / speed / 1000)) + " Kbps")
                        except:
                            pass
                        f.write(l)
                        sys.stdout.flush()
                    f.close()
                    print(f"\r\n{gr}> [Finished] Success download {name}")
                except KeyboardInterrupt:
                    f.close()
                    paused("solidfiles",os.path.getsize(name),url,tmpsize)
        else:
            data=r.Session().get(u,headers={"User-Agent":ra.choice(ua),"Connection":"keep-alive"},stream=True)
            tmpsize=int(data.headers['content-length'])
            if tmpsize < 1024:
                size=str(tmpsize) + " Bytes"
            elif 1024 <= tmpsize < 1048576:
                size=str(round(tmpsize / 1024, 2)) + " KB"
            elif 1048576 <= tmpsize < 1073741824:
                size=str(round(tmpsize / 1048576, 2)) + " MB"
            elif 1073741824 <= tmpsize :
                size=str(round(tmpsize / 1073741824, 2)) + " GB"
            name=r.utils.unquote(u.split('/')[-1])
            print(f"""{de}> [INFO] Filename : {name}
         Size : {size}""")
            with open(name, "wb") as f:
                print(f"{ye}> [Starting] Downloading")
                tl=int(data.headers['content-length'])
                dl=0
                now=time.time()
                try:
                    for l in data.iter_content(chunk_size=int(tl/100)):
                        speed=time.time() - now
                        dl += len(l)
                        done = int(100 * dl / tl)  
                        sys.stdout.write(cy+"\r"+"> [Downloading] Progress : "+str(done)+"% | Speed: "+str(int(dl / speed / 1000)) + " Kbps")
                        f.write(l)
                        sys.stdout.flush()
                    f.close()
                    print(f"\r\n{gr}> [Finished] Success download {name}")
                except KeyboardInterrupt:
                    f.close()
                    paused("solidfiles",os.path.getsize(name),url,tmpsize)

#TUSFILES
def tusfiles(url, direct, resume, downloaded=0, tmpsize=0):
    html=r.get(url,headers={"User-Agent":ra.choice(ua)}).text
    try:
        tmp=Bs(str(Bs(html,"html.parser").find("form")),"html.parser").find_all("input")
        v1=f"op={lh.fromstring(tmp[0].encode()).xpath('//input/@value')[0]}&id={lh.fromstring(tmp[1].encode()).xpath('//input/@value')[0]}&rand={lh.fromstring(tmp[2].encode()).xpath('//input/@value')[0]}&referer={lh.fromstring(tmp[3].encode()).xpath('//input/@value')[0]}&method_free=&method_premium=1"
    except IndexError:
        print(f'{re}> [X] File not found')
        sys.exit()
    html1=r.post(url,headers={"User-Agent":ra.choice(ua)},data=v1,allow_redirects=False)
    if direct == True:
        print(f"Link : {cy}{html1.headers['location']}")
    else:
        if resume == True:
            data=r.get(html1.headers['location'],headers={"User-Agent":ra.choice(ua), "Range": f"bytes={str(downloaded)}-","Connection":"keep-alive"},stream=True)
            name=html1.headers['location'].split("/")[-1]
            if tmpsize < 1024:
                size=str(tmpsize) + " Bytes"
            elif 1024 <= tmpsize < 1048576:
                size=str(round(tmpsize / 1024, 2)) + " KB"
            elif 1048576 <= tmpsize < 1073741824:
                size=str(round(tmpsize / 1048576, 2)) + " MB"
            elif 1073741824 <= tmpsize :
                size=str(round(tmpsize / 1073741824, 2)) + " GB"
            print(f"""{de}> [INFO] Filename : {name}
         Size : {size}""")
            with open(name, "ab") as f:
                print(f"{ye}> [Resume] Resuming...")
                tl=int(data.headers['content-length'])
                dl=0
                now=time.time()
                try:
                    for l in data.iter_content(chunk_size=int(tl/100)):
                        speed=time.time() - now
                        dl += len(l)
                        done = int(100 * dl / tl)
                        try:
                            sys.stdout.write(cy+"\r"+"> [Downloading] Progress : "+str(done)+"% | Speed: "+str(int(dl / speed / 1000)) + " Kbps")
                        except:
                            pass
                        f.write(l)
                        sys.stdout.flush()
                    f.close()
                    print(f"\r\n{gr}> [Finished] Success download {name}")
                except KeyboardInterrupt:
                    f.close()
                    paused("tusfiles",os.path.getsize(name),url,tmpsize)
        else:
            data=r.get(html1.headers['location'],headers={"User-Agent":ra.choice(ua),"Connection":"keep-alive"},stream=True)
            name=html1.headers['location'].split("/")[-1]
            tmpsize=int(data.headers['content-length'])
            if tmpsize < 1024:
                size=str(tmpsize) + " Bytes"
            elif 1024 <= tmpsize < 1048576:
                size=str(round(tmpsize / 1024, 2)) + " KB"
            elif 1048576 <= tmpsize < 1073741824:
                size=str(round(tmpsize / 1048576, 2)) + " MB"
            elif 1073741824 <= tmpsize :
                size=str(round(tmpsize / 1073741824, 2)) + " GB"
            print(f"""{de}> [INFO] Filename : {name}
         Size : {size}""")
            with open(name, "wb") as f:
                print(f"{ye}> [Starting] Downloading")
                tl=int(data.headers['content-length'])
                dl=0
                now=time.time()
                try:
                    for l in data.iter_content(chunk_size=int(tl/100)):
                        speed=time.time() - now
                        dl += len(l)
                        done = int(100 * dl / tl)  
                        sys.stdout.write(cy+"\r"+"> [Downloading] Progress : "+str(done)+"% | Speed: "+str(int(dl / speed / 1000)) + " Kbps")
                        f.write(l)
                        sys.stdout.flush()
                    f.close()
                    print(f"\r\n{gr}> [Finished] Success download {name}")
                except KeyboardInterrupt:
                    f.close()
                    paused("tusfiles",os.path.getsize(name),url,tmpsize)

#MAIN
def main():
    arg=len(sys.argv)
    if arg > 3 and sys.argv[1] == "-p":
        if arg > 4 and sys.argv[4] == "-grabdirectlink":
            direct=True
        else:
            direct=False
        if sys.argv[2] == "mediafire":
            url=sys.argv[3]
            start()
            mediafire(url, direct, False)
        elif sys.argv[2] == "solidfiles":
            url=sys.argv[3]
            start()
            solidfiles(url, direct, False)
        elif sys.argv[2] == "tusfiles":
            url=sys.argv[3]
            start()
            tusfiles(url, direct, False)
        else:
            print(f"{de}File Hosting Not Found")
    else:
        print(f'''{de}Usage : python {sys.argv[0]} [option] [url] [optional option]
  -h    Show help
  -p    mediafire, solidfiles, tusfiles
  Optional options:
    -grabdirectlink  Get direct download link only''')

if __name__ == '__main__':
    main()