# This .spec file is targeted for SuSE OBS. It relies on macro that
# are not available on regular distributions. If you use directly
# rpmbuild, be sure to use something like `--define 'rhel_version
# 700'`.

# Conditional build options, disable with "--without xxx"
%bcond_without xml
%bcond_without cdp
%bcond_without edp
%bcond_without sonmp
%bcond_without fdp
%bcond_without lldpmed
%bcond_without dot1
%bcond_without dot3
%bcond_without custom
%bcond_without snmp
%bcond_with json

# On RHEL <= 6, compile with oldies
# For SuSE, SLE11 with a recent SP comes with 3.0. SLE12 comes with 3.12.
%if 0%{?rhel_version} > 0 && 0%{?rhel_version} < 700 || 0%{?centos_version} > 0 && 0%{?centos_version} < 700
%bcond_without oldies
%else
%bcond_with oldies
%endif

# On RHEL < 7, disable systemd
# On SuSE < 12, disable systemd
%if 0%{?rhel_version} > 0 && 0%{?rhel_version} < 700 || 0%{?centos_version} > 0 && 0%{?centos_version} < 700 || 0%{?suse_version} > 0 && 0%{?suse_version} < 1200
%bcond_with systemd
%else
%bcond_without systemd
%endif

# On RHEL < 7, use embedded libevent
%if 0%{?rhel_version} > 0 && 0%{?rhel_version} < 700 || 0%{?centos_version} > 0 && 0%{?centos_version} < 700 || 0%{?suse_version} > 0 && 0%{?suse_version} < 1200
%bcond_with system_libevent
%else
%bcond_without system_libevent
%endif

%define lldpd_user lldpd
%define lldpd_group lldpd
%define lldpd_chroot /var/run/lldpd
%define lldpd_ctl_socket /var/run/lldpd/lldpd.socket
%define lldpd_pid_file /var/run/lldpd/lldpd.pid

Summary: Implementation of IEEE 802.1ab (LLDP)
Name: lldpd
Version: 0.9.0
Release: 0%{?_tis_dist}.%{tis_patch_ver}
License: MIT
Group: System/Management
URL: http://vincentbernat.github.com/lldpd/
Source0: http://media.luffy.cx/files/lldpd/%{name}-%{version}.tar.gz
Source1: lldpd.init%{?suse_version:.suse}
# Source2: lldpd.sysconfig
Source3: lldpd.default
Source4: i40e-lldp-configure.sh

Patch0: lldpd-interface-show.patch
Patch1: lldpd-create-run-dir.patch
Patch2: lldpd-i40e-disable.patch
Patch3: lldpd-clear-station.patch

BuildRequires: pkgconfig
%if %{with system_libevent}
BuildRequires: libevent-devel
%endif
BuildRequires: readline-devel
%if %{with snmp}
BuildRequires: net-snmp-devel
BuildRequires: openssl-devel
%{!?suse_version:BuildRequires: lm_sensors-devel}
%endif
%if %{with xml}
BuildRequires: libxml2-devel
%endif

BuildRequires: json-c-devel
BuildRequires: pciutils-devel

%if %{with systemd}
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
BuildRequires: systemd
BuildRequires: systemd-devel
BuildRequires: systemd-units
%endif
%if 0%{?suse_version}
PreReq: %fillup_prereq %insserv_prereq pwdutils
%else
Requires(pre): /usr/sbin/groupadd /usr/sbin/useradd
Requires(post): chkconfig
Requires(preun): chkconfig
Requires(preun): initscripts
Requires(postun): initscripts
%endif

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}

%description
This implementation provides LLDP sending and reception, supports VLAN
and includes an SNMP subagent that can interface to an SNMP agent
through AgentX protocol.

LLDP is an industry standard protocol designed to supplant proprietary
Link-Layer protocols such as Extreme EDP (Extreme Discovery Protocol)
and CDP (Cisco Discovery Protocol). The goal of LLDP is to provide an
inter-vendor compatible mechanism to deliver Link-Layer notifications
to adjacent network devices.

This daemon is also able to deal with CDP, FDP, SONMP and EDP
protocol. It also handles LLDP-MED extension.

%package devel
Summary:  Implementation of IEEE 802.1ab - Tools and header files for developers
Group:    Development/Libraries/C
BuildRequires: pkgconfig
Requires: lldpd = %{version}-%{release}

%description devel
This package is required to develop alternate clients for lldpd.

LLDP is an industry standard protocol designed to supplant proprietary
Link-Layer protocols such as Extreme EDP (Extreme Discovery Protocol)
and CDP (Cisco Discovery Protocol). The goal of LLDP is to provide an
inter-vendor compatible mechanism to deliver Link-Layer notifications
to adjacent network devices.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1


