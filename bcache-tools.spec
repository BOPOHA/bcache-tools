#global gitdate 20131018

%if 0%{?fedora} >= 23
%global need_python3 1
%else
%global need_python3 0
%endif

Summary: Tools for Linux kernel block layer cache
Name: bcache-tools
Version: 1.0.8
Release: 5%{?dist}
License: GPLv2
Group: System Environment/Base
URL: http://bcache.evilpiepirate.org/
VCS: https://github.com/g2p/bcache-tools.git
# git clone https://github.com/g2p/bcache-tools.git
# cd bcache-tools/
# git archive --format=tar --prefix=bcache-tools-1.0.8/ v1.0.8 | gzip > ../bcache-tools-1.0.8.tar.gz
Source0: %{name}-%{version}.tar.gz
# This part is a prerelease version obtained by https://gist.github.com/djwong/6343451:
# git clone https://gist.github.com/6343451.git
# cd 6343451/
# git archive --format=tar --prefix=bcache-status-20140220/ 6d278f9886ab5f64bd896080b1b543ba7ef6c7a6 | gzip > ../bcache-status-20140220.tar.gz
# see also http://article.gmane.org/gmane.linux.kernel.bcache.devel/1951
Source1: bcache-status-20140220.tar.gz
# bcache status not provided as a true package, so this is a self maintained
# man page for it
# http://article.gmane.org/gmane.linux.kernel.bcache.devel/1946
Patch0: %{name}-status-20130826-man.patch
# configure is not "Fedora compliant", do a small step in the
# right direction
Patch2: %{name}-20131018-fedconf.patch
# util-linux takes care of bcache superblock identification so we remove
# the probe-cache call (which is Fedora specific):
Patch3: %{name}-1.0.8-noprobe.patch
# the following fix is pending upstream
# gcc 5.1.1 apparently is more picky than Fedora 21 gcc
Patch4: bcache-tools-1.0.8-crc64.patch
# Fedora 23 uses python3 by default
Patch5: bcache-status-python3.patch

%if %{need_python3}
Requires: python3
%else
Requires: python
%endif
# This is a kind of soft dependency: because we don't include probe-bcache
# we have to make sure that libblkid is able to identify bcache. So this
# is why it requires recent libblkid.
Requires: libblkid >= 2.24
Conflicts: dracut < 034
BuildRequires: libuuid-devel libblkid-devel systemd

%description
Bcache is a Linux kernel block layer cache. It allows one or more fast disk
drives such as flash-based solid state drives (SSDs) to act as a cache for
one or more slower hard disk drives.
This package contains the utilities for manipulating bcache.

%global _udevlibdir %{_prefix}/lib/udev
%global dracutlibdir %{_prefix}/lib/dracut

%prep
%setup -q -n bcache-tools-%{version}
tar xzf %{SOURCE1} --strip-components=1
%patch0 -p1 -b .man
%patch2 -p1 -b .fedconfmake
chmod +x configure
%patch3 -p1 -b .noprobe
%patch4 -p1 -b .crc64

%if %{need_python3}
%patch5 -p1 -b .python3
%endif

%build
%configure
make %{?_smp_mflags}

%install
mkdir -p \
    %{buildroot}%{_sbindir} \
    %{buildroot}%{_mandir}/man8 \
    %{buildroot}%{_udevlibdir} \
    %{buildroot}%{_udevrulesdir} \
    %{buildroot}%{dracutlibdir}/modules.d

%make_install \
    INSTALL="install -p" \
    UDEVLIBDIR=%{_udevlibdir} \
    DRACUTLIBDIR=%{dracutlibdir} \
    MANDIR=%{_mandir}

# prevent complaints when checking for unpackaged files
rm %{buildroot}%{_udevlibdir}/probe-bcache
rm %{buildroot}%{_mandir}/man8/probe-bcache.8
rm %{buildroot}%{_prefix}/lib/initcpio/install/bcache
rm %{buildroot}%{_datarootdir}/initramfs-tools/hooks/bcache


install -p  -m 755 bcache-status %{buildroot}%{_sbindir}/bcache-status

