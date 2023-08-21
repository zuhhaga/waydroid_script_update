#!/bin/python3
import re
import sys
from os import makedirs, listdir
from importlib import import_module as mod
from os.path import join, isfile, abspath, splitext, dirname, basename, exists, isdir
import argparse
from shutil import copy2, rmtree
from pathlib import Path

# def build_waydroid_extra_from_file(name, source, provisions=[], out=sys.stdout):
    # print("""Name: waydroid-{0}
# Version: 1
# Release: 1
# License: LGPL
# Summary: Waydroid extra files
# Source0: {1}""".format(name, source), file=out)
    # print("""
# %if %{undefined _waydroidextradir}
# %define _waydroidextradir %{_datadir}/waydroid-extra
# %endif

# %if %{undefined _waydroid_unit}
# %define _waydroid_unit() waydroid(%1)
# %endif

# %if %{undefined _waydroid_provide}
# %define _waydroid_provide() Provides: %{_waydroid_unit %{1}}
# %endif
    # """, file=out)
    # for token in provisions:
        # print('%_waydroid_provide', token, file=out)
    # filename = basename(source)
    # path = '%{_datadir}/%{name}/'+filename
    # dirstr = '%{_waydroidextradir}'
    # print("""
# %description
# %{summary}. 

# %post
# #!/bin/sh
# echo post install "$1"
# if [ "$1" == 1 ]; then""", file=out)
    # for token in provisions:
        # print("%{_sbindir}/update-alternatives --install '%{_waydroidextradir}/"
    # ,token,"' '%{_waydroid_unit ",token,"}' '",path,"' 25", sep='',file=out)
    # print('''fi
   
# %postun
# #!/bin/sh
# echo post remove "$1"
# if [ "$1" == 0 ]; then''', file=out) 
    # for token in provisions:
        # print("%{_sbindir}/update-alternatives --remove '%{_waydroid_unit ",
    # token,"}' '",path,"' 25", sep='', file=out)
    # dirs = set()
    # for i in provisions:
        # while i:
            # i = dirname(i)
            # dirs.add(i)
    # print('''fi

# %files''', path, sep='\n', file=out)
    # for i in dirs:
        # print('%dir', dirstr + '/' + i, file=out)
        
    # print("""
# %install
# mkdir -p '%{buildroot}%{_datadir}/%{name}'
# cp '%{_sourcedir}/""",
# filename,"""' '%{buildroot}""",path,"'",sep='',file=out)
    # for i in dirs:
        # print("mkdir -p '",'%{buildroot}',
        # dirstr,'/',i,"'",sep='', file=out)

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
    'requests=__import__("cache.data", fromlist=("cache")).url_cache')
    print('requests_file', file=open(join(tosrcpath, 'requirements.txt'), 'a'))
    Path(join(tosrcpath, '__init__.py')).touch()
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

for i in links:
    u = i.names[-1]
    url = i.url
    if url == '':
        continue
    print(repr(i.url), ':', repr(join(share_dir, u)), ',', sep='', file=j)

print('}', file=j)

j.close()

j=open(join(main_path, 'requirements.txt'), 'r')

reqs=[]
for i in j.readlines():
    i = i.strip()
    if not (len(i) == 0 or i[0] == '#'):
        reqs.append(i)

j.close()

reqs=list(map(lambda x: 'Requires: python3dist('+x+')', reqs))

j=open(join(data_path, 'waydroid-script.spec'), 'r')
text = j.read()
j.close()

text = text.replace('%requires', '\n'.join(reqs))

