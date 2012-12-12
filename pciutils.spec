# when updating, please rebuild ldetect as it is compiled against this static library

%bcond_with	bootstrap
%bcond_without	diet
%bcond_without	uclibc

%define	major	3
%define	libname	%mklibname pci %{major}
%define	devname	%mklibname pci -d

Summary:	PCI bus related utilities
Name:		pciutils
Version:	3.1.10
Release:	4
License:	GPLv2+
Group:		System/Kernel and hardware
URL:		http://atrey.karlin.mff.cuni.cz/~mj/pciutils.shtml
Source0:	ftp://atrey.karlin.mff.cuni.cz/pub/linux/pci/%{name}-%{version}.tar.gz
Patch0:		pciutils-3.0.3-use-stdint.patch
Patch10:	pciutils-3.1.2-pcimodules.patch
Patch11:	pciutils-3.0.3-cardbus-only-when-root.patch
# allow build with dietlibc, using sycall() and sys/io.h
Patch20:	pciutils-2.2.6-noglibc.patch
# allow build with dietlibc, not using unsupported features:
Patch21:	pciutils-3.0.3-fix-compiliing-w-diet.patch
Patch22:	pciutils-3.1.10-LDFLAGS.patch

# Fedora patches
# don't segfault on systems without PCI bus (rhbz #84146)
Patch102:	pciutils-2.1.10-scan.patch
# use pread/pwrite, ifdef check is obsolete nowadays
Patch103:	pciutils-havepread.patch
# multilib support
Patch108:	pciutils-3.0.2-multilib.patch
# platform support 3x
Patch110:	pciutils-2.2.10-sparc-support.patch
Patch111:	pciutils-3.0.1-superh-support.patch
Patch112:	pciutils-3.1.8-arm.patch
Patch113:	pciutils-3.1.10-dont-remove-static-libraries.patch

%if !%{with bootstrap}
Requires:	pciids
%endif
%if %{with diet}
BuildRequires:	dietlibc-devel
%endif
%if %{with uclibc}
BuildRequires:	uClibc-devel >= 0.9.33.2-15
%endif
#- previous libldetect was requiring file /usr/share/pci.ids, hence a urpmi issue (cf #29299)
Conflicts:	%{mklibname ldetect 0.7} < 0.7.0-5

%description
This package contains various utilities for inspecting and setting
devices connected to the PCI bus. 

%package -n	%{libname}
Summary:	The PCI library
Group:		System/Libraries

%description -n	%{libname}
This package contains a dynamic library for inspecting and setting
devices connected to the PCI bus.

%package -n	uclibc-%{libname}
Summary:	uClibc linked version of the PCI library
Group:		System/Libraries

%description -n	uclibc-%{libname}
This package contains a dynamic uClibc linked library for inspecting and setting
devices connected to the PCI bus.

%package -n	%{devname}
Summary:	Linux PCI development library
Group:		Development/C
Requires:	%{libname} = %{version}-%{release}
%if %{with uclibc}
Requires:	uclibc-%{libname} = %{version}-%{release}
%endif
Provides:	pciutils-devel = %{version}-%{release}

%description -n	%{devname}
This package contains a library for inspecting and setting
devices connected to the PCI bus.

%prep
%setup -q
%patch0 -p0
%patch10 -p1
%patch11 -p0
%patch20 -p1
%patch21 -p1
%patch22 -p1

%patch102 -p1 -b .scan~
%patch103 -p1 -b .pread~
%patch108 -p1 -b .multilib~
%patch110 -p1 -b .sparc~
%patch111 -p1 -b .superh~
%patch112 -p1 -b .arm~
%patch113 -p1 -b .keep_static~

%build
sed -e 's|^SRC=.*|SRC="http://pciids.sourceforge.net/pci.ids"|' -i update-pciids.sh

%if %{with diet}
%make PREFIX=%{_prefix} ZLIB=no OPT="-Os -D__USE_DIETLIBC" LDFLAGS="%{ldflags}" CC="diet gcc" DNS=no lib/libpci.a
mkdir -p dietlibc
mv lib/libpci.a dietlibc/libpci.a
make clean
%endif

%if %{with uclibc}
%make PREFIX=%{_prefix} ZLIB=no OPT="%{uclibc_cflags}" LDFLAGS="%{ldflags}" CC="%{uclibc_cc}" DNS=no lib/libpci.a
mkdir -p uclibc
mv lib/libpci.a uclibc/libpci.a
make clean
%make PREFIX=%{_prefix} ZLIB=no OPT="%{uclibc_cflags}" SHARED=yes LDFLAGS="%{ldflags} -Wl,-O2" CC="%{uclibc_cc}" DNS=no
mv lib/libpci.so.%{major}* uclibc
make clean
%endif

