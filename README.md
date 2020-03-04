# m3u8
a simple tool for downloading and merging video fragments, which may be encrypted, listed in m3u8 file
## environment
* Linux, Windows 10, macOS
* python3 with pip
## install
```sh
git clone https://github.com/eagleoflqj/m3u8
cd m3u8
# read requirements.txt, then it's up to you whether use a virtual environment or not
python3 -m pip install -r requirements.txt
```
## usage
In the directory that contains scrapy.cfg.
```bash
scrapy crawl m3u8 -a m3u8='m3u8 file url' [-a merge='anything will prevent spider from merging video fragments']
```
or
```bash
scrapy crawl m3u8 -a page='static html page that contains m3u8 file url'[-a merge=...]
```
You can also merge video fragments manually, because you may remove some head or tail fragments which sometimes contain ads
```bash
python m3u8/merge_ts.py 'directory that contains all video fragments'
```
