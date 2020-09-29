#!/usr/bin/python3.7

from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from bs4 import BeautifulSoup
import numpy as np
import requests
import tempfile
import os
import re
import sys
import random

is_direct = False
is_local = False
width = os.get_terminal_size().columns
font = ImageFont.truetype('DejaVuSansMono.ttf', 16)
characters = list('!"#$%&\'(*+,-./0123456789:;<=?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[^_`abcdefghijklmnopqrstuvwxyz{|~ ')

def get_image(destination):
    try:
        html = requests.get(destination)
        html.raise_for_status()
        soup = BeautifulSoup(html.text,'lxml')
        links = soup.find_all('img')
        for i in range(10):
            link = links[random.randrange(len(links))].get('src')
            if re.match('https?://[\w/:%#\$&\?\(\)~\.=\+\-]+', link):
                image = requests.get(link)
                image.raise_for_status()
                break
            elif i >= 9:
                raise Exception('Oh dear. Couldn\'t find any image.\nWhy don\'t you try with my name?')
    except Exception as e:
        print('Error: ', e)
        sys.exit(1)
    fd, temp_path = tempfile.mkstemp()
    with open(temp_path, 'wb') as f:
        f.write(image.content)
    return temp_path

def normalize(l):
    l_min = min(l)
    l_max = max(l)
    return [(i - l_min) / (l_max - l_min) * 255 for i in l]

def calc_density():
    l = []
    for i in characters:
        im = Image.new('L', (24,24), 'black')
        draw = ImageDraw.Draw(im)
        draw.text((0,0), i, fill='white', font=font)
        l.append(np.array(im).mean())
    normed = normalize(l)
    dict = {key: val for key, val in zip(normed, characters)}
    return sorted(dict.items(), key=lambda x:x[0])

arg = sys.argv

if '-h' in arg or '-help' in arg:
    print(' Okey, here is the fuckin\' help.\n'
        '\n'
        '  Usase: jason2aa.py keyword keyword .. [option]\n'
        '\n'
        '  [Options]\n'
        '   -w   Width of AA (The number of characters)\n'
        '   -p   Path to image file.\n'
        '\n'
        ' If I wes you, I\'m sure I can handle such a bullshit app without help.\n'
        ' Because, I\'m a true man.')
    sys.exit(0)
if '-w' in arg:
    w_index = arg.index('-w')
    try:
        width = int(arg.pop(w_index + 1))
        arg.pop(w_index)
    except Exception:
        print('Watch it! You passed me a invalid argument as width.\nI replaced it with default width.')
        for i in range(1):
            arg.pop(w_index)
if '-p' in arg:
    p_index = arg.index('-p')
    try:
        path = arg.pop(p_index + 1)
        arg.pop(p_index)
        if re.match('.+\.(png|jpg|jpeg|bmp|gif|tiff)', path):
            if re.match('https?://[\w/:%#\$&\?\(\)~\.=\+\-]+', path):
                try:
                    image = requests.get(path)
                    image.raise_for_status()
                    fd, temp_path = tempfile.mkstemp()
                    with open(temp_path, 'wb') as f:
                        f.write(image.content)
                    is_direct = True
                    file_path = temp_path
                except Exception as e:
                    raise Exception(e)
            else:
                if os.path.exists(path):
                    is_local = True
                    file_path = path
                else:
                    raise Exception('There ain\'t any such file. Are you fucking with me?')
        else:
            raise Exception('The path ain\'t to image file. Are you fucking with me?')
    except Exception as e:
        print(e, '\nThe above error blocked me accessing the path.\nBut, don\'t worry. Here is the my photo.')
        url = 'https://www.google.com/search?q=Jason+Statham&tbm=isch&safe=off&num=100&pws=0'
        file_path = get_image(url)
else:
    if len(arg) <= 1:
        arg = ['Jason', 'Statham']
    url = 'https://www.google.com/search?q=' + '+'.join(arg) + '&tbm=isch&safe=off&num=100&pws=0'
    file_path = get_image(url)

for i in range(10):
    img = Image.open(file_path)
    if img.mode == 'RGB':
        cont = ImageEnhance.Contrast(img)
        img_gray = cont.enhance(2.5).convert('L').resize((width, int(img.height*width/img.width//2)))
        break
    elif is_local or is_direct:
        print('Shit! I could only find only useless image.\nYou pass me files containing fuckin\' alpha channel, aren\'t you?.')
        sys.exit(1)
    elif i >= 9:
        print('Damm it! I could only find only useless image.\nMaybe, fuckin\' alpha channel is contained.')
        sys.exit(1)
    else:
        os.remove(file_path)
        file_path = get_image(url)

maps = calc_density()
density_map = np.array([i[0] for i in maps])
charcter_map = np.array([i[1] for i in maps])
imarray = np.array(img_gray)
index = np.searchsorted(density_map, imarray)
aa = charcter_map[index]

aa = aa.tolist()
for i in range(len(imarray)):
    print(''.join(aa[i]))

if not is_local:
    os.remove(file_path)

sys.exit(0)
