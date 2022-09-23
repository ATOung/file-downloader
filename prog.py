#pylint: disable=invalid-name, line-too-long, import-error
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

def test() -> None:
    '''Test your internet ping with singapore firstmedia server.'''
    print(f"{re}[{ye}%{re}] {cy}Testing your connection{de}")
    try:
        print(f"{re}[{wh}%{re}] {ye}Pinging to Singapore Firstmedia speedtest server")
        s=time()
        req.get("http://sg-speedtest.fast.net.id.prod.hosts.ooklaserver.net:8080", timeout=3)
        s2=time()
        ping=int((round(s2 - s, 3))*1000)
        if ping < 500:
            print(f"{gr}[G] Your connection is good | Ping: {ping}ms")
        elif 500 <= ping < 1000:
            print(f"{ye}[N] Your connection is ok | Ping : {ping}ms")
        else:
            print(f"{re}[B] Your connection is bad | Ping : {ping}ms")
    except (req.exceptions.ConnectTimeout,req.exceptions.ReadTimeout):
        print(f"{re}[Err] Connection Timeout. Ping exceeds3000ms{de}")
        sys_exit()
    except req.exceptions.ConnectionError:
        print(f"{re}[Err] Connection Error!{de}")
        sys_exit()

def start(mode: str, url: str, skip_test=False) -> None:
    '''Start'''
    if "https://" in url or "http://" in url:
        os_system(clear)
        if not skip_test:
            banner(mode)
            test()
            sleep(2)
            os_system(clear)
        banner(mode)
        return
    print(f"{re}[Err] Invalid URL scheme. There is no http/https in URL{de}")
    sys_exit()

def get_paused(temp: str, quiet: bool=False) -> None:
    '''Get list of paused download(s)'''
    file_list=glob(f"{temp}/*.temp-log")
    file_dict={}
    if not quiet:
        print(f">>> {ye}[{cy}Info{ye}] {gr}List of Paused Download\n{wh}----------------------------------\n{re}[Id]   {cy}[Name]{de}")
    for i,n in enumerate(file_list):
        if not quiet:
            print(f"{gr}[{i+1}] {os_basename(n).split('.temp-log')[0]}{de}")
            file_dict[i+1]=os_basename(n).split('.temp-log')[0]
    with open("paused.json","w",encoding="utf-8") as f:
        json_dump(file_dict, f)
        f.close()

def get_user_setting() -> list:
    '''Get config.json'''
    result=[]
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            jsonvar=json_load(f)
            result=[jsonvar[i] for i in ["temp_location","complete_location","chunk_size","thread_count","default_mode"]]
    except (JSONDecodeError, KeyError, FileNotFoundError):
        print(f"""{de}>>> {re}[Err] Config file didn't found or corrupted\n{de}>>> {gr}[{wh}+{gr}] Creating new config.json!{de}""")
        with open("config.json", "w", encoding="utf-8") as f:
            json_dump({"temp_location":"temp","complete_location":"complete","chunk_size":128,"thread_count":4,"default_mode":"multi"},f)
            f.close()
        result=["temp","complete",128,4,"multi"]
    return result