j=open(join(spec_path, 'waydroid-script.spec'), 'w')
print(r"""
%define ADD_DESCRIPTION_FROM_SUMMARY no
%global flavor @BUILD_FLAVOR@%{nil}
%define pypi_name waydroid_script
%define pypi_version main

%ifarch %{arm} 
%define wayarch armeabi-v7a 
%endif

%ifarch %{arm64} aarch64 
%define wayarch arm64-v8a 
%endif   Script to add gapps and other stuff to waydroid!

%ifarch %{x86_64} x86_64 amd64
%define wayarch x86_64
%endif

%ifarch %{ix86} 
%define wayarch x86
%endif

%define descr %{expand:
Python Script to add OpenGapps, Magisk, libhoudini translation library and
libndk translation library to waydroid !
}

%description
%{descr}

%define build_waydroid_extra_from_file(-) %{lua: 
larg = {}
lopt = {}

len = #arg
ind = 0

while ind < len do
  ind = ind + 1
  tk = arg[ind]
  if tk:sub(1, 2) == '--' then
    ind = ind + 1
    lopt[tk:sub(3)] = arg[ind]
  else 
    larg[#larg+1] = tk
  end
end

arg = larg

name = lopt['name'] or rpm.expand('%{?NAME:%NAME}')
if name == '' then 
  error('name is not defined')
end
source = lopt['source'] or rpm.expand('%{?SOURCE0:%SOURCE0}')
if source == '' then
  error('source is not defined')
end

license = lopt['license'] or rpm.expand('%{?LICENSE:%LICENSE}%{!?LICENSE:LGPL}')
summary = lopt['summary'] or rpm.expand('%{?SUMMARY:%SUMMARY}%{!?SUMMARY:Waydroid extra files}')
version = lopt['version'] or rpm.expand('%{?VERSION:%VERSION}%{!?VERSION:1}')
release = lopt['release'] or rpm.expand('%{?RELEASE:%RELEASE}%{!?RELEASE:1}')

main = lopt['dscr'] or rpm.expand('%{ADD_DESCRIPTION_FROM_SUMMARY}')
main = main:lower()
createdescription = (main == 'ok') or (main == 'yes') or (main == 'y') or (main == '1')

--main = opt.main
--main = main:lower()
--main = (main == 'ok') or (main == 'yes') or (main == 'y') or (main == '1')

a,b=rpm.isdefined('_waydroidextradir')
if (not a) or b then
  rpm.define('_waydroidextradir %{_datadir}/waydroid-extra')
end

a,b=rpm.isdefined('_waydroid_unit')
if (not a) or (not b) then
  rpm.define('_waydroid_unit() waydroid(%1)')
end

a,b=rpm.isdefined('_waydroid_provide')
if (not a) or (not b) then
  rpm.define('_waydroid_provide() Provides: %{_waydroid_unit %{1}}')
end

len=#arg

ind=0
dirs={}

while ind < len do
  ind = ind + 1
  dir = arg[ind]
  while dir do
    dir=dir:match("(.*)/")
    if dir then
        dirs['/' .. dir ] = 1
    else 
        dirs[''] = 1
    end
  end
end
nw = string.char(10) .. string.char(13)

--if main then
--    print('Name: ' .. name .. nw)
--else
--    print('%package -n ', name, nw)
--end

--print('License: ' .. license .. nw
--   .. 'Summary: ' .. summary .. nw
--   .. 'Version: ' .. version .. nw
--   .. 'Release: ' .. release .. nw)

ind = 0
while ind < len do
  ind = ind + 1
  print(rpm.expand('%_waydroid_provide ' .. arg[ind]) .. nw)
end

filename = source:match("^.*/(.*)$") or source
path = rpm.expand('%_datadir/') .. name .. '/' .. filename
waydroidextradir = rpm.expand('%_waydroidextradir')

if createdescription then
    print([[

%description 
]])
    --if main then
    --print('-n ', name)
    --end
    print(summary .. '.' .. nw)
end

if len > 0 then
print([[

%post ]])
--if main then 
--    print('-n ', name)
--end
print([[

#!/bin/sh
echo post install "$1"
if [ "$1" == 1 ]; then
]])

ind = 0

alternatives = rpm.expand('%{_sbindir}/update-alternatives')

if len == 1 then
  ind = ind + 1
  token = arg[ind]
  print(
  alternatives .. " --install '" .. waydroidextradir .. '/' 
  ..token..rpm.expand("' '%{_waydroid_unit "..token.."}' '" ) 
  ..path.."' 25" .. nw) 
else 
print('for i in ')
while ind < len do
  ind = ind + 1
  token = arg[ind]
  print("'" .. token .. "' ")
end
print('; do '..nw..alternatives.." --install '"..
    waydroidextradir.."'"..rpm.expand('/"$i" "%{_waydroid_unit $1}" ')
    .."'"..path .."' 25" .. nw .. "done" .. nw )
end


print([[
fi

%postun ]])
--if main then 
--    print('-n ', name)
--end
print([[

#!/bin/sh
echo post remove "$1"
if [ "$1" == 0 ]; then
]])

ind = 0

if len == 1 then
  ind = ind + 1
  token = arg[ind]
  print(alternatives .. rpm.expand(" --remove '%{_waydroid_unit "
  ..token.."}' '")..path.."' " .. nw) 
else 
print('for i in ')
while ind < len do
  ind = ind + 1
  token = arg[ind]
  print("'" .. token .. "' ")
end
print('; do '..nw..alternatives.. rpm.expand(
  ' --remove "%{_waydroid_unit $1}" ')
  .."'"..path .."' 25" .. nw .. "done" .. nw )
end

print('fi')
end

print(
[[


%files ]])
--if main then 
--    print('-n ', name)
--end
print(nw)
print(path, nw)
for key, v in pairs(dirs) do
  print('%dir '.. waydroidextradir ..  key .. nw)
end


print([[

%install 
]])

for key, v in pairs(dirs) do
  print('mkdir -p ' .. waydroidextradir .. key .. nw)
end
print("cp '"..rpm.expand('%{_sourcedir}/')..filename.."' " )

}

""", file=j)

