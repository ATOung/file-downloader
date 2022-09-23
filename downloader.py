"""Module that implement downloader"""
#pylint: disable=invalid-name, line-too-long
from os import remove as osrm
from os.path import getsize, isfile
from math import floor
from shutil import move
from random import choice
from abc import ABC
from typing import Callable, Union
from sys import exit as sys_exit
from threading import Event as TEvent
import requests as req, concurrent
from yaml import safe_dump as yaml_safe_dump
from tqdm import tqdm
req.urllib3.disable_warnings(category=req.urllib3.exceptions.InsecureRequestWarning)

__all__=(
    'InvalidDataError', 'InvalidModeError',
    'ua', 'FileInfoBase',
    'FileDownloader'
)
class InvalidModeError(Exception):
    """Exception if user select neither single nor multi mode"""
    def __init__(self, value: str) -> None:
        """
        Parameter
        ---------
        value: str
            Download mode that user selected
        """
        super().__init__(f"Running download with mode: {value} is invalid. Please select either single or multi!")

class InvalidDataError(Exception):
    """Exception if data that passed is invalid"""
    def __init__(self) -> None:
        super().__init__("Data that you parsed is invalid")

def ua() -> str:
    """Returns Random User Agent"""
    return choice(["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
"Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.62"])

def default_pause_handler() -> str:
    """
    Default pause handler
    """
    while True:
        print("Your download got paused. (R) Resume, (E) Exit, (D) Delete?")
        user_input=input()
        if user_input.upper() in ('E','R','D'):
            return user_input.upper()

def download_finish() -> None:
    """
    Print finish message
    """
    print('Download finished!')

def dummy(*args) -> None: #pylint: disable=unused-argument
    """
    This is a dummy function
    """

class FileInfoBase(ABC):
    """
    Abstract class for file info
    """
    def __init__(self, data):
        self.__data=data

    @property
    def download_url(self) -> str:
        """
        Return
        -------
        str
            Download url from given url
        """
        return self.__data['download_url']

    @property
    def fmt_size(self) -> str:
        """
        Return
        -------
        str
            File size with it's format
        """
        return self.__data['fmt_size']

    @property
    def host(self) -> str:
        """
        Return
        -------
        str
            File hosting
        """
        return self.__data['host']

    @property
    def name(self) -> str:
        """
        Return
        -------
        str
            File name
        """
        return self.__data['name']

    @property
    def size(self) -> str:
        """
        Return
        -------
        int
            File size in bytes
        """
        return int(self.__data['size'])

    @property
    def url(self) -> str:
        """
        Return
        -------
        str
            Url that given by user
        """
        return self.__data['url']

