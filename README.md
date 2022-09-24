# File-Downloader
## About
File-Downloader is a script to download a file from (ex: mediafire) with command line.

<img src="https://img.shields.io/badge/Python-3-informational?logo=python&style=for-the-badge">

## Table of contents
- [Installation](#installation)
- [Usage](#usage)
  - [Download](#1-download)
  - [Resume](#2-resume)
  - [Paused](#3-paused)
  - [API Usage](#4-api)
- [Supported File Hosting](#supported-file-hosting)
- [Features](#features)
- [Known Issues](#known-issues)

## Installation
1. Clone this repository
```
git clone --depth 1 https://github.com/XniceCraft/file-downloader
```
2. Install python3 (if you haven't installed one)
<br>• Windows: ```Download python from https://www.python.org/```
<br>• Linux : ```sudo apt-get install python3```
3. Install required python module
```
pip install -r requirements.txt
```

To use the program read the [usage](#usage)

## Usage
### 1. Download
> Download a file or just return the download url.

```usage: prog.py download [-h] [-d] [-m mode] [-nt] [-o] [-c int] [-t int] url```

positional arguments:<br>
```url```

optional arguments:
 - -h, --help            show this help message and exit
 - -d, --grabdirectlink  Return direct download link
 - -m mode, --mode mode  Select singlethreaded or multithreaded download
 - -nt, --no-test        Skip the internet test
 - -o, --overwrite       Allow overwrite if file exists
 - -c int, --chunk int   Override chunk size in config
 - -t int, --threads int
                        Override threads count in config
 
> Example: ```python prog.py download https://mediafire.com/xxxxx```

### 2. Resume
> Continue paused download

```usage: prog.py resume [-h] [-c int] [-nt] [-o] id```

positional arguments:<br>
```id: That file id you wanna resume (get it with python prog.py paused)```

optional arguments:
  - -h, --help           show this help message and exit
  - -c int, --chunk int  Override chunk size in config
  - -nt, --no-test       Skip the internet test
  - -o, --overwrite      Allow overwrite if file exists

> Example: ```python prog.py resume 1```

### 3. Paused
> Return list of paused download(s)

```usage: prog.py paused```

### 4. API
> Import this program as a module

<a href="/API.md">View usage</a>

### Supported File Hosting
- Mediafire
- Solidfiles
- Tusfiles
- Anonfiles
- Bayfiles
- Racaty
- Zippyshare
- Hxfile

## Features
- Download speed meter
- Internet ping test (based on singapore firstmedia speedtest server)
- Pause (CTRL-C for pause)
- Can return direct download link with -d argument
- Can select singlethreaded or multithreaded (default: multithreaded)
- You can use import this as a module 

## Known Issues
- Sometimes program can't be paused when using multithreaded mode.

> Please report if there is a bug on this script
