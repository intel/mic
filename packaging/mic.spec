%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
Name:       mic
Summary:    Image Creator for Linux Distributions
Version:    0.14
Release:    1
Group:      System/Base
License:    GPLv2
BuildArch:  noarch
URL:        http://www.tizen.org
Source0:    %{name}-%{version}.tar.gz
Requires:   rpm-python
Requires:   util-linux
Requires:   coreutils
Requires:   python >= 2.5
Requires:   e2fsprogs
Requires:   dosfstools
Requires:   syslinux
Requires:   kpartx
Requires:   parted
Requires:   device-mapper
Requires:   cpio
Requires:   gzip
Requires:   bzip2
Requires:   qemu-arm-static
Requires:   python-urlgrabber
#Requires:   btrfs-progs


Requires:   syslinux-extlinux

Requires:   python-zypp
BuildRequires:  python-devel

Obsoletes:  mic2

BuildRoot:  %{_tmppath}/%{name}-%{version}-build


%description
The tool mic is used to create and manipulate images for Linux distributions.
It is composed of three subcommand\: create, convert, chroot. Subcommand create
is used to create images with different types; subcommand convert is used to
convert an image to a specified type; subcommand chroot is used to chroot into
an image.


%prep
%setup -q -n %{name}-%{version}

%build
CFLAGS="$RPM_OPT_FLAGS" %{__python} setup.py build


%install
rm -rf $RPM_BUILD_ROOT
%if 0%{?suse_version}
%{__python} setup.py install --root=$RPM_BUILD_ROOT --prefix=%{_prefix}
%else
%{__python} setup.py install --root=$RPM_BUILD_ROOT -O1
%endif

# install man page
mkdir -p %{buildroot}/%{_prefix}/share/man/man1
install -m644 doc/mic.1 %{buildroot}/%{_prefix}/share/man/man1


%files
%defattr(-,root,root,-)
%doc README.rst
%{_mandir}/man1/*
%dir %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/%{name}.conf
%{python_sitelib}/*
%dir %{_prefix}/lib/%{name}
%{_prefix}/lib/%{name}/*
%{_bindir}/*
