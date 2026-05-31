%define openssl_ver 3.6.2
%global debug_package %{nil}
%define openssh_ver 10.3p1

Name:           openssh-static
Version:        10.3
Release:        p1%{?dist}
Summary:        OpenSSH 10.3p1 with static OpenSSL 3.6.2

License:        BSD
URL:            https://www.openssh.com/
Source0:        openssh-10.3p1.tar.gz
Source1:        openssl-3.6.2.tar.gz
Source2:        sshd.service
Source3:        pam.sshd
Source4:        sysconfig.sshd
Source5:        05-redhat.conf
Source6:        sshd-keygen.target
Source7:        sshd-keygen@.service
Source8:        sshd@.service
Source9:        sshd.socket
Source10:       openssh.conf
Source11:       ssh-copy-id
Source12:       sshd-keygen

BuildRequires:  gcc, make, perl, pam-devel, zlib-devel, perl-interpreter
Obsoletes:      openssh-server, openssh, openssh-clients, openssh-help
Provides:       openssh-server, openssh, openssh-clients

%description
OpenSSH 10.3p1 compiled with static OpenSSL 3.6.2 linkage,
resolving glibc compatibility issues on Kylin V10 (glibc 2.28).
PAM authentication support is retained via dynamic linking.

%prep
%setup -q -n openssh-10.3p1

%build
# Build static OpenSSL
tar xzf %{SOURCE1} -C /tmp/
cd /tmp/openssl-%{openssl_ver}
./Configure linux-x86_64 no-shared no-dso     --prefix=/usr/local/openssl-static     --openssldir=/usr/local/openssl-static
make -j16
make install

# Build OpenSSH with static OpenSSL
cd %{_builddir}/openssh-10.3p1
LDFLAGS="-L/usr/local/openssl-static/lib64" CFLAGS="-I/usr/local/openssl-static/include" LIBS="-lcrypto -ldl -lpthread" ./configure     --prefix=%{_prefix}     --sysconfdir=%{_sysconfdir}/ssh     --with-ssl-dir=/usr/local/openssl-static     --with-pam     --with-zlib
make -j16

%install
cd %{_builddir}/openssh-10.3p1
make install DESTDIR=%{buildroot}

# Create directories
mkdir -p -m 0755 %{buildroot}/var/empty/sshd
mkdir -p %{buildroot}%{_unitdir}
mkdir -p %{buildroot}%{_sysconfdir}/pam.d
mkdir -p %{buildroot}%{_sysconfdir}/sysconfig
mkdir -p %{buildroot}%{_sysconfdir}/ssh/ssh_config.d
mkdir -p %{buildroot}/usr/libexec/openssh
mkdir -p %{buildroot}%{_tmpfilesdir}

# Install systemd units
install -m 644 %{SOURCE2} %{buildroot}%{_unitdir}/sshd.service
install -m 644 %{SOURCE6} %{buildroot}%{_unitdir}/sshd-keygen.target
install -m 644 %{SOURCE7} %{buildroot}%{_unitdir}/sshd-keygen@.service
install -m 644 %{SOURCE8} %{buildroot}%{_unitdir}/sshd@.service
install -m 644 %{SOURCE9} %{buildroot}%{_unitdir}/sshd.socket

# Install config files
install -m 644 %{SOURCE3} %{buildroot}%{_sysconfdir}/pam.d/sshd
install -m 644 %{SOURCE4} %{buildroot}%{_sysconfdir}/sysconfig/sshd
install -m 644 %{SOURCE5} %{buildroot}%{_sysconfdir}/ssh/ssh_config.d/05-redhat.conf
install -m 644 %{SOURCE10} %{buildroot}%{_tmpfilesdir}/openssh.conf

# Install helper scripts
install -m 755 %{SOURCE11} %{buildroot}%{_bindir}/ssh-copy-id
install -m 755 %{SOURCE12} %{buildroot}/usr/libexec/openssh/sshd-keygen

# Remove static OpenSSL libs/include from package
rm -rf %{buildroot}/usr/local

%files
# Systemd units
%{_unitdir}/sshd.service
%{_unitdir}/sshd-keygen.target
%{_unitdir}/sshd-keygen@.service
%{_unitdir}/sshd@.service
%{_unitdir}/sshd.socket

# Config files (noreplace)
%config(noreplace) %{_sysconfdir}/pam.d/sshd
%config(noreplace) %{_sysconfdir}/sysconfig/sshd
%config(noreplace) %{_sysconfdir}/ssh/ssh_config.d/05-redhat.conf
%config(noreplace) %{_sysconfdir}/ssh/ssh_config
%config(noreplace) %{_sysconfdir}/ssh/sshd_config
%config(noreplace) %{_sysconfdir}/ssh/moduli
%{_tmpfilesdir}/openssh.conf

