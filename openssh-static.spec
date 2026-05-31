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

# Create /var/empty for privilege separation
mkdir -p -m 0755 %{buildroot}/var/empty

# Install systemd service file
mkdir -p %{buildroot}%{_unitdir}
install -m 644 %{SOURCE2} %{buildroot}%{_unitdir}/sshd.service

# Remove static OpenSSL libs/include from package - they are embedded
rm -rf %{buildroot}/usr/local

%files
%{_unitdir}/sshd.service
%dir %attr(0755,root,root) /var/empty
%attr(0755,root,root) %{_bindir}/ssh
%attr(0755,root,root) %{_bindir}/scp
%attr(0755,root,root) %{_bindir}/ssh-add
%attr(0755,root,root) %{_bindir}/ssh-agent
%attr(0755,root,root) %{_bindir}/ssh-keygen
%attr(0755,root,root) %{_bindir}/ssh-keyscan
%attr(0755,root,root) %{_bindir}/sftp
%attr(0755,root,root) %{_sbindir}/sshd
%attr(0755,root,root) %{_libexecdir}/sshd-session
%attr(0755,root,root) %{_libexecdir}/sshd-auth
%attr(4711,root,root) %{_libexecdir}/ssh-keysign
%attr(0755,root,root) %{_libexecdir}/ssh-pkcs11-helper
%attr(0755,root,root) %{_libexecdir}/ssh-sk-helper
%attr(0755,root,root) %{_libexecdir}/sftp-server
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
%config(noreplace) %{_sysconfdir}/ssh/ssh_config
%config(noreplace) %{_sysconfdir}/ssh/sshd_config
%config(noreplace) %{_sysconfdir}/ssh/moduli

%pre
# Backup existing host keys before upgrade
if [ -d /etc/ssh ]; then
    mkdir -p /tmp/ssh-hostkeys-backup
    cp -a /etc/ssh/ssh_host_* /tmp/ssh-hostkeys-backup/ 2>/dev/null || true
fi

%post
# Restore host keys if needed
if [ -f /tmp/ssh-hostkeys-backup/ssh_host_ed25519_key ]; then
    cp -a /tmp/ssh-hostkeys-backup/ssh_host_* /etc/ssh/ 2>/dev/null || true
    rm -rf /tmp/ssh-hostkeys-backup
fi

# Fix incompatible config options for OpenSSH 10.x
sed -i 's/^GSSAPIAuthentication/#GSSAPIAuthentication/' /etc/ssh/sshd_config 2>/dev/null || true
sed -i 's/^GSSAPICleanupCredentials/#GSSAPICleanupCredentials/' /etc/ssh/sshd_config 2>/dev/null || true
sed -i 's/^RSAAuthentication/#RSAAuthentication/' /etc/ssh/sshd_config 2>/dev/null || true
sed -i 's/^RhostsRSAAuthentication/#RhostsRSAAuthentication/' /etc/ssh/sshd_config 2>/dev/null || true
sed -i 's/^GSSAPIKexAlgorithms/#GSSAPIKexAlgorithms/' /etc/ssh/sshd_config 2>/dev/null || true

# Reload systemd and enable/start sshd
systemctl daemon-reload 2>/dev/null || true
systemctl enable sshd 2>/dev/null || true
systemctl try-restart sshd 2>/dev/null || systemctl restart sshd 2>/dev/null || true

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
- Includes systemd service file

