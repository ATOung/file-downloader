# file-downloader
Last update : 08/12/2021
### INFO
Built with : [Python3](https://www.python.org/)

Usage : ```python download.py [option] [url] [optional option]```
- Option
    - -h  Show help
    - -p  mediafire, solidfiles, tusfiles, anonfiles, bayfiles, racaty, zippyshare, hxfile
- Optional options:
    - -grabdirectlink    Get direct download link only
    - -c  [int]          Override chunk size in config
    - -t  [single/multi] Single threaded or multithreaded
    
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
- Download speed meter (updated every second)
- Internet ping test (based on singapore speedtest server)
- Pause (CTRL-C for pause (multithreaded didn't support pause))
- Customized Chunk Size (can adjusted in config.json (written in kilobytes)) or override with -c (value)
- Multithreaded (still in beta)

### Note : This script may not function properly or glitch. You can use the old one at [old-script branch](https://github.com/XniceCraft/file-downloader/tree/old-script)

> Please report if there is a bug on this script