# Directories
%dir %attr(0755,root,root) /var/empty/sshd
%dir /usr/libexec/openssh

# Binaries
%attr(0755,root,root) %{_bindir}/ssh
%attr(0755,root,root) %{_bindir}/scp
%attr(0755,root,root) %{_bindir}/ssh-add
%attr(0755,root,root) %{_bindir}/ssh-agent
%attr(0755,root,root) %{_bindir}/ssh-keygen
%attr(0755,root,root) %{_bindir}/ssh-keyscan
%attr(0755,root,root) %{_bindir}/sftp
%attr(0755,root,root) %{_bindir}/ssh-copy-id
%attr(0755,root,root) %{_sbindir}/sshd
%attr(0755,root,root) %{_libexecdir}/sshd-session
%attr(0755,root,root) %{_libexecdir}/sshd-auth
%attr(4711,root,root) %{_libexecdir}/ssh-keysign
%attr(0755,root,root) %{_libexecdir}/ssh-pkcs11-helper
%attr(0755,root,root) %{_libexecdir}/ssh-sk-helper
%attr(0755,root,root) %{_libexecdir}/sftp-server
%attr(0755,root,root) /usr/libexec/openssh/sshd-keygen

# Man pages
%{_mandir}/man1/ssh.1*
%{_mandir}/man1/scp.1*
%{_mandir}/man1/ssh-add.1*
%{_mandir}/man1/ssh-agent.1*
%{_mandir}/man1/ssh-keygen.1*
%{_mandir}/man1/ssh-keyscan.1*
%{_mandir}/man1/sftp.1*
%{_mandir}/man5/moduli.5*
%{_mandir}/man5/sshd_config.5*
%{_mandir}/man5/ssh_config.5*
%{_mandir}/man8/sshd.8*
%{_mandir}/man8/sftp-server.8*
%{_mandir}/man8/ssh-keysign.8*
%{_mandir}/man8/ssh-pkcs11-helper.8*
%{_mandir}/man8/ssh-sk-helper.8*

%pre
if [ -d /etc/ssh ] && [ -f /etc/ssh/ssh_host_ed25519_key ]; then
    mkdir -p /tmp/ssh-hk-bak
    cp -a /etc/ssh/ssh_host_* /tmp/ssh-hk-bak/ 2>/dev/null || true
fi

%post
# Restore host keys
if [ -f /tmp/ssh-hk-bak/ssh_host_ed25519_key ]; then
    cp -a /tmp/ssh-hk-bak/ssh_host_* /etc/ssh/ 2>/dev/null || true
    rm -rf /tmp/ssh-hk-bak
fi

# Fix incompatible config options for OpenSSH 10.x
sed -i "s/^GSSAPIAuthentication/#GSSAPIAuthentication/" /etc/ssh/sshd_config 2>/dev/null || true
sed -i "s/^GSSAPICleanupCredentials/#GSSAPICleanupCredentials/" /etc/ssh/sshd_config 2>/dev/null || true
sed -i "s/^RSAAuthentication/#RSAAuthentication/" /etc/ssh/sshd_config 2>/dev/null || true
sed -i "s/^RhostsRSAAuthentication/#RhostsRSAAuthentication/" /etc/ssh/sshd_config 2>/dev/null || true
sed -i "s/^GSSAPIKexAlgorithms/#GSSAPIKexAlgorithms/" /etc/ssh/sshd_config 2>/dev/null || true

# Fix sftp-server subsystem path for OpenSSH 10.x
sed -i "s|/usr/libexec/openssh/sftp-server|/usr/libexec/sftp-server|g" /etc/ssh/sshd_config 2>/dev/null || true

# Reload systemd
systemctl daemon-reload 2>/dev/null || true

%posttrans
# enable+start AFTER all old package scripts complete
systemctl enable sshd 2>/dev/null || true
systemctl start sshd 2>/dev/null || true

%preun
if [  -eq 0 ]; then
    systemctl stop sshd 2>/dev/null || true
    systemctl disable sshd 2>/dev/null || true
fi

%postun
if [  -ge 1 ]; then
    systemctl daemon-reload 2>/dev/null || true
    systemctl try-restart sshd 2>/dev/null || systemctl restart sshd 2>/dev/null || true
fi

%changelog
* Sun May 31 2026 Builder <root@localhost> - 10.3-p1
- OpenSSH 10.3p1 with static OpenSSL 3.6.2
- Built for Kylin V10 (glibc 2.28) compatibility
- PAM authentication retained via dynamic linking
- Complete systemd units, PAM config, sshd-keygen included





