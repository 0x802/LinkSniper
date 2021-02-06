#!/usr/bin/env python3
import sys
from re import findall
from httpx import get
from bs4 import BeautifulSoup
from concurrent.futures import ProcessPoolExecutor
from tldextract import extract

Targets_tags = [('a', 'href'),('base', 'href'),('link', 'href'),('script', 'src')]
search_url = lambda x : findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', x)
blacklist_path = ['#', '/'] 
blacklist_src = [   
    '.png', '.jpg', '.ttf','.otf', '.woff','.woff1','.woff2','.woff3',
    '.jpg', '.gif', '.jpge', '.srv', '.tif', '.tiff','.bmp', '.eps', 
    '.svg','.raw','.cr2', '.nef', '.orf', '.sr2'
]   

UserAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4351.102 Safari/537.36' 
def SaveOutput(data:str, filename:str):
    with open(filename , 'a') as Out:Out.write(f'{data}\n')

def chack(url:str,domain:str):
    try:
        if domain in extract(url).domain:return True
        else:return False
    except Exception as err:
        # print(f'[ ! ] [ ERROR ] [ CHACK ] {url} {err} ')
        return None

def black_list(src:str, status:str):
    if not src:return False

    src = src.lower()

    xp = lambda : None
    # xp = lambda: print(f'[ - ] [ BLACKLIS ] {src}')

    if '@' in src: 
        xp();return True

    elif status==0x0:
        for i in blacklist_src:
            if src.endswith(i):xp();return True

    else:
        if  src in blacklist_path:xp();return True
        else:
            if src[0:11] == 'javascript:':xp();return True
            elif src[0] == '#':xp();return True

    return False

def clear(data:str):
    for i in ['\'', ';', ')', '(', '\"']:data = data.split(i)[0]
    return data

def get_urls(Data:str, domain:str, cache:list):
    if not Data:
        # print(f"Data empty: {Data}")
        return []

    URLS = []

    domain_d= extract(domain).domain

    html = BeautifulSoup(Data,'lxml')
    # domain_ds = '.'.join([domain_d, domain_s])

    #TODO       Step [ 1 ]
    for _ in Targets_tags:
        tag , src = _
        links_list = html.findAll(tag)
        for link_list in links_list:
            

            # try:__ = link_list.get(src) 
            # except:
                # print(f'[ ! ] [ ERRER_GETSRC ] can\'t found {src} in {link_list}')
                # continue
            __ = clear(str(link_list.get(src))) 

            if not __ or __ == 'None':continue
            if black_list(__, 0x1):continue                

            #TODO       [ in scope and Url ]
            #TODO       if http[s]:[//]target.com OR http[s]:[//]targetHome.com OR  http[s]:[//]targetHome.com.us OR  http[s]:[//]target.us 
            #TODO       OR Subdomain ( target )
            if chack(__, domain_d) == True:
                fin = __.strip()

                # print(f'[ + ] [ FOUND_1 ] Found : {fin}')

                if __[0:2] == '//':
                    fin = fin.replace(fin[0:2], '')
                    fin = f"{domain.split(':')[0]}://{fin}" .strip()
                else: fin = __.strip()

                if fin not in cache and not black_list(fin, 0x0):
                    # print(f'[ + ] [ADD_LINKE_1] Add : {fin}')
                    URLS.append(fin)
                    cache.append(fin)
                    print(fin)
                    SaveOutput(fin, extract(domain).domain+'-links.txt')

                else:
                    pass
                    # print(f'[ - ] [ CACHE ] {fin} in CACHE')

            #TODO       [ in scope and Path ]
            #TODO       if /path/path/etc... OR # or etc ...
            elif chack(__, domain_d) == False and extract(__).suffix == '':
                if not black_list(__, 0x0):
                    fin = __.strip()
                    # print(f'[ + ] [ FOUND_2 ] Found : {fin}')
                    if fin[0:4] != 'http' and fin[0:2] != '//':
                        fin = domain + '/' + __ if domain[-1] != '/'  and __[0] != '/' else domain + __

                    if fin not in cache: 
                        # print(f'[ + ] [ADD_LINKE_2] Add : {fin}')
                        URLS.append(fin)
                        cache.append(fin)
                        print(fin)
                        SaveOutput(fin, extract(domain).domain+'-links.txt')

                    else:
                        pass
                        # print(f'[ - ] [ CACHE ] {fin} in CACHE')

            #TODO       [ Out Scope and ]
            #TODO       if https://akmskjnsjn.com OR //aksnkjnsjns.com == OUT SCOPE
            elif chack(__, domain_d) == False and  extract(__).suffix != '':
                # print(f'[ + ] [ OUT_SCOPE ] {__}')
                pass
            # sys.stdout.write(f'\r[ + ] urls : {len(cache)}\t')
            # sys.stdout.flush()



    #TODO       STEP [ 2 ]
    sr = search_url(html.text)
    for link_list in sr:
        link_list = clear(link_list)
        if black_list(link_list, 0x0):continue

        link_list= link_list[0:-1] if domain + '/' == link_list else link_list

        if link_list not in cache and chack(link_list,domain):
            # print(f'[ + ] [ADD_LINKE_3] Add : {link_list}')
            URLS.append(link_list)
            cache.append(link_list)
            print(link_list)
            SaveOutput(link_list, extract(domain).domain+'-links.txt')

        # sys.stdout.write(f'\r[ + ] urls : {len(cache)}\t')
        # sys.stdout.flush()

    return URLS

def process(args=None,url:str=None,domain:str=None,cache:list=None):
    if args:url, domain, cache = args

    try:
        # print(f"[ REQUEST ] {url}")
        
        Respons = get(url=url, timeout=20, verify=False, allow_redirects=True)
        try:title = BeautifulSoup(Respons.text, 'lxml').findAll('title')[0].text 
        except: title = ''
            
        SaveOutput(f'{Respons.url} [ {Respons.status_code} ] [ {len(Respons.text)} ] [ {title} ] ',  extract(domain).domain+'-details.txt')
        
        if Respons.status_code != 200: return list()

        # elif Respons.url in cache:return list() 

        LINKS = get_urls(Data=Respons.text, domain=domain, cache=cache)

        return LINKS
    
    except Exception:return list()

def main(target:str):
    target = target[0:-1] if target[-1] == '/' else target
    Cache = []
    Cache.append(target)
    WalletUrls = Cache

    # WalletUrls = process(url=target, domain=None,status=0x0)

    if not WalletUrls:print() ;exit(0) # ERR
    Registry = []
    domain = target

    while True:
        with ProcessPoolExecutor(max_workers=20) as e:
            for Link in WalletUrls:
                [Registry.append(rLINK) for rLINK in e.submit(process, args=[Link,domain,Cache]).result()]
                [Cache.append(_) if _ not in Cache else None for _ in Registry]
                
        WalletUrls , Registry= Registry, list()
        if not WalletUrls: break

if __name__ == '__main__':main(sys.argv[1])