def main():
    """Program main function"""
    temp_dir=get_user_setting()
    complete_dir=temp_dir[1]

    #Argument parser
    parser=ArgumentParser()
    subparser=parser.add_subparsers(dest="action",required=True)
    parser1=subparser.add_parser("download",help="Download a file from url")
    parser1.add_argument("-d","--grabdirectlink",help="Return direct download link",dest="direct",action="store_true")
    parser1.add_argument("-m","--mode", metavar="mode",help="Select singlethreaded or multithreaded download",choices=["single","multi"],default=temp_dir[4])
    parser1.add_argument("-nt","--no-test", action="store_true", help="Skip the internet test", dest="notest")
    parser1.add_argument("-o","--overwrite", action="store_true", help="Allow overwrite if file exists")
    parser1.add_argument("-c","--chunk", type=int, metavar="int", help="Override chunk size in config", default=temp_dir[2])
    parser1.add_argument("-t","--threads", type=int, metavar="int", help="Override threads count in config", choices=range(2,9), default=temp_dir[3])
    parser1.add_argument("url")
    parser2=subparser.add_parser("resume",help="Resume paused download by selecting the id")
    parser2.add_argument("id", type=int, help="That file id you wanna resume")
    parser2.add_argument("-c","--chunk",type=int,metavar="int",help="Override chunk size in config", default=temp_dir[2])
    parser2.add_argument("-nt","--no-test", action="store_true", help="Skip the internet test", dest="notest")
    parser2.add_argument("-o","--overwrite", action="store_true", help="Allow overwrite if file exists")
    subparser.add_parser("paused",help="Get list of pauseddownload")
    args=parser.parse_args()

    temp_dir=temp_dir[0]
    if args.action == "download":
        start(args.mode, args.url, skip_test=args.notest)
        if args.direct:
            print(f"{gr}>>> [{wh}={gr}] Link : {cy}{extract_info(args.url).download_url}{de}")
            return
        elif args.mode == "single":
            args.threads=1
        dl=setup_download(args.url,
            complete_dir=complete_dir,
            temp_dir=temp_dir,
            chunk_size=args.chunk,
            mode=args.mode,
            overwrite=args.overwrite,
            threads=args.threads)
    elif args.action == "paused":
        get_paused(temp_dir)
    elif args.action == "resume":
        if not os_exists("paused.json"):
            get_paused(temp_dir, quiet=True)
        with open("paused.json", encoding="utf-8") as f:
            try:
                with open(f"{temp_dir}/{json_load(f)[str(args.id)]}.temp-log", encoding="utf-8") as selected_f:
                    load_yaml=yaml_safe_load(selected_f.read())
                downloaded_bytes=load_yaml["Downloaded"]
                download_pos=load_yaml["Download-Pos"]
                file_name=load_yaml["Name"]
                mode=load_yaml["Mode"]
                resume_kwargs={"file_name": file_name}
                size=load_yaml["Size"]
                threads=1
                url=load_yaml["Source"]
                if mode == 'multi':
                    threads=load_yaml["Threads"]
                    threads_result=load_yaml["Threads-Result"]
                    resume_kwargs.update({"thread_result": threads_result})
            except (KeyError, YamlScannerError):
                print(f"{re} An error occured. Try get a new list of paused download!{de}")
                sys_exit(1)
            except FileNotFoundError:
                print(f"{re}[Err] File with download {args.id} doesn't exist{de}")
                sys_exit(1)
            f.close()
        start(mode, url, skip_test=args.notest)
        dl=setup_download(url,
            complete_dir=complete_dir,
            temp_dir=temp_dir,
            chunk_size=args.chunk,
            mode=mode,
            threads=threads,
            overwrite=args.overwrite,
            resume=True)
    @dl.event
    def on_pause():
        while True:
            print(f"{re}[!] {ye}Your download got paused. {gr}(R) {ye}Resume, {gr}(E) {ye}Exit, {gr}(D) {ye}Delete?{de}")
            user_input=input()
            if user_input.upper() in ('E','R','D'):
                return user_input.upper()
    @dl.event
    def post_pause():
        os_system(clear)
        banner(args.mode)
    @dl.event
    def pre_download(is_resume):
        if is_resume:
            print(f"""{de}> [INFO] Filename : {dl.name}
         Size : {dl.fmt_size}
{ye}> [Info] Resuming{de}""")
        else:
            print(f"""{de}> [INFO] Filename : {dl.name}
         Size : {dl.fmt_size}
{ye}> [Info] Downloading{de}""")
    @dl.event
    def post_download():
        print(f"{gr}> Download Finished!{de}")
        
        #Do return or download
        dl.resume({"size":size, "downloaded_bytes": downloaded_bytes, 'download_pos': download_pos}, **resume_kwargs) if args.action == "resume" else dl.download()

if __name__ == "__main__":
    from glob import glob
    from platform import system as ps
    from fetch import extract_info, setup_download
    from time import time, sleep
    from yaml import safe_load as yaml_safe_load
    from yaml.scanner import ScannerError as YamlScannerError
    from os import system as os_system
    from os.path import basename as os_basename, exists as os_exists
    from sys import exit as sys_exit
    from argparse import ArgumentParser
    from json.decoder import JSONDecodeError
    from json import load as json_load, dump as json_dump
    import requests as req

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
            del init, Fore
            clear="cls"
        except ModuleNotFoundError:
            print("Install colorama with \'pip install colorama\'")
            sys_exit()
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
else:
    raise ImportError("This prog.py isn't intended to be imported as module")
