# when updating, please rebuild ldetect as it is compiled against this static library

%define build_diet 1

Name:		pciutils
Version:	3.0.0
Release:	%mkrel 1
Source0:	ftp://atrey.karlin.mff.cuni.cz/pub/linux/pci/%{name}-%{version}.tar.bz2
URL:		http://atrey.karlin.mff.cuni.cz/~mj/pciutils.html
Patch0: 	pciutils-2.2.1-use-stdint.patch
Patch10:	pciutils-3.0.0-pcimodules.patch
Patch11:	pciutils-2.2.1-cardbus-only-when-root.patch
# allow build with dietlibc, using sycall() and sys/io.h
Patch20:	pciutils-2.2.6-noglibc.patch
# allow build with dietlibc, not using unsupported features:
Patch21:	pciutils-3.0.0-fix-compiliing-w-diet.patch
License:	GPL
Buildroot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
Requires:	pciids
%if %{build_diet}
BuildRequires: dietlibc-devel
%endif
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
%patch20 -p1
%patch21 -p1

%build
%if %{build_diet}
%make PREFIX=%{_prefix} ZLIB=no OPT="-Os -D__USE_DIETLIBC" CC="diet gcc" lib/libpci.a
cp lib/libpci.a libpci.a.diet
make clean
%endif

# do not build with zlib support since it's useless (only needed if we compress
# pci.ids which we cannot do since hal mmaps it for memory saving reason)
%make PREFIX=%{_prefix} OPT="$RPM_OPT_FLAGS -fPIC" ZLIB=no

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%_bindir,%_mandir/man8,%_libdir,%_includedir/pci}

install pcimodules lspci setpci $RPM_BUILD_ROOT%_bindir
install -m 644 pcimodules.man lspci.8 setpci.8 $RPM_BUILD_ROOT%_mandir/man8
install -m 644 lib/libpci.a $RPM_BUILD_ROOT%_libdir
%if %{build_diet}
install -d $RPM_BUILD_ROOT%{_prefix}/lib/dietlibc/lib-%{_arch}
install libpci.a.diet $RPM_BUILD_ROOT%{_prefix}/lib/dietlibc/lib-%{_arch}/libpci.a
%endif

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
%if %{build_diet}
%{_prefix}/lib/dietlibc/lib-%{_arch}/libpci.a
%endif
%{_includedir}/pci
%{_includedir}/*/pci
%multiarch %{_includedir}/multiarch-*/pci/config.h