%make PREFIX=%{_prefix} OPT="%{optflags} -fPIC" ZLIB=no SHARED=no DNS=no LDFLAGS="%{ldflags}" lib/libpci.a 
mkdir -p glibc
mv lib/libpci.a glibc/libpci.a
make clean

# do not build with zlib support since it's useless (only needed if we compress
# pci.ids which we cannot do since hal mmaps it for memory saving reason)
%make PREFIX=%{_prefix} OPT="%{optflags} -fPIC" ZLIB=no SHARED=yes LDFLAGS="%{ldflags}"
mv lib/libpci.so.%{major}* glibc


%install
install -d %{buildroot}{%{_bindir},%{_mandir}/man8,%{_libdir}/pkgconfig,%{_includedir}/pci}

install pcimodules lspci setpci %{buildroot}%{_bindir}
install -m644 pcimodules.man lspci.8 setpci.8 %{buildroot}%{_mandir}/man8
install -m644 glibc/libpci.a -D %{buildroot}%{_libdir}/libpci.a
install -m755 glibc/libpci.so.%{major}.* %{buildroot}%{_libdir}
ln -s libpci.so.%{major} %{buildroot}%{_libdir}/libpci.so
%if %{with diet}
install -m644 dietlibc/libpci.a -D %{buildroot}%{_prefix}/lib/dietlibc/lib-%{_arch}/libpci.a
%endif
%if %{with uclibc}
install -m644 uclibc/libpci.a -D %{buildroot}%{uclibc_root}%{_libdir}/libpci.a
install -m755 uclibc/libpci.so.%{major}.* %{buildroot}%{uclibc_root}%{_libdir}
ln -s libpci.so.%{major} %{buildroot}%{uclibc_root}%{_libdir}/libpci.so
%endif

install -m 644 lib/{pci.h,header.h,config.h,types.h} %{buildroot}%{_includedir}/pci
install -m 755 update-pciids.sh %{buildroot}%{_bindir}/
install -m 644 lib/libpci.pc %{buildroot}%{_libdir}/pkgconfig/

