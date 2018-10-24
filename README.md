# m3u8
a simple tool for downloading and merging video fragments, which may be encrypted, listed in m3u8 file
## requirements
scrapy  
pycryptodome
## usage
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