class FileDownloader(FileInfoBase):
    """
    Class to download file
    """
    def __init__(self,
        data: dict, temp_obj,
        complete_obj, resume: bool=False,
        chunk_size: int=64, mode: str='multi',
        overwrite: bool=False, progress: bool=True,
        threads: int=4):
        super().__init__(data)
        self.__data={
            'allow_overwrite': overwrite,
            'chunk_size': chunk_size,
            'complete_obj': complete_obj,
            'complete_path': str(complete_obj),
            'enable_progress': progress,
            'is_complete': False,
            'is_resume': resume,
            'mode': mode,
            'temp_obj': temp_obj,
            'temp_path': str(temp_obj)
        }
        if self.mode not in ('single','multi'):
            raise InvalidModeError(self.mode)

        #Define essential variables
        self.__event_list={"on_pause": default_pause_handler, "post_pause": dummy, "pre_download": dummy, "post_download": download_finish}
        self.__multithreaded_data={'threads':threads, 'kill_event': TEvent(), 'threads_result': []}
        if self.mode == "single":
            self.__multithreaded_data['threads']=1
        self._download_position={}
        self._downloaded_bytes=0
        self._tqdm=None

    def __repr__(self):
        return f"<{self.host} size={self.fmt_size} name={self.name} is_complete={self.is_complete}>"

    @property
    def chunk_size(self) -> int:
        """Return download's chunk size"""
        return self.__data['chunk_size']

    @property
    def complete_path(self) -> str:
        """Return download's complete path"""
        return self.__data['complete_path']

    @property
    def is_complete(self) -> bool:
        """Return is the download finished or not"""
        return self.__data['is_complete']

    @property
    def mode(self) -> str:
        """Return download's mode"""
        return self.__data['mode']

    @property
    def temp_path(self) -> str:
        """Return download's temporary path"""
        return self.__data['temp_path']

    def _calculate_position(self) -> None:
        """
        Calculate where the thread start and stop
        """
        for i in range(self.__multithreaded_data['threads']):
            if i == 0:
                self._download_position[1]={"start":0, "end":floor(self.size/self.__multithreaded_data['threads'])}
            elif i+1 == self.__multithreaded_data['threads']:
                self._download_position[self.__multithreaded_data['threads']]={"start":floor(self.size/self.__multithreaded_data['threads'])*i+1, "end":self.size}
            else:
                self._download_position[i+1]={"start":floor(self.size/self.__multithreaded_data['threads'])*i+1, "end":floor(self.size/self.__multithreaded_data['threads'])*(i+1)}

    def _create_tqdm(self) -> None:
        """
        Function that create tqdm
        """
        self._tqdm=tqdm(**{
            'initial': self._downloaded_bytes,
            'total': self.size,
            'unit': 'B',
            'unit_scale': True,
            'unit_divisor': 1024,
            'miniters': 1,
            'smoothing': 0.7
        })

    def _close_tqdm(self) -> None:
        """
        Close the tqdm
        """
        if self._tqdm:
            self._tqdm.close()

    @staticmethod
    def _get_headers(start_range: int=None, end_range: int=None) -> dict:
        """
        Function that return headers value in dict

        Parameters
        ----------
        start_range: int=None
            Download start point

        end_range: int=None
            Download stop point

        Returns
        -------
        dict:
            Dict of needed headers
        """
        if not start_range and not end_range:
            return {"User-Agent": ua(), "Accept-Encoding":"identity", "Connection": "Keep-Alive"}
        return {"User-Agent": ua(), "Accept-Encoding":"identity",
               "Connection": "Keep-Alive", "Range":f"bytes={start_range}-{end_range}"}

    def _finish(self) -> None:
        """
        Triggered after download finished
        """
        self.__data['is_complete']=True
        self._close_tqdm()
        if self.__data["is_resume"] and isfile(f"{self.temp_path}-log"):
            osrm(f"{self.temp_path}-log")
        if self.mode == "multi":
            with open(self.complete_path,"wb") as file:
                for i in range(self.__multithreaded_data['threads']):
                    with open(f"{self.temp_path}-{i+1}","rb") as h:
                        file.write(h.read())
                    h.close()
                    osrm(f"{self.temp_path}-{i+1}")
            file.close()
        if self.mode == "single" and self.temp_path != self.complete_path:
            move(self.temp_path, self.complete_path)

    def _multithreaded_handler(self) -> list:
        """
        Function that handle for multithreaded downloading
        """
        if self.__data['is_resume']:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                failedthread=[val["Pos"] for val in self.__multithreaded_data['threads_result'] if not val["Val"]]
                run=[executor.submit(self._start_download, self._download_position[_]["start"], self._download_position[_]["end"], _) for _ in failedthread]
                try:
                    while False in [i.done() for i in run]:
                        pass
                except KeyboardInterrupt:
                    self.__multithreaded_data['kill_event'].set()
        elif not self.__data['is_resume']:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                run=[executor.submit(self._start_download, self._download_position[thread+1]['start'],self._download_position[thread+1]['end'], thread+1) for thread in range(self.__multithreaded_data['threads'])]
                try:
                    while False in [i.done() for i in run]:
                        pass
                except KeyboardInterrupt:
                    self.__multithreaded_data['kill_event'].set()
        return run

    @staticmethod
    def _multithreaded_test(url, threads) -> int:
        '''
        Test how many threads that server can handle
        '''
        def runtest(req_session_obj, url):
            return bool(req_session_obj.get(url, headers={"User-Agent":ua()}, stream=True, timeout=10, verify=False).status_code in [200,201,202,206])
        try:
            with req.Session() as request:
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    result=[executor.submit(runtest, request, url) for _ in range(threads)]
                    value=[future.result() for future in concurrent.futures.as_completed(result)]
            return value.count(True)
        except req.exceptions.ConnectionError:
            print("[Err] Connection Error")
            sys_exit()
        except req.exceptions.ReadTimeout:
            print("[Err] Connection Timeout after 10000ms")
            sys_exit()

    def _paused(self):
        """
        Function when user interrupt the downloading process
        """
        self.__data['is_resume']=True
        result=self.__event_list['on_pause']()
        if self.mode == 'single':
            if result == 'E':
                with open(f"{self.temp_path}-log", "w", encoding="utf-8") as f:
                    f.write(str(yaml_safe_dump({"Source":self.url,"Size":self.size, "Name":self.name, "Downloaded":self._downloaded_bytes, "Threads":1, "Mode":self.mode, "Download-Pos": self._download_position})))
                    f.close()
                sys_exit()
            elif result == "D":
                osrm(self.temp_path)
                sys_exit()
        elif self.mode == 'multi':
            self.__multithreaded_data['kill_event'].clear()
            if result == 'E':
                with open(f"{self.temp_path}-log", "w", encoding="utf-8") as f:
                    f.write(str(yaml_safe_dump({"Source": self.url,"Size":self.size, "Name":self.name, "Downloaded":self._downloaded_bytes, "Threads":self.__multithreaded_data["threads"], "Mode":self.mode, "Download-Pos": self._download_position, "Threads-Result":self.__multithreaded_data['threads_result']})))
                    f.close()
                sys_exit()
            elif result == "D":
                for i in range(self.__multithreaded_data['threads']):
                    osrm(f"{self.temp_path}-{i+1}")
                sys_exit()
        self.__event_list['post_pause']()
        self.download()

    def _start_download(self, start=None, end=None, thread_number=None) -> Union[None, dict]:
        headers=self._get_headers(start, end)
        resp=req.get(self.download_url, headers=headers, stream=True, verify=False)
        if self.mode == 'multi':
            with open(f"{self.temp_path}-{thread_number}", 'ab' if self.__data['is_resume'] else 'wb') as f:
                try:
                    previous_size=getsize(f"{self.temp_path}-{thread_number}")
                    for data in resp.iter_content(chunk_size=self.chunk_size*1024):
                        f.write(data)
                        self._downloaded_bytes+=len(data)
                        self._update_progress(len(data))
                        if self.__multithreaded_data['kill_event'].isSet():
                            raise KeyboardInterrupt
                    f.close()
                    self._download_position[thread_number]['start']+=getsize(f"{self.temp_path}-{thread_number}")-previous_size
                    return {"Pos":thread_number,"Val":True}
                except (req.exceptions.ConnectionError, req.exceptions.ChunkedEncodingError, req.exceptions.ReadTimeout, KeyboardInterrupt):
                    f.close()
                    self._download_position[thread_number]['start']+=getsize(f"{self.temp_path}-{thread_number}")-previous_size
                    return {"Pos":thread_number,"Val":False}
        elif self.mode == 'single':
            with open(self.temp_path, 'ab' if self.__data['is_resume'] else 'wb') as f:
                try:
                    for data in resp.iter_content(chunk_size=self.chunk_size*1024):
                        f.write(data)
                        self._downloaded_bytes+=len(data)
                        self._update_progress(len(data))
                    f.close()
                    self._downloaded_bytes=self.__data['temp_obj'].stat().st_size
                    self._download_position={"start": self._downloaded_bytes, "end": self.size}
                except (req.exceptions.ConnectionError, req.exceptions.ChunkedEncodingError, req.exceptions.ReadTimeout, KeyboardInterrupt) as e:
                    f.close()
                    self._close_tqdm()
                    self._downloaded_bytes=self.__data['temp_obj'].stat().st_size
                    self._download_position={"start": self._downloaded_bytes, "end": self.size}
                    raise KeyboardInterrupt from e

    def _update_progress(self, value) -> None:
        """
        Update tqdm progress
        """
        if self._tqdm:
            self._tqdm.update(value)

    def download(self):
        """
        Entry point function to download a file
        """
        if not self.__data['is_resume'] and bool(self.__data['complete_obj'].is_file() and not self.__data['allow_overwrite']):
            raise FileExistsError(f"File {self.complete_path} already exists.")
        self.__event_list['pre_download'](self.__data['is_resume'])
        if self.__data['enable_progress']:
            self._create_tqdm()
        if self.mode == 'single':
            try:
                if not self.__data['is_resume']:
                    self._start_download()
                    self._finish()
                    self.__event_list['post_download']()
                    return self
                self._start_download(self._download_position['start'], self._download_position['end'])
                self._finish()
                self.__event_list['post_download']()
                return self
            except KeyboardInterrupt:
                self._paused()
        elif self.mode == 'multi':
            if not self.__data['is_resume']:
                self.__multithreaded_data['threads']=self._multithreaded_test(self.download_url, self.__multithreaded_data['threads'])
                self._calculate_position()
            try:
                run=self._multithreaded_handler()
            except KeyboardInterrupt:
                pass
            self._close_tqdm()
            self.__multithreaded_data['threads_result']=sorted([i.result() for i in concurrent.futures.as_completed(run)], key=lambda p: p["Pos"])
            if all((i["Val"] for i in self.__multithreaded_data['threads_result'])):
                print('Assembling file into one solid file. Please wait!')
                self._finish()
                self.__event_list['post_download']()
                return self
            self._paused()

    def event(self, func: Callable, name: str=None) -> None:
        """
        Function to set pause handler, when pause condition achieved

        Parameters
        ----------
        func:
            Function that will executed at certain condition
        """
        name=func.__name__ if not name else name
        if name in self.__event_list:
            self.__event_list[name]=func

    def resume(self, data: dict, file_name: str=None, thread_result: dict=None):
        """
        Function to resume paused download

        Return
        ------
        FileDownloader
        """
        #data: {'size': real size of file in bytes, 'downloaded_bytes': how many bytes already downloaded, 'download_pos': the download position}
        if file_name:
            self.__data['name']=file_name
        try:
            self._download_position=data["download_pos"]
            self._downloaded_bytes=data["downloaded_bytes"]
            self.__data['size']=data['size']
            if self.mode == "multi":
                self.__multithreaded_data['threads_result']=thread_result
        except KeyError as e:
            raise InvalidDataError from e
        return self.download()