%build
%configure \
%if %{with snmp}
   --with-snmp \
%endif
%if %{with xml}
   --with-xml \
%endif
%if %{with cdp}
   --enable-cdp \
%else
   --disable-cdp \
%endif
%if %{with edp}
   --enable-edp \
%else
   --disable-edp \
%endif
%if %{with sonmp}
   --enable-sonmp \
%else
   --disable-sonmp \
%endif
%if %{with fdp}
   --enable-fdp \
%else
   --disable-fdp \
%endif
%if %{with lldpmed}
   --enable-lldpmed \
%else
   --disable-lldpmed \
%endif
%if %{with dot1}
   --enable-dot1 \
%else
   --disable-dot1 \
%endif
%if %{with dot3}
   --enable-dot3 \
%else
   --disable-dot3 \
%endif
%if %{with custom}
   --enable-custom \
%else
   --disable-custom \
%endif
%if %{with oldies}
   --enable-oldies \
%else
   --disable-oldies \
%endif
   --with-privsep-user=%lldpd_user \
   --with-privsep-group=%lldpd_group \
   --with-privsep-chroot=%lldpd_chroot \
%if %{without systemd}
   --with-systemdsystemunitdir=no \
%endif
   --with-sysusersdir=no \
   --prefix=%{_usr} \
   --localstatedir=%{_localstatedir} \
   --sysconfdir=%{_sysconfdir} \
   --libdir=%{_libdir} \
   --docdir=%{_docdir}/lldpd \
   --enable-pie \
   --with-lldpd-ctl-socket=%lldpd_ctl_socket \
   --with-lldpd-pid-file=%lldpd_pid_file

[ -f %{_includedir}/net-snmp/agent/struct.h ] || touch src/struct.h
make %{?_smp_mflags}

%install
make install DESTDIR=$RPM_BUILD_ROOT
%if %{without systemd}
install -d $RPM_BUILD_ROOT/%{_initrddir}
install -m755 %{SOURCE1} $RPM_BUILD_ROOT/%{_initrddir}/lldpd
%endif
# %if 0%{?suse_version}
# mkdir -p ${RPM_BUILD_ROOT}/var/adm/fillup-templates
# install -m700 %{SOURCE2} ${RPM_BUILD_ROOT}/var/adm/fillup-templates/sysconfig.lldpd
# %else
# install -d $RPM_BUILD_ROOT/etc/sysconfig
# install -m644 %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/lldpd
# %endif

install -Dm 0644 %{SOURCE3} %{buildroot}%{_sysconfdir}/default/lldpd
install -d %{buildroot}%{_initrddir}
install -Dm 0755 %{SOURCE4} %{buildroot}%{_initrddir}/

# Make an empty configuration file
touch %{buildroot}%{_sysconfdir}/lldpd.conf

%pre
# Create lldpd user/group
if getent group %lldpd_group >/dev/null 2>&1 ; then : ; else \
 %{_sbindir}/groupadd -r %lldpd_group > /dev/null 2>&1 || exit 1 ; fi
if getent passwd %lldpd_user >/dev/null 2>&1 ; then : ; else \
 %{_sbindir}/useradd --system --shell /bin/false --no-create-home \
 -g %lldpd_group %lldpd_user 2> /dev/null \
 || exit 1 ; fi

%if 0%{?suse_version}
# Service management for SuSE

%post
/sbin/ldconfig
%{fillup_and_insserv lldpd}
%postun
/sbin/ldconfig
%restart_on_update lldpd
%insserv_cleanup
%preun
%stop_on_removal lldpd

%else
%if %{without systemd}
# Service management for Redhat/CentOS without systemd

%post
/sbin/ldconfig
/sbin/chkconfig --add lldpd
%postun
/sbin/ldconfig
if [ "$1" -ge  "1" ]; then
   /sbin/service lldpd condrestart >/dev/null 2>&1 || :
fi
%preun
if [ "$1" = "0" ]; then
   /sbin/service lldpd stop > /dev/null 2>&1
   /sbin/chkconfig --del lldpd
fi

%else
# Service management for Redhat/CentOS with systemd

%post
/sbin/ldconfig
%systemd_post lldpd.service
/bin/systemctl enable lldpd.service

%preun
%systemd_preun lldpd.service

%postun
%systemd_postun_with_restart lldpd.service
/sbin/ldconfig