k = '%if'
copylinks=[]
for i in links:
    id=i.id
    url=i.url
    if id == 'magisk-delta-apk':
        continue
    if url == '':
        continue
    copylinks.append(i)
    print (k, '"%{flavor}" == "'+id+'" ',file=j)
    k = '%elif'
    print ("%define mainsource", url, '\n%define nameprovides' *i.names, file=j) 
links=copylinks

print('''%else
%global flavor script%{nil}', file=j)
%endif

%if "%flavor" == "script"
  %define main_name %{pypi_name}
%else
  %define main_name waydroid-%{flavor}
%endif


Name:           %{main_name}
Version:        0
Release:        1%{?dist}
Summary:        Script to add gapps and other stuff to waydroid!
License:        MIT
URL:            http://github.com/casualsnek/waydroid-script

BuildRequires:  python3-devel
BuildRequires:  python3dist(setuptools)


%if "%flavor" == "script"
Source0:        %{pypi_name}-%{pypi_version}.tar.gz


%package -n     waydroid-script-binary-%{wayarch}
Summary: Binaries for waydroid-script package

%description -n waydroid-script-binary-%{wayarch}
Binaries for waydroid-script package.

%package -n    waydroid-script
Summary:         Script to add gapps and other stuff to waydroid!
BuildArch: noarch
Requires:     python3-%{pypi_name}

%package -n     python3-%{pypi_name}
Summary:          Script to add gapps and other stuff to waydroid!
BuildArch: noarch
%{?python_provide:%python_provide python3-%{pypi_name}}
Requires: lzip
Requires: waydroid-script-binary-%{wayarch}

%requires


%description -n waydroid-script
Python Script to add OpenGapps, Magisk, libhoudini translation library and
libndk translation library to waydroid !

%description -n python3-%{pypi_name}
Python Script to add OpenGapps, Magisk, libhoudini translation library and
libndk translation library to waydroid !

%prep
%autosetup -n %{pypi_name}-%{pypi_version}

%build
%py3_build
%define  pypi_libdir    %{_usr}/lib/%{pypi_name}
%define  pypi_bindir  %{pypi_libdir}/bin
%define  pypi_oldbindir  %{python3_sitelib}/%{pypi_name}/bin

%install
%py3_install
mkdir -p %{buildroot}%{pypi_bindir}/%{wayarch}/
mv   %{buildroot}%{pypi_oldbindir}/%{wayarch}/resetprop    %{buildroot}%{pypi_bindir}/%{wayarch}/resetprop
rm -R %{buildroot}%{pypi_oldbindir}
ln -s %{pypi_bindir}   %{buildroot}%{pypi_oldbindir}


%files -n waydroid-script-binary-%{wayarch}
%{pypi_bindir}/%{wayarch}/resetprop 
%dir %{pypi_bindir}/%{wayarch}/
%dir %{pypi_bindir}/
%dir %{pypi_libdir}/

%files -n waydroid-script
%{_bindir}/waydroid-script

%files -n python3-%{pypi_name}
%license LICENSE
%doc README.md
%{python3_sitelib}/**/*
%dir %{python3_sitelib}/*



%else
Source0:        %mainsource
%{build_waydroid_extra_from_file  --name waydroid-%{flavor}  --source  %{mainsource}  }
%endif

''', file=j)
#    build_waydroid_extra_from_file(id, i.url, i.names, j)

j.close()

j = open(join(spec_path, '_multibuild'), 'w')
print('<multibuild>', file=j)
for i in links:
    print('<flavor>', i.id, '</flavor>', sep='', file=j)
print('</multibuild>', file=j)
j.close()
