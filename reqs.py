#!/bin/python3
import re
import sys
from os import makedirs, listdir
from importlib import import_module as mod
from os.path import join, isfile, abspath, splitext, dirname, basename, exists, isdir
import argparse
from shutil import copy2, rmtree
from pathlib import Path

data_path = sys.path[0]

parser = argparse.ArgumentParser(
    prog='reqs.py',
    description='Formatting waydroid_script to distribution package')

parser.add_argument('--scriptdir')
parser.add_argument('--outputdir')


import re

def copytree(base, dest, exclude=()):
    if not isdir(base):
        makedirs(dirname(dest), exist_ok=True)
        copy2(base, dest)
        return 
    else: 
        makedirs(dest, exist_ok=True)
    dirs=['']
    while len(dirs):
        dir = dirs.pop()
        old_dir = join(base, dir)
        for i in listdir(old_dir):
            i = join(dir, i)
            j = join(base, i)
            if i in exclude:
                continue
            if (isdir(j)):
                dirs.append(i)
                makedirs(join(dest, i), exist_ok=True)
            else: 
                copy2(j, join(dest, i)) 
                
        
def replace(infile, oldstr, newstr):
    t=open(infile, 'r')
    oldtext=t.read().replace(oldstr, newstr)
    t.close()
    t=open(infile, 'w')
    t.write(oldtext)
    t.close()
            
def copydist(data_path, from_path, to_path, src):
    rmtree(to_path, ignore_errors=True)
    tosrcpath = join(to_path, src)
    copytree(from_path, tosrcpath, exclude=[
        '.git', 'assets', 'LICENSE', 'README.md', '.gitignore'])
    
    for i in ('LICENSE', 'README.md'):
        copy2(join(from_path, i), join(to_path, i))

    for i in ('setup.py', 'MANIFEST.in'):
        copy2(join(data_path, i), join(to_path, i))
    
    copytree(join(data_path, 'cache'), join(tosrcpath, 'cache'))
    makedirs(join(to_path, 'specs', 'main'), exist_ok=True)
    replace(join(tosrcpath, 'tools', 'helper.py'), 'import requests', 
    'requests=__import__("cache.hooks", fromlist=("cache")).default()')
    print('requests-file', file=open(join(tosrcpath, 'requirements.txt'), 'a'))
    
    t=open(join(tosrcpath, '__init__.py'), 'w')
    t.write('''
from sys import path
from os.path import dirname
path.append(dirname(__file__))
''')
    t.close()
    
    for i in ('cache', 'stuff', 'tools'):
        Path(join(tosrcpath, i, '__init__.py')).touch()

args=parser.parse_args()
outputdir=args.outputdir
scriptdir=args.scriptdir

if scriptdir:
    main_path = scriptdir
else:
    main_path = data_path

src = 'waydroid_script'

if outputdir:
    copydist(data_path, main_path, outputdir, src)
    main_path = join(outputdir, src)
    spec_path = join(outputdir, 'specs')
else: 
    spec_path = join(main_path, 'specs')
    
sys.path[0]=main_path

class Link:
    def __init__(self, names, url, id='falsetrip'):
        self.url=url
        self.names=names
        self.id = id
    def __str__(self):
        return str(self.names)
    def __repr__(self):
        return repr(str(self))

from stuff.hidestatusbar import HideStatusBar
from stuff.nodataperm import Nodataperm
from stuff.smartdock import Smartdock
from stuff.houdini import Houdini
from stuff.magisk import Magisk
from stuff.ndk import Ndk

def get_id(a):
    id = a.id.replace(' ', '-')
    ext = splitext(a.dl_file_name)[1][1:]
    id = id + '-' + ext
    return id

def get_links_ndk(a):
    links = a.dl_links
    name = a.dl_file_name
    ret = []
    id = get_id(a)
    for i in links.items():
        ver=i[0]
        l = Link((name, join(ver, name)), i[1][0], ver+'-'+id)
        ret.append(l)
    return ret
    
def get_links_magisk(a):
    link = a.dl_link
    name = a.dl_file_name
    id = get_id(a)
    return (Link((name,), link, id), )

links=[]

for i in (Ndk, Nodataperm, Houdini, HideStatusBar):
    links.extend(get_links_ndk(i))
    
for i in (Magisk, Smartdock):
    links.extend(get_links_magisk(i))    
    
from stuff.widevine import Widevine
from stuff.microg import MicroG
from stuff.gapps import Gapps

gapps = {
  '11': 'OpenGapps',
  '13': 'MindTheGapps'
}

def get_links_gapps(a):
    links = a.dl_links
    name = a.dl_file_name
    ret=[]
    ext = splitext(name)[1][1:]
    for i in links.items():
        ver=i[0]
        id = gapps[ver] + '-' + ext
        for u in i[1].items():
            arch=u[0]
            l = Link((name, join(ver, name), join(arch, ver, name)), 
                u[1][0], '-'.join((arch, ver, id)))
            ret.append(l)
    return ret    
    
def get_links_widevine(a):
    links = a.dl_links
    name = a.dl_file_name
    ret=[]
    id = get_id(a)
    for u in links.items():
        for i in u[1].items():
            l = Link((name, join(i[0], name), join(u[0], i[0], name)), 
                i[1][0], '-'.join((u[0], i[0], id)))
            ret.append(l)
    return ret    

def get_links_microg(a):
    links = a.dl_links
    name = a.id
    ext = 'zip'
    extname = '.'.join((name, ext)) 
    ret = []
    for i in links.items():
        var=i[0]
        l = Link((extname, name+'_'+var+'.'+ext),
            i[1][0], '-'.join((name, var, ext)))
        ret.append(l)
    return ret  

links.extend(get_links_widevine(Widevine))
links.extend(get_links_gapps(Gapps))
links.extend(get_links_microg(MicroG))

#j=open(join(data_path, 'template.spec'), 'r')
#text = j.read()
#j.close()

#%global flavor @BUILD_FLAVOR@%{nil}
#%global ADD_DESCRIPTION_FROM_SUMMARY yes

share_dir='/usr/share/waydroid-extra/'

j=open(join(main_path, 'cache', 'data.py'), 'w')

print ('url_cache={', file=j)

copylinks=[]
for i in links:
    u = i.names[-1]
    url = i.url
    if url == '':
        continue
    print(repr(i.url), ':', repr(join(share_dir, u)), ',', sep='', file=j)
    if i.id == 'magisk-delta-apk':
        continue
    copylinks.append(i)
    
links=copylinks
    
print('}', file=j)

j.close()

j=open(join(main_path, 'requirements.txt'), 'r')

reqs=[]
for i in j.readlines():
    i = i.strip()
    if not (len(i) == 0 or i[0] == '#'):
        reqs.append(i)

j.close()

j=open(join(spec_path, 'waydroid-script.spec'), 'w')

print('''
%define namerequires''', *reqs, file=j)

print(open(join(data_path,'waydroid-script.spec'),'r').read(), file=j)

j.close()


for i in links:
    id = i.id
    j=open(join(spec_path, id+'.spec'), 'w')
    id='waydroid-'+id
    print('Name: ', id, '\nSource0: ', i.url, 
'''
BuildArch: noarch
BuildRequires: rpm_macro(build_waydroid_extra_from_file)
%build_waydroid_extra_from_file --dscr yes ''', 
      *i.names, file=j)
    
    j.close()

j = open(join(spec_path, '_multibuild'), 'w')
print('<multibuild>', file=j)
for i in links:
    print('<flavor>', i.id, '</flavor>', sep='', file=j)
print('</multibuild>', file=j)
j.close()






