Name:		pciutils
Version:	2.2.4
Release:	%mkrel 12
Source0:	ftp://atrey.karlin.mff.cuni.cz/pub/linux/pci/%{name}-%{version}.tar.bz2
URL:		http://atrey.karlin.mff.cuni.cz/~mj/pciutils.html
Patch0: 	pciutils-2.2.1-use-stdint.patch
Patch10:	pciutils-2.2.4-pcimodules.patch
Patch11:	pciutils-2.2.1-cardbus-only-when-root.patch
License:	GPL
Buildroot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
Requires:	pciids
#- previous libldetect was requiring file /usr/share/pci.ids, hence a urpmi issue (cf #29299)
Conflicts:	%{mklibname ldetect 0.7} < 0.7.0-5mdv2007.1
Summary:	PCI bus related utilities
Group:		System/Kernel and hardware

%description
This package contains various utilities for inspecting and setting
devices connected to the PCI bus. The utilities provided require
kernel version 2.1.82 or newer (supporting the /proc/bus/pci
interface).

%package	devel
Summary:	Linux PCI development library
Group:		Development/C

%description	devel
This package contains a library for inspecting and setting
devices connected to the PCI bus.

%prep
%setup -q
%patch0 -p1
%patch11 -p1
%patch10 -p1

%build
# do not build with zlib support since it's useless (only needed if we compress
# pci.ids which we cannot do since hal mmaps it for memory saving reason)
%make PREFIX=%{_prefix} OPT="$RPM_OPT_FLAGS -fPIC" ZLIB=no

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%_bindir,%_mandir/man8,%_libdir,%_includedir/pci}

install pcimodules lspci setpci $RPM_BUILD_ROOT%_bindir
install -m 644 pcimodules.man lspci.8 setpci.8 $RPM_BUILD_ROOT%_mandir/man8
install -m 644 lib/libpci.a $RPM_BUILD_ROOT%_libdir
install -m 644 lib/{pci.h,header.h,config.h,types.h} $RPM_BUILD_ROOT%_includedir/pci
install -m 755 update-pciids.sh $RPM_BUILD_ROOT%_bindir/

%multiarch_includes $RPM_BUILD_ROOT%{_includedir}/pci/config.h

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-, root, root)
%doc README ChangeLog pciutils.lsm
%{_mandir}/man8/*
%{_bindir}/lspci
%{_bindir}/pcimodules
%{_bindir}/setpci


%files devel
%defattr(-, root, root)
%doc TODO
%{_bindir}/update-pciids.sh
%{_libdir}/*.a
%{_includedir}/pci
%{_includedir}/*/pci
%multiarch %{_includedir}/multiarch-*/pci/config.h