%files
%doc README ChangeLog pciutils.lsm
%{_mandir}/man8/*
%{_bindir}/lspci
%{_bindir}/pcimodules
%{_bindir}/setpci

%files -n %{libname}
%{_libdir}/*.so.%{major}*

%if %{with uclibc}
%files -n uclibc-%{libname}
%{uclibc_root}%{_libdir}/*.so.%{major}*
%endif

%files -n %{devname}
%doc TODO
%{_bindir}/update-pciids.sh
%{_libdir}/*.a
%{_libdir}/*.so
%if %{with diet}
%{_prefix}/lib/dietlibc/lib-%{_arch}/libpci.a
%endif
%if %{with uclibc}
%{uclibc_root}%{_libdir}/libpci.a
%{uclibc_root}%{_libdir}/libpci.so
%endif
%dir %{_includedir}/pci
%{_includedir}/pci/*.h
%{_libdir}/pkgconfig/libpci.pc

%changelog
* Tue Dec 12 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 3.1.10-4
- rebuild on ABF

* Mon Oct 29 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 3.1.10-3
+ Revision: 820471
- add missing dependency on uclibc library for devel package

* Fri Sep 21 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 3.1.10-2
+ Revision: 817241
- do dynamcally linked uClibc build

* Sun Jul 01 2012 Tomasz Pawel Gajc <tpg@mandriva.org> 3.1.10-1
+ Revision: 807689
- rediff patch 22
- update to new version 3.1.10

* Tue May 22 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 3.1.9-4
+ Revision: 800057
- disable dns query support for diet & uclibc builds
- do diet & uclibc builds with %%ldflags
- build against uClibc 0.9.33
- update url

* Tue May 08 2012 Franck Bui <franck.bui@mandriva.com> 3.1.9-3
+ Revision: 797455
- pci-devel has to provide pciutils-devel
  and there's no point in providing again pci-devel, so I assumed
  the previous commit dropped wrongly pciutils-devel.

* Wed Mar 07 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 3.1.9-2
+ Revision: 782660
- drop excessive provides
- cleanups

* Mon Jan 30 2012 Tomasz Pawel Gajc <tpg@mandriva.org> 3.1.9-1
+ Revision: 769930
- update to new version 3.1.9

* Mon Nov 07 2011 Tomasz Pawel Gajc <tpg@mandriva.org> 3.1.8-1
+ Revision: 728329
- update to new version 3.1.8
- drop patches 101, 106 and 109
- rediff patches 22 and 112

* Sat Oct 29 2011 Matthew Dawkins <mattydaw@mandriva.org> 3.1.7-8
+ Revision: 707821
- ship pkgconfig file

* Mon Aug 22 2011 Lonyai Gergely <aleph@mandriva.org> 3.1.7-7
+ Revision: 696122
- Add the pciutils-devel to obsolotes.

* Sat Jul 16 2011 Lonyai Gergely <aleph@mandriva.org> 3.1.7-6
+ Revision: 690121
- rebuild

* Sun May 29 2011 Matthew Dawkins <mattydaw@mandriva.org> 3.1.7-5
+ Revision: 681725
- changed buildwith diet to bcond
- renamed devel pkg to libpci-devel

* Wed May 04 2011 Oden Eriksson <oeriksson@mandriva.com> 3.1.7-4
+ Revision: 666999
- mass rebuild

* Fri Dec 03 2010 Oden Eriksson <oeriksson@mandriva.com> 3.1.7-3mdv2011.0
+ Revision: 607082
- rebuild

* Wed Mar 17 2010 Thierry Vignaud <tv@mandriva.org> 3.1.7-2mdv2010.1
+ Revision: 523759
- build diet lib by default (needed by installer's stage1)

* Fri Feb 12 2010 Frederik Himpe <fhimpe@mandriva.org> 3.1.7-1mdv2010.1
+ Revision: 505082
- update to new version 3.1.7
- Update to new version 3.1.7
- Rediff LDFLAGS patch

* Mon Jan 25 2010 Frederik Himpe <fhimpe@mandriva.org> 3.1.6-1mdv2010.1
+ Revision: 496346
- Update to new version 3.1.6
- Rediff LDFLAGS patch

* Tue Jan 19 2010 Frederik Himpe <fhimpe@mandriva.org> 3.1.5-1mdv2010.1
+ Revision: 493771
- Update to new version 3.1.5
- capabilities freeing fix integrated upstream
- Rediff ldflags patch

  + Per Øyvind Karlsen <peroyvind@mandriva.org>
    - add support for building against uclibc

* Tue Dec 15 2009 Eugeni Dodonov <eugeni@mandriva.com> 3.1.4-6mdv2010.1
+ Revision: 479071
- Do not search for pci.ids in /usr/share/hwdata/pci.ids, as it is not there.

* Mon Dec 14 2009 Per Øyvind Karlsen <peroyvind@mandriva.org> 3.1.4-5mdv2010.1
+ Revision: 478486
- disable changing of pci.ids path (P106),release was submitted a bit prematurely

* Sat Dec 05 2009 Per Øyvind Karlsen <peroyvind@mandriva.org> 3.1.4-4mdv2010.1
+ Revision: 473685
- sync with fedora patches:
        o truncate too long names (P101, rhbz #205948)
        o don't segfault on systems without PCI bus (P102, rhbz #84146)
        o use pread/pwrite, ifdef check is obsolete nowadays (P103, alters P20)
        o change pci.ids directory to hwdata (P106)
        o multilib support (P106, replacing %%multiarch voodoo)
        o add support for directory with another pci.ids (P109)
        o add support for sparc, sh & arm (P110, 111 & P112)
- correct license

* Wed Sep 30 2009 Thierry Vignaud <tv@mandriva.org> 3.1.4-3mdv2010.0
+ Revision: 451197
- patche 100: backport crash fix when using PCI_FILL_CAPS
- drop BuildConflicts on zlib-devel (useless with current build options)

* Sun Sep 27 2009 Olivier Blin <blino@mandriva.org> 3.1.4-2mdv2010.0
+ Revision: 450240
- add bootstrap flag: pciutils needs pciids to be installed and to
  build pciids, one needs pciutils (from Arnaud Patard)

* Fri Aug 14 2009 Frederik Himpe <fhimpe@mandriva.org> 3.1.4-1mdv2010.0
+ Revision: 416384
- Update to new version 3.1.4
- Rediff LDFLAGS patch

* Mon Jul 06 2009 Frederik Himpe <fhimpe@mandriva.org> 3.1.3-1mdv2010.0
+ Revision: 392686
- Update to new version 3.1.3
- Rediff LDFLAGS patch

* Tue Feb 10 2009 Tomasz Pawel Gajc <tpg@mandriva.org> 3.1.2-1mdv2009.1
+ Revision: 339077
- update to new version 3.1.2
- rediff patches 10 and 22
- spec file clean

* Wed Feb 04 2009 Pascal Terjan <pterjan@mandriva.org> 3.0.3-2mdv2009.1
+ Revision: 337437
- Disable support for network fetching of pci.ids in static libpci

* Thu Jan 08 2009 Thierry Vignaud <tv@mandriva.org> 3.0.3-1mdv2009.1
+ Revision: 327278
- new release
- rediff patches

* Thu Dec 25 2008 Oden Eriksson <oeriksson@mandriva.com> 3.0.0-7mdv2009.1
+ Revision: 319062
- rediffed some fuzzy patches
- use %%ldflags

* Thu Aug 07 2008 Thierry Vignaud <tv@mandriva.org> 3.0.0-6mdv2009.0
+ Revision: 265335
- rebuild early 2009.0 package (before pixel changes)

* Tue Jun 10 2008 Oden Eriksson <oeriksson@mandriva.com> 3.0.0-5mdv2009.0
+ Revision: 217579
- rebuilt against dietlibc-devel-0.32

* Tue Jun 10 2008 Thierry Vignaud <tv@mandriva.org> 3.0.0-4mdv2009.0
+ Revision: 217497
- make devel package require library (thus fixing linking of library users)
- remove kernel require from description

  + Pixel <pixel@mandriva.com>
    - do not call ldconfig in %%post/%%postun, it is now handled by filetriggers

* Wed May 21 2008 Thierry Vignaud <tv@mandriva.org> 3.0.0-3mdv2009.0
+ Revision: 209756
- rebuild with gcc-4.3

* Wed May 14 2008 Thierry Vignaud <tv@mandriva.org> 3.0.0-2mdv2009.0
+ Revision: 207184
- provide .so link for linking

* Wed May 14 2008 Thierry Vignaud <tv@mandriva.org> 3.0.0-1mdv2009.0
+ Revision: 206969
- enable dynamic library
- patch 21: allow build with dietlibc, not using unsupported __res_state.res_h_errno feature
- typo fix
- new release
- rediff pcimodules patch

* Wed Jan 02 2008 Thierry Vignaud <tv@mandriva.org> 2.2.9-1mdv2008.1
+ Revision: 140541
- new release
- kill re-definition of %%buildroot on Pixel's request

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

* Wed Aug 15 2007 Olivier Blin <blino@mandriva.org> 2.2.6-3mdv2008.0
+ Revision: 63511
- build dietlibc library with -Os

* Tue Aug 14 2007 Olivier Blin <blino@mandriva.org> 2.2.6-2mdv2008.0
+ Revision: 63367
- build dietlibc static library
- add patch to be able to build with dietlibc

  + Thierry Vignaud <tv@mandriva.org>
    - add a note asking for rebuilding ldetect on update

* Wed Jun 27 2007 Thierry Vignaud <tv@mandriva.org> 2.2.6-1mdv2008.0
+ Revision: 45028
- new release

  + Pixel <pixel@mandriva.com>
    - replace BuildConflicts on zlib-devel with flag ZLIB=no

* Mon May 14 2007 Thierry Vignaud <tv@mandriva.org> 2.2.4-12mdv2008.0
+ Revision: 26643
- build w/ozlib support since it's useless

* Mon May 07 2007 Per Øyvind Karlsen <peroyvind@mandriva.org> 2.2.4-11mdv2008.0
+ Revision: 23932
- add zlib-devel to buildrequires to ensure building with zlib support
- do not strip binaries with 'install', otherwise rpm won't be able to create -debug package
- do parallell build


* Fri Mar 09 2007 Pixel <pixel@mandriva.com> 2.2.4-10mdv2007.1
+ Revision: 138807
- add a conflict to help workaround urpmi #29299
  (the other part of the fix is libldetect 0.7.0-5mdv now requiring pciids directly)
- don't requires kernel
  (it was meant to be a conflict, and conflicting on kernel < 2.1.82 is
  useless nowadays)
- requires pciids (otherwise lspci will fail)
- remove BuildRequires needed by update-pciids
  (since it is called in pciids now)
- remove pciutils-devel requiring pciutils, it's useless and help breaking the
  loop below:
- move update-pciids.sh inside pciutils-devel
  (it's a little ugly, but it allows pciids to buildrequire pciutils-devel
  without introducing a loop (when bootstrapping distro))

* Thu Mar 08 2007 Thierry Vignaud <tvignaud@mandriva.com> 2.2.4-8mdv2007.1
+ Revision: 138536
- package update-pciids.sh (for pciids package)
- stop packaging pci.ids (now in pciids package)

* Thu Mar 08 2007 Thierry Vignaud <tvignaud@mandriva.com> 2.2.4-7mdv2007.1
+ Revision: 138525
- reenable updating pci.ids

* Mon Feb 26 2007 Thierry Vignaud <tvignaud@mandriva.com> 2.2.4-6mdv2007.1
+ Revision: 125875
- bump release

* Mon Feb 26 2007 Thierry Vignaud <tvignaud@mandriva.com> 2.2.4-4mdv2007.1
+ Revision: 125855
- bump release
- fix library on x86_64

* Fri Feb 23 2007 Thierry Vignaud <tvignaud@mandriva.com> 2.2.4-3mdv2007.1
+ Revision: 124846
- rebuild in order to update pci.ids
- buildrequire curl for update-pciids.sh

* Fri Jan 26 2007 Thierry Vignaud <tvignaud@mandriva.com> 2.2.4-2mdv2007.1
+ Revision: 113897
- update pci.ids

* Fri Nov 24 2006 Pixel <pixel@mandriva.com> 2.2.4-1mdv2007.1
+ Revision: 86875
- new release
- adapt patch10
- add /usr/include/multiarch-i386-linux/pci to file list (what's this?)
- Import pciutils

* Fri Jun 23 2006 Pixel <pixel@mandriva.com> 2.2.3-1mdv2007.0
- new release

* Mon Jan 09 2006 Pixel <pixel@mandriva.com> 2.2.1-3mdk
- use uint* & stdin.h instead of u_int* & sys/types.h
  (u_int* is not available in diet libc)

* Thu Jan 05 2006 Pixel <pixel@mandriva.com> 2.2.1-2mdk
- types.h is needed in pciutils-devel

* Sun Dec 18 2005 Pixel <pixel@mandriva.com> 2.2.1-1mdk
- new release
- update pci.ids
- redo patch11, patch10
- drop patch1, patch12 (applied upstream)
- drop patch13 (seems to be useless)

* Mon Dec 12 2005 Thierry Vignaud <tvignaud@mandriva.com> 2.1.11-21mdk
- update pci.ids

* Thu Nov 24 2005 Thierry Vignaud <tvignaud@mandriva.com> 2.1.11-20mdk
- update pci.ids

* Mon Nov 07 2005 Thierry Vignaud <tvignaud@mandriva.com> 2.1.11-19mdk
- update pci.ids

* Wed Oct 19 2005 Thierry Vignaud <tvignaud@mandriva.com> 2.1.11-18mdk
- update pci.ids

* Wed Sep 07 2005 Thierry Vignaud <tvignaud@mandriva.com> 2.1.11-17mdk
- update pci.ids

* Fri Aug 26 2005 Thierry Vignaud <tvignaud@mandriva.com> 2.1.11-16mdk
- update pci.ids

* Sat Jun 25 2005 Thierry Vignaud <tvignaud@mandrakesoft.com> 2.1.11-15mdk
- update pci.ids

* Wed May 25 2005 Thierry Vignaud <tvignaud@mandrakesoft.com> 2.1.11-14mdk
- update pci.ids

* Sat May 14 2005 Thierry Vignaud <tvignaud@mandrakesoft.com> 2.1.11-13mdk
- update pci.ids

* Tue May 10 2005 Thierry Vignaud <tvignaud@mandrakesoft.com> 2.1.11-12mdk
- update pci.ids

* Tue Apr 26 2005 Thierry Vignaud <tvignaud@mandrakesoft.com> 2.1.11-11mdk
- update pci.ids

* Tue Mar 08 2005 Thierry Vignaud <tvignaud@mandrakesoft.com> 2.1.11-10mdk
- update pci.ids

* Tue Feb 08 2005 Thierry Vignaud <tvignaud@mandrakesoft.com> 2.1.11-9mdk
- update pci.ids

* Fri Jan 21 2005 Gwenole Beauchesne <gbeauchesne@mandrakesoft.com> 2.1.11-8mdk
- multiarch capable

* Thu Dec 02 2004 Thierry Vignaud <tvignaud@mandrakesoft.com> 2.1.11-7mdk
- update pci.ids

* Wed Aug 04 2004 Thierry Vignaud <tvignaud@mandrakesoft.com> 2.1.11-6mdk
- update pci.ids

* Sat Jul 24 2004 Per Øyvind Karlsen <peroyvind@linux-mandrake.com> 2.1.11-5mdk
- rebuild (to update pciids)
- cosmetics
