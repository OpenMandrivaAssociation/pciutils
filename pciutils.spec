# when updating, please rebuild ldetect as it is compiled against this static library

%bcond_with	bootstrap
%bcond_without	diet
%bcond_without	uclibc

%define	major	3
%define	libname	%mklibname pci %{major}
%define	devname	%mklibname pci -d

Summary:	PCI bus related utilities
Name:		pciutils
Version:	3.1.9
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
Patch22:	pciutils-3.1.8-LDFLAGS.patch

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

%if !%{with bootstrap}
Requires:	pciids
%endif
%if %{with diet}
BuildRequires:	dietlibc-devel
%endif
%if %{with uclibc}
BuildRequires:	uClibc-devel >= 0.9.33.2
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

%package -n	%{devname}
Summary:	Linux PCI development library
Group:		Development/C
Requires:	%{libname}  = %{version}-%{release}
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

%build
sed -e 's|^SRC=.*|SRC="http://pciids.sourceforge.net/pci.ids"|' -i update-pciids.sh

%if %{with diet}
%make PREFIX=%{_prefix} ZLIB=no OPT="-Os -D__USE_DIETLIBC" CC="diet gcc" lib/libpci.a
cp lib/libpci.a libpci.a.diet
make clean
%endif
%if %{with uclibc}
%make PREFIX=%{_prefix} ZLIB=no OPT="%{uclibc_cflags}" CC="%{uclibc_cc}" lib/libpci.a
cp lib/libpci.a libpci.a.uclibc
make clean
%endif

%make PREFIX=%{_prefix} OPT="%{optflags} -fPIC" ZLIB=no SHARED=no DNS=no LDFLAGS="%{ldflags}" lib/libpci.a 
cp lib/libpci.a lib/libpci.a.libc
make clean

# do not build with zlib support since it's useless (only needed if we compress
# pci.ids which we cannot do since hal mmaps it for memory saving reason)
%make PREFIX=%{_prefix} OPT="%{optflags} -fPIC" ZLIB=no SHARED=yes LDFLAGS="%{ldflags}"

%install
install -d %{buildroot}{%{_bindir},%{_mandir}/man8,%{_libdir}/pkgconfig,%{_includedir}/pci}

install pcimodules lspci setpci %{buildroot}%{_bindir}
install -m 644 pcimodules.man lspci.8 setpci.8 %{buildroot}%{_mandir}/man8
install -m 644 lib/libpci.a.libc %{buildroot}%{_libdir}/libpci.a
install lib/libpci.so.%{major}.* %{buildroot}%{_libdir}
ln -s libpci.so.3 %{buildroot}%{_libdir}/libpci.so
%if %{with diet}
install -m644 libpci.a.diet -D %{buildroot}%{_prefix}/lib/dietlibc/lib-%{_arch}/libpci.a
%endif
%if %{with uclibc}
install -m644 libpci.a.uclibc -D %{buildroot}%{uclibc_root}%{_libdir}/libpci.a
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
%endif
%dir %{_includedir}/pci
%{_includedir}/pci/*.h
%{_libdir}/pkgconfig/libpci.pc