%endif
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%dir %{_docdir}/lldpd
%doc %{_docdir}/lldpd/NEWS
%doc %{_docdir}/lldpd/ChangeLog
%doc %{_docdir}/lldpd/README.md
%doc %{_docdir}/lldpd/CONTRIBUTE.md
%{_sbindir}/lldpd
%{_sbindir}/lldpctl
%{_sbindir}/lldpcli
%{_libdir}/liblldpctl.so.*
%{_datadir}/zsh
%{_datadir}/bash-completion
%doc %{_mandir}/man8/lldp*
%config(noreplace) %{_sysconfdir}/lldpd.d
%if %{without systemd}
%config(noreplace) %attr(755,root,root) %{_initrddir}/lldpd
%else
%{_unitdir}/lldpd.service
%endif
%{_sysconfdir}/default/lldpd
%config(noreplace) %{_sysconfdir}/lldpd.conf
%{_initrddir}/i40e-lldp-configure.sh

%files devel
%defattr(-,root,root)
%{_libdir}/liblldpctl.so
%{_libdir}/liblldpctl.a
%{_libdir}/liblldpctl.la
%{_libdir}/pkgconfig/lldpctl.pc
%{_includedir}/lldpctl.h
%{_includedir}/lldp-const.h

%changelog
* Fri Jan 01 2016 Vincent Bernat <bernat@luffy.cx> - 0.9.0-1
- New upstream version.
- Do not rely on libnl3.

* Sun Dec 27 2015 Vincent Bernat <bernat@luffy.cx> - 0.8.0-1
- New upstream version.
- Use system libnl3 when possible.
- Use system libevent when possible.

* Wed Sep 09 2015 Vincent Bernat <bernat@luffy.cx> - 0.7.17-1
- New upstream version.

* Fri Aug 07 2015 Vincent Bernat <bernat@luffy.cx> - 0.7.16-1
- New upstream version.

* Wed May 20 2015 Vincent Bernat <bernat@luffy.cx> - 0.7.15-1
- New upstream version.

* Sat Apr 04 2015 Vincent Bernat <bernat@luffy.cx> - 0.7.14-1
- New upstream version.

* Tue Dec 30 2014 Vincent Bernat <bernat@luffy.cx> - 0.7.13-1
- New upstream version.

* Sat Nov 22 2014 Vincent Bernat <bernat@luffy.cx> - 0.7.12-1
- New upstream version.
- Completion for bash and zsh.

* Wed Oct 08 2014 Vincent Bernat <bernat@luffy.cx> - 0.7.11-1
- New upstream version.
- Completion for bash and zsh.

* Mon Jul 21 2014 Vincent Bernat <bernat@luffy.cx> - 0.7.10-1
- New upstream version.

* Wed May 28 2014 Vincent Bernat <bernat@luffy.cx> - 0.7.9-1
- New upstream version.

* Sun Apr 13 2014 Vincent Bernat <bernat@luffy.cx> - 0.7.8-1
- New upstream version.

* Sun Nov 10 2013 Vincent Bernat <bernat@luffy.cx> - 0.7.7-1
- New upstream version.

* Fri Jul 12 2013 Vincent Bernat <bernat@luffy.cx> - 0.7.6-1
- New upstream version.

* Sat Jun 22 2013 Vincent Bernat <bernat@luffy.cx> - 0.7.5-1
- New upstream version.

* Sun May 12 2013 Vincent Bernat <bernat@luffy.cx> - 0.7.3-1
- New upstream version.

* Fri Apr 19 2013 Vincent Bernat <bernat@luffy.cx> - 0.7.2-1
- New upstream version.

* Sat Jan 12 2013 Vincent Bernat <bernat@luffy.cx> - 0.7.1-1
- New upstream version.

* Sun Jan 06 2013 Vincent Bernat <bernat@luffy.cx> - 0.7.0-1
- New upstream version.
- Requires readline-devel.
- Ships lldpcli.

* Thu Sep 27 2012 Vincent Bernat <bernat@luffy.cx> - 0.6.1-1
- New upstream version
- Do not require libevent, use embedded copy.
- Provide a -devel package.

* Fri Jun 11 2010 Vincent Bernat <bernat@luffy.cx> - 0.5.1-1
- New upstream version
- Define bcond_without and with macros if not defined to be compatible
  with RHEL
- Requires useradd and groupadd
- Adapt to make it work with SuSE
- Provide an init script targetted at SuSE
- Build require lm_sensors-devel on RHEL

* Fri Mar 12 2010 Vincent Bernat <bernat@luffy.cx> - 0.5.0-1
- New upstream version
- Add XML support

* Tue May 19 2009 Vincent Bernat <bernat@luffy.cx> - 0.4.0-1
- Add variables
- Enable SNMP support
- Add _lldpd user creation
- Add initscript
- New upstream version

* Mon May 18 2009 Dean Hamstead <dean.hamstead@optusnet.com.au> - 0.3.3-1
- Initial attempt