%files
%doc README COPYING
%{_udevrulesdir}/*
%{_mandir}/man8/*
%{_udevlibdir}/bcache-register
%{_sbindir}/bcache-super-show
%{_sbindir}/bcache-status
%{_sbindir}/make-bcache
%{dracutlibdir}/modules.d/90bcache

%changelog
* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.0.8-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Sat Jun 20 2015 Rolf Fokkens <rolf@rolffokkens.nl> - 1.0.8-4
- bcache-status now explicitly uses python3 not python on Fedora 23 and up

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.8-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Fri May 22 2015 Rolf Fokkens <rolf@rolffokkens.nl> - 1.0.8-2
- (#1224384) Now compiles on Fedora 22 / gcc 5.1.1

* Fri Dec 05 2014 Rolf Fokkens <rolf@rolffokkens.nl> - 1.0.8-1
- Sourced now from https://github.com/g2p/bcache-tools.git

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Sat May 10 2014 Rolf Fokkens <rolf@rolffokkens.nl> - 0.9-1
- Using the v0.9 git tag instead of the commit#
- Removed obsolete SOURCE2 (bcache-tools-dracut-module.tgz) way too late...

* Thu Feb 20 2014 Rolf Fokkens <rolf@rolffokkens.nl> - 0-0.16.20131018git
- (#1066555) updated bcache-status to latest upstream gist

* Fri Oct 18 2013 Rolf Fokkens <rolf@rolffokkens.nl> - 0-0.15.20131018git
- updated bcache-tools to latest upstream git
- dracut module is now included upstream
- bcache-register no longer needs patching
- Makefile no longer needs patching

* Wed Oct 02 2013 Rolf Fokkens <rolf@rolffokkens.nl> - 0-0.14.20130909git
- dropped pre F20 support; no use since deps on util-linux and dracut
- (#1004693) removed execute blkid in 61-bcache.rules
- (#1004693) moved 61-bcache.rules to 69-bcache.rules
- (#1004693) now inluding /usr/lib/dracut/modules.d/90bcache/...

* Mon Sep 30 2013 Rolf Fokkens <rolf@rolffokkens.nl> - 0-0.13.20130909git
- (#1004693) add execute blkid in 61-bcache.rules

* Fri Sep 27 2013 Rolf Fokkens <rolf@rolffokkens.nl> - 0-0.12.20130909git
- remove obsoleted probe-bcache in F20 using use_blkid macro

* Mon Sep 09 2013 Rolf Fokkens <rolf@rolffokkens.nl> - 0-0.11.20130909git
- updated to new bcache-status
- updated to new bcache-tools
- added libblkid-devel to BuildRequires

* Fri Sep 06 2013 Rolf Fokkens <rolf@rolffokkens.nl> - 0-0.10.20130827git
- fixed some udev related issues (#1004693)

* Mon Sep 02 2013 Rolf Fokkens <rolf@rolffokkens.nl> - 0-0.9.20130827git
- fedconfmake.spec file renamed to fedconfmake.patch
- removed libuuid as dependency
- removed trailing white-spaces in patch lines
- removed CFLAGS= from configure section
- removed (empty) check section
- replaced "make install" with make_install macro
- updated summary

* Sat Aug 31 2013 Rolf Fokkens <rolf@rolffokkens.nl> - 0-0.8.20130827git
- updated bcache-tools to commit 8327108eeaf3e0491b17d803da164c0827aae622
- corrected URL/VCS tag
- moved towards more RPM compliancy by using configure macro
- used "make install" to do most of the work
- added (empty) check section

* Mon Aug 26 2013 Rolf Fokkens <rolf@rolffokkens.nl> - 0-0.7.20130820git
- updated bcache-status to latest upstream gist
- removed the -rules patch

* Mon Aug 26 2013 Rolf Fokkens <rolf@rolffokkens.nl> - 0-0.6.20130820git
- removed tar and gcc from BuildRequires
- removed defattr from files section
- added upstream references to patches in comments 

* Sun Aug 25 2013 Rolf Fokkens <rolf@rolffokkens.nl> - 0-0.5.20130820git
- moved bcache-register to /usr/lib/udev
- suppress bcache-register error output (caused by registering device twice)
- removed man page for bcache-register
- added bcache-status
- added tar and gcc to BuildRequires
- added python to Requires

* Sat Aug 24 2013 Rolf Fokkens <rolf@rolffokkens.nl> - 0-0.4.20130820git
- Fixed the udev rules for Fedora

* Thu Aug 22 2013 Rolf Fokkens <rolf@rolffokkens.nl> - 0-0.3.20130820git
- Added systemd to BuildRequires

* Thu Aug 22 2013 Rolf Fokkens <rolf@rolffokkens.nl> - 0-0.2.20130820git
- Fixed initial review feedback

* Tue Aug 20 2013 Rolf Fokkens <rolf@rolffokkens.nl> - 0-0.1.20130820git
- Initial build
