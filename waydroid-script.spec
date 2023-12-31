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

Name:           python-%{pypi_name}

Version:        0
Release:        1%{?dist}

AutoReqProv: no

Summary:        Script to add gapps and other stuff to waydroid!
License:        MIT
URL:            http://github.com/casualsnek/waydroid-script
Source0:        %{pypi_name}-%{pypi_version}.tar.gz

BuildArch: %{ix86}  %{x86_64} %{arm64} %{arm}

BuildRequires:  python3-devel
BuildRequires:  python3dist(setuptools)

%description
Python Script to add OpenGapps, Magisk, libhoudini translation library and
libndk translation library to waydroid !

%package -n     waydroid-script
AutoReqProv: no
Summary: Binaries for waydroid-script package
Requires:     python3-%{pypi_name}

%description -n waydroid-script
Executables for waydroid-script package.


%package -n     waydroid-script-binary-%{wayarch}
AutoReqProv: no
Summary: Binaries for waydroid-script package

%description -n waydroid-script-binary-%{wayarch}
Binaries for waydroid-script package.

%package -n     python3-%{pypi_name}
AutoReqProv: no
Summary:          Script to add gapps and other stuff to waydroid!
%{?python_provide:%python_provide python3-%{pypi_name}}
Requires: lzip
Provides:  python3dist(%{pypi_name})
Requires: waydroid-script-binary-%{wayarch}

%{lua:
for str in string.gmatch(rpm.expand('%{namerequires}'), "([^%s]+)") do
    
    print(string.char(10))
    print('Requires: python3dist(' .. str .. ')')
    print(string.char(10))
end
}

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
mkdir -p '%{buildroot}%{_bindir}'
cat << 'EOF' > '%{buildroot}%{_bindir}/waydroid-script'
#!/usr/bin/python3
from waydroid_script import main
main.main()

EOF
sed -i 's~\./bin~%{pypi_bindir}~'  '%{buildroot}%{python3_sitelib}/%{pypi_name}/stuff/general.py'

%files -n waydroid-script-binary-%{wayarch}
%{pypi_bindir}/%{wayarch}/resetprop 
%dir %{pypi_bindir}/%{wayarch}/
%dir %{pypi_bindir}/
%dir %{pypi_libdir}/

%files -n     waydroid-script
%attr(755,  root, root) %{_bindir}/waydroid-script

%files -n python3-%{pypi_name}
%license LICENSE
%doc README.md
%{python3_sitelib}/**/*
%dir %{python3_sitelib}/*
