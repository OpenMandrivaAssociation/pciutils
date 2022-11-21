%bcond_with bootstrap

%define major 3
%define libname %mklibname pci %{major}
%define devname %mklibname pci -d

Summary:	PCI bus related utilities
Name:		pciutils
Version:	3.9.0
Release:	1
License:	GPLv2+
Group:		System/Kernel and hardware
Url:		https://mj.ucw.cz/sw/pciutils/
Source0:	https://mj.ucw.cz/download/linux/pci/%{name}-%{version}.tar.gz
Patch10:	pciutils-3.3.1-pcimodules.patch
Patch11:	pciutils-3.0.3-cardbus-only-when-root.patch
# Fedora patches
# don't segfault on systems without PCI bus (rhbz #84146)
Patch102:	pciutils-2.1.10-scan.patch
# platform support 3x
Patch113:	pciutils-3.1.10-dont-remove-static-libraries.patch

# change pci.ids directory to hwdata, fedora/rhel specific
Patch150:	https://src.fedoraproject.org/rpms/pciutils/raw/rawhide/f/pciutils-2.2.1-idpath.patch
# add support for directory with another pci.ids, rejected by upstream, rhbz#195327
Patch151:	https://src.fedoraproject.org/rpms/pciutils/raw/rawhide/f/pciutils-dir-d.patch

# (tpg) add explicit requires on libname
Requires:	%{libname} = %{EVRD}
%if !%{with bootstrap}
Requires:	hwdata >= 0.314
%endif
BuildRequires:	pkgconfig(libudev)
BuildRequires:	pkgconfig(libkmod)
#- previous libldetect was requiring file /usr/share/pci.ids, hence a urpmi issue (cf #29299)
Conflicts:	%{mklibname ldetect 0.7} < 0.7.0-5
Provides:	/sbin/lspci
Provides:	/sbin/setpci

%description
This package contains various utilities for inspecting and setting
devices connected to the PCI bus.

%package -n %{libname}
Summary:	The PCI library
Group:		System/Libraries

%description -n %{libname}
This package contains a dynamic library for inspecting and setting
devices connected to the PCI bus.

%package -n %{devname}
Summary:	Linux PCI development library
Group:		Development/C
Requires:	%{libname} = %{EVRD}
Provides:	pciutils-devel = %{EVRD}

%description -n %{devname}
This package contains a library for inspecting and setting
devices connected to the PCI bus.

%prep
%autosetup -p1

%build
# (tpg) set right URL for pci.ids file
sed -e 's|^SRC=.*|SRC="https://pci-ids.ucw.cz/v2.2/pci.ids"|' -i update-pciids.sh

# build static lib
%make_build CC=%{__cc} SHARED="no" ZLIB="no" LIBKMOD="yes" DNS="no" STRIP="" OPT="%{optflags} -fPIC" LDFLAGS="%{build_ldflags}" PREFIX="%{_prefix}" LIBDIR="%{_libdir}" IDSDIR="%{_datadir}/hwdata" PCI_IDS="pci.ids" lib/libpci.a
cp lib/libpci.a lib/libpci.a.libc
make clean CC=%{__cc}

# build shared lib
# do not build with zlib support since it's useless (only needed if we compress
%make_build CC=%{__cc} SHARED="yes" ZLIB="no" LIBKMOD="yes" HWDB="yes" DNS="no" STRIP="" OPT="%{optflags} -fPIC" LDFLAGS="%{build_ldflags}" PREFIX="%{_prefix}" LIBDIR="%{_libdir}" IDSDIR="%{_datadir}/hwdata" PCI_IDS="pci.ids"

# fix lib vs. lib64 in libpci.pc (static Makefile is used)
sed -i "s|^libdir=.*$|libdir=%{_libdir}|" lib/libpci.pc

%install
install -d %{buildroot}{%{_bindir},%{_sbindir},%{_mandir}/man8,%{_libdir}/pkgconfig,%{_includedir}/pci}

install pcimodules lspci setpci %{buildroot}%{_bindir}
install -m644 pcimodules.man lspci.8 setpci.8 %{buildroot}%{_mandir}/man8
install -m644 lib/libpci.a.libc -D %{buildroot}%{_libdir}/libpci.a
install -m755 lib/libpci.so.%{major}.* %{buildroot}%{_libdir}
ln -s libpci.so.%{major} %{buildroot}%{_libdir}/libpci.so

install -m 644 lib/{pci.h,header.h,config.h,types.h} %{buildroot}%{_includedir}/pci
install -m 755 update-pciids.sh %{buildroot}%{_sbindir}/
install -m 644 lib/libpci.pc %{buildroot}%{_libdir}/pkgconfig/

%files
%doc README pciutils.lsm
%doc %{_mandir}/man8/*
%{_sbindir}/update-pciids.sh
%{_bindir}/lspci
%{_bindir}/pcimodules
%{_bindir}/setpci

%files -n %{libname}
%{_libdir}/*.so.%{major}*

%files -n %{devname}
%doc TODO
%{_libdir}/*.a
%{_libdir}/*.so
%dir %{_includedir}/pci
%{_includedir}/pci/*.h
%{_libdir}/pkgconfig/libpci.pc
