# file-downloader
Last update : 22/11/2021
### INFO
Built with : [Python3](https://www.python.org/)

Usage : ```python download_[single/multi].py -p [file hosting] [url] [Optional option]```
- -h    Show help
- -p    mediafire, solidfiles, tusfiles, anonfiles, bayfiles, racaty, zippyshare, hxfile

-  Optional options:
   - -grabdirectlink  Get direct download link only
   - -c [int]         Override chunk size in config
    
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
- Download speed meter (Updated every chunk size cycle - singlethreaded, Updated every second - multithreaded)
- Internet ping test (Based on singapore speedtest server)
- Pause (CTRL-C for pause (Multithreaded didn't support pause))
- Customized Chunk Size (Can be adjusted in config.json (written in kilobytes))
- Multithreaded (Still in beta)

> Please report if there is a bug on this script
