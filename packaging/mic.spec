%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:       mic
Summary:    Image Creator for Linux Distributions
Version:    0.22.2
Release:    1
Group:      System/Base
License:    GPLv2
BuildArch:  noarch
URL:        http://www.tizen.org
Source0:    %{name}_%{version}.tar.gz
%if 0%{?tizen_version:1}
Requires:   python-rpm
%else
Requires:   rpm-python
%endif
Requires:   util-linux
Requires:   coreutils
Requires:   python >= 2.5
Requires:   e2fsprogs
Requires:   dosfstools >= 2.11
%if 0%{?centos_version}
Requires:   syslinux >= 3.82
%else
Requires:   syslinux >= 4.05
%endif
Requires:   kpartx
Requires:   parted
Requires:   device-mapper
Requires:   /usr/bin/genisoimage
Requires:   cpio
%if ! 0%{?tizen_version:1}
Requires:   isomd5sum
%endif
Requires:   gzip
Requires:   bzip2
Requires:   python-urlgrabber
Requires:   yum >= 3.2.24
Requires:   psmisc
%if ! 0%{?centos_version}
%if 0%{?suse_version}
Requires:   btrfsprogs
%else
Requires:   btrfs-progs
%endif
%endif

%if 0%{?suse_version} || 0%{?tizen_version:1}
Requires:   squashfs >= 4.0
Requires:   python-m2crypto
%else
Requires:   squashfs-tools >= 4.0
Requires:   m2crypto
%endif

%if 0%{?fedora_version} || 0%{?centos_version}
Requires:   syslinux-extlinux
%endif

%if 0%{?suse_version} || 0%{?tizen_version:1}
Requires:   /usr/bin/qemu-arm
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

# install bash completion
install -d -m0755 %{buildroot}/%{_sysconfdir}/bash_completion.d/
install -Dp -m0755 etc/%{name}.bash %{buildroot}/%{_sysconfdir}/bash_completion.d/%{name}.sh

# install zsh completion
install -d -m0755 %{buildroot}/%{_sysconfdir}/zsh_completion.d/
install -Dp -m0755 etc/_%{name} %{buildroot}/%{_sysconfdir}/zsh_completion.d/_%{name}

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
%{_sysconfdir}/bash_completion.d
%{_sysconfdir}/zsh_completion.d
