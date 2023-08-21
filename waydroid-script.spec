%define pypi_name waydroid_script
%define pypi_version main

%if %{undefined arm64}
%define arm64 aarch64
%endif

%if %{undefined x86_64}
%define x86_64 x86_64 amd64
%endif

%ifarch %{arm} 
%define wayarch armeabi-v7a 
%elifarch %{arm64} 
%define wayarch arm64-v8a 
%elifarch %{x86_64}
%define wayarch x86_64
%elifarch %{ix86} 
%define wayarch x86
%endif

Name:           waydroid-%{flavor}
Version:        0
Release:        1%{?dist}


%if "%{flavor}" == "script"

Summary:        Script to add gapps and other stuff to waydroid!
License:        MIT
URL:            http://github.com/casualsnek/waydroid-script
Source0:        %{pypi_name}-%{pypi_version}.tar.gz
BuildArch: noarch

Requires:     python3-%{pypi_name}

BuildRequires:  python3-devel
BuildRequires:  python3dist(setuptools)

%description
Python Script to add OpenGapps, Magisk, libhoudini translation library and
libndk translation library to waydroid !


%package -n     waydroid-script-binary-%{wayarch}
Summary: Binaries for waydroid-script package
BuildArch: %{ix86}  %{x86_64} %{arm64} %{arm}

%description -n waydroid-script-binary-%{wayarch}
Binaries for waydroid-script package.

%package -n     python3-%{pypi_name}
Summary:          Script to add gapps and other stuff to waydroid!
BuildArch: noarch
%{?python_provide:%python_provide python3-%{pypi_name}}
Requires: lzip
Requires: waydroid-script-binary-%{wayarch}

%{lua:
for str in string.gmatch(rpm.expand('%{namerequires}'), "([^%s]+)") do
    print('Requires: python3dist(' .. str .. ')')
end
}

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

Summary:        Waydroid extra files
License:        LGPL
URL:            http://github.com/casualsnek/waydroid-script
Source0:        %{mainsource}


%{lua:
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

source = rpm.expand('%{mainsource}')
name = 'waydroid-' .. rpm.expand('%{flavor}')

arg={}
len = 0
for str in string.gmatch(rpm.expand('%{nameprovides}'), "([^%s]+)") do
    len=len + 1
    arg[len] = str
end

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

nw = string.char(10)


ind = 0
while ind < len do
  ind = ind + 1
  print(rpm.expand('%_waydroid_provide ' .. arg[ind]) .. nw)
end

filename = source:match("^.*/(.*)$") or source
path = rpm.expand('%_datadir/') .. name .. '/' .. filename
waydroidextradir = rpm.expand('%_waydroidextradir')

if len > 0 then
print([[

%post
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

%postun 
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
  .."'"..path .."'" .. nw .. "done" .. nw )
end

print('fi')
end

print(
[[


%files 
]])
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

%description
Waydroid extra files.

%endif
