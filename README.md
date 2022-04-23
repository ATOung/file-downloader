# file-downloader
Last update : 23/04/2022
### INFO
Built with : [Python3.8](https://www.python.org/)\
usage: prog.py [-h] [-d] [-c int] [-m mode] [-t int] url

positional arguments:\
```url```

optional arguments:
 - -h, --help            show this help message and exit
 - -d, --grabdirectlink  Return direct download link
 - -c int, --chunk int   Override chunk size in config
 - -m mode, --mode mode  Select singlethreaded or multithreaded download
 - -t int, --threads int Override threads count in config
    
### Supported File Hosting
- Mediafire
- Solidfiles
- Tusfiles
- Anonfiles
- Bayfiles
- Racaty
- Zippyshare
- Hxfile

### Features
- Download speed meter (updated every second - Multithread / every chunk cycle - Singlethread)
- Internet ping test (based on singapore firstmedia speedtest server)
- Pause (CTRL-C for pause) (Only works on singlethreaded)
- Grab direct download link with -d argument
- Can select singlethreaded or multithreaded (default: singlethreaded)

> Please report if there is a bug on this script
