import multiprocessing
import pathlib
import json
from dataclasses import dataclass
import random
import string

import requests

query = 'anime'
parallel_downloads = 5
name_len = 10
out_dir = pathlib.Path('~/d/wallpapers').expanduser()
aspect_ratio = '16:9'

@dataclass
class Wallpaper:
    path: str
    file_type: str
    dimensions: str

def search_wallpapers(query: str, aspect_ratio: str|None = None):
    wallpapers = []
    if aspect_ratio:
        aspect_ratio = aspect_ratio.replace(':', 'x') 
        data = json.loads(requests.get(f'https://wallhaven.cc/api/v1/search?q={query}&ratios={aspect_ratio},').text)
    else:
        data = json.loads(requests.get(f'https://wallhaven.cc/api/v1/search?q={query}').text)
    for wallpaper in data['data']:
            wallpapers.append(Wallpaper(wallpaper['path'], wallpaper['file_type'], wallpaper['resolution']))

    return wallpapers

def download_wallpaper(wallpaper: Wallpaper, out: pathlib.Path):
    data = requests.get(wallpaper.path).content
    with open(out, 'wb') as file:
        file.write(data)

def download_all_worker(wallpapers: multiprocessing.Queue):
    while not wallpapers.empty():
        wallpaper = wallpapers.get()
        print(f'[START] Download wallpaper {wallpaper.path} with dimensions {wallpaper.dimensions}...')
        extension = wallpaper.file_type.split('/')[-1]
        name = ''.join([random.choice(string.ascii_lowercase + string.digits) for _ in range(name_len)])
        download_wallpaper(wallpaper, out_dir / f'{name}.{extension}')
        print(f'[FINISH] Download wallpaper {wallpaper.path} with dimensions {wallpaper.dimensions}...')

def download_all(wallpapers_list: list[Wallpaper]):
    wallpapers = multiprocessing.Queue()

    for wallpaper in wallpapers_list:
        wallpapers.put(wallpaper)

    workers: list[multiprocessing.Process] = []
    for _ in range(parallel_downloads):
        workers.append(multiprocessing.Process(target=download_all_worker, args=(wallpapers,)))

    for worker in workers:
        worker.start()

    for worker in workers:
        worker.join()

download_all(search_wallpapers(query, aspect_ratio))
