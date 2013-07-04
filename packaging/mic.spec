%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:       mic
Summary:    Image Creator for Linux Distributions
Version:    0.20
Release:    0.rc1.<CI_CNT>.<B_CNT>
Group:      System/Base
License:    GPLv2
BuildArch:  noarch
URL:        http://www.tizen.org
Source0:    %{name}_%{version}.tar.gz
Requires:   rpm-python
Requires:   util-linux
Requires:   coreutils
Requires:   python >= 2.5
Requires:   e2fsprogs
Requires:   dosfstools >= 2.11-8
Requires:   syslinux >= 3.82
Requires:   kpartx
Requires:   parted
Requires:   device-mapper
Requires:   /usr/bin/genisoimage
Requires:   cpio
Requires:   isomd5sum
Requires:   gzip
Requires:   bzip2
Requires:   python-urlgrabber
Requires:   yum >= 3.2.24
%if ! 0%{?centos_version}
%if 0%{?suse_version}
Requires:   btrfsprogs
%else
Requires:   btrfs-progs
%endif
%endif

%if 0%{?suse_version}
Requires:   squashfs >= 4.0
Requires:   python-m2crypto
%else
Requires:   squashfs-tools >= 4.0
Requires:   m2crypto
%endif

%if 0%{?fedora_version} || 0%{?centos_version}
Requires:   syslinux-extlinux
%endif

%if 0%{?tizen_version:1}
Requires:   qemu-linux-user
%else
Requires:   qemu-arm-static
%endif

Requires:   tizen-python-zypp

BuildRequires:  python-devel
%if ! 0%{?tizen_version:1}
BuildRequires:  python-docutils
%endif

Obsoletes:  mic2

BuildRoot:  %{_tmppath}/%{name}_%{version}-build

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
%if ! 0%{?tizen_version:1}
make man
%endif

%install
rm -rf $RPM_BUILD_ROOT
%if 0%{?suse_version}
%{__python} setup.py install --root=$RPM_BUILD_ROOT --prefix=%{_prefix}
%else
%{__python} setup.py install --root=$RPM_BUILD_ROOT -O1
%endif

# install man page
mkdir -p %{buildroot}/%{_prefix}/share/man/man1
%if ! 0%{?tizen_version:1}
install -m644 doc/mic.1 %{buildroot}/%{_prefix}/share/man/man1
%endif

%files
%defattr(-,root,root,-)
%doc doc/*
%doc README.rst AUTHORS COPYING ChangeLog
%if ! 0%{?tizen_version:1}
%{_mandir}/man1/*
%endif
%dir %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/%{name}.conf
%{python_sitelib}/*
%dir %{_prefix}/lib/%{name}
%{_prefix}/lib/%{name}/*
%{_bindir}/*

