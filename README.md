<p align="center">
  <img src="https://www.openssh.com/images/openssh.gif" alt="OpenSSH" width="300">
</p>

<h1 align="center">OpenSSH Static Build</h1>

<p align="center">
  <strong>OpenSSH 10.3p1 + OpenSSL 3.6.2 (Static Link) + PAM</strong>
  <br>
  <em>Clean RPM for legacy Linux distributions with glibc compatibility issues</em>
</p>

<p align="center">
  <a href="https://github.com/jinlingW/openssh-static-openssl/releases"><img src="https://img.shields.io/github/v/release/jinlingW/openssh-static-openssl?color=blue&label=latest" alt="Latest Release"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-BSD-green" alt="License"></a>
  <img src="https://img.shields.io/badge/OpenSSH-10.3p1-orange" alt="OpenSSH">
  <img src="https://img.shields.io/badge/OpenSSL-3.6.2-red" alt="OpenSSL">
  <img src="https://img.shields.io/badge/glibc-2.28%2B-yellow" alt="glibc">
  <img src="https://img.shields.io/badge/arch-x86__64-blueviolet" alt="x86_64">
  <img src="https://img.shields.io/badge/PAM-enabled-success" alt="PAM">
</p>

---

## [中文](#cn) | [English](#en)

---

<div id="cn">

## OpenSSH 静态编译 RPM

### 问题背景

Kylin Linux Advanced Server V10（银河麒麟服务器版）搭载 **glibc 2.28**，官方源中 OpenSSH 版本老旧（8.2p1），且直接编译新版 OpenSSH 会因 glibc 版本不足而产生符号依赖冲突。

本项目通过**将 OpenSSL 3.6.2 静态编译进 OpenSSH 10.3p1**，彻底绕过 libcrypto/libssl 的版本依赖链，同时**保留 PAM 认证的动态链接**，确保与系统认证体系无缝兼容。

### 特性

| 特性 | 说明 |
|------|------|
| **OpenSSL 静态链接** | libssl & libcrypto 编译进二进制，无运行时 OpenSSL 依赖 |
| **PAM 动态链接** | 保留 `/etc/pam.d/sshd` 认证，与系统用户体系完美集成 |
| **标准 RPM 包** | 使用 `rpmbuild` 构建，`rpm -Uvh` 一键安装 |
| **平滑升级** | 自动备份 host keys，自动修复不兼容配置项 |
| **版本替换** | Provides openssh/openssh-server/openssh-clients，可直接替换系统包 |
| **Kylin V10 适配** | 在 Kylin V10 (Halberd) x86_64 上编译和测试通过 |

### 链接分析

```
$ ldd /usr/sbin/sshd
    linux-vdso.so.1
    libcrypt.so.1    -> /usr/lib64/libcrypt.so.1     (系统)
    libpam.so.0      -> /usr/lib64/libpam.so.0       (系统, PAM 认证)
    libutil.so.1     -> /usr/lib64/libutil.so.1       (系统)
    libdl.so.2       -> /usr/lib64/libdl.so.2         (系统)
    libpthread.so.0  -> /usr/lib64/libpthread.so.0    (系统)
    libresolv.so.2   -> /usr/lib64/libresolv.so.2     (系统)
    libz.so.1        -> /usr/lib64/libz.so.1          (系统)
    libc.so.6        -> /usr/lib64/libc.so.6          (系统)

    libssl.so     -> 无! (已静态链接)
    libcrypto.so  -> 无! (已静态链接)
    libpam.so.0   -> 有 (保留 PAM)
```

### 快速安装

```bash
# 1. 下载 RPM
wget https://github.com/jinlingW/openssh-static-openssl/releases/latest/download/openssh-static-10.3-p1.ky10.x86_64.rpm

# 2. 安装（替换系统自带 OpenSSH）
rpm -Uvh openssh-static-10.3-p1.ky10.x86_64.rpm

# 3. 验证
ssh -V
# OpenSSH_10.3p1, OpenSSL 3.6.2
/usr/sbin/sshd -V
# OpenSSH_10.3p1, OpenSSL 3.6.2
```

> **注意**：安装会自动重启 sshd 服务，当前 SSH 会话可能断开。建议在控制台或 tmux 中操作。

### 从源码构建

```bash
# 1. 克隆仓库
git clone https://github.com/jinlingW/openssh-static-openssl.git
cd openssh-static-openssl

# 2. 准备构建环境
yum install -y gcc make perl pam-devel zlib-devel rpm-build

# 3. 构建
rpmbuild -ba openssh-static.spec

# 4. 输出在
ls ~/rpmbuild/RPMS/x86_64/
```

### 包内容

```
/usr/bin/ssh              SSH 客户端
/usr/bin/scp              安全复制
/usr/bin/sftp             SSH 文件传输
/usr/bin/ssh-add          密钥添加
/usr/bin/ssh-agent        认证代理
/usr/bin/ssh-keygen       密钥生成
/usr/bin/ssh-keyscan      主机密钥扫描
/usr/sbin/sshd            SSH 守护进程
/usr/libexec/sshd-session 会话处理（OpenSSH 10.x 新架构）
/usr/libexec/sshd-auth    认证处理（OpenSSH 10.x 新架构）
/usr/libexec/ssh-keysign  主机签名
/usr/libexec/sftp-server  SFTP 服务端
/etc/ssh/ssh_config       SSH 客户端配置 (noreplace)
/etc/ssh/sshd_config      SSH 服务端配置 (noreplace)
```

### 兼容性

| 操作系统 | glibc 版本 | 状态 |
|----------|-----------|------|
| Kylin V10 Server (Halberd) | 2.28 | 已测试 |
| RHEL / CentOS 8 | 2.28 | 理论兼容 |
| RHEL / CentOS 7 | 2.17 | 需测试 |
| Ubuntu 20.04 | 2.31 | 理论兼容 |

### 许可证

仓库中的 spec 文件和构建脚本使用 [BSD License](LICENSE)。OpenSSH 和 OpenSSL 各属其原始许可证。

---

</div>

<div id="en">

## OpenSSH Static Build RPM

### Background

Kylin Linux Advanced Server V10 ships with **glibc 2.28** and an outdated OpenSSH 8.2p1. Building newer OpenSSH directly fails due to symbol dependency conflicts with the older glibc.

This project solves the problem by **statically compiling OpenSSL 3.6.2 into OpenSSH 10.3p1**, breaking the libcrypto/libssl version dependency chain while **preserving dynamic PAM linking** for seamless system authentication integration.

### Features

| Feature | Description |
|---------|-------------|
| **Static OpenSSL** | libssl & libcrypto compiled into binaries - zero OpenSSL runtime deps |
| **Dynamic PAM** | `/etc/pam.d/sshd` auth preserved, perfect system user integration |
| **Standard RPM** | Built with `rpmbuild`, one-command install via `rpm -Uvh` |
| **Seamless Upgrade** | Auto-backs up host keys, auto-fixes incompatible config options |
| **Drop-in Replacement** | Provides openssh/openssh-server/openssh-clients |
| **Kylin V10 Ready** | Compiled and tested on Kylin V10 (Halberd) x86_64 |

### Linkage Analysis

```
$ ldd /usr/sbin/sshd
    linux-vdso.so.1
    libcrypt.so.1    -> /usr/lib64/libcrypt.so.1     (system)
    libpam.so.0      -> /usr/lib64/libpam.so.0       (system, PAM auth)
    libutil.so.1     -> /usr/lib64/libutil.so.1       (system)
    libdl.so.2       -> /usr/lib64/libdl.so.2         (system)
    libpthread.so.0  -> /usr/lib64/libpthread.so.0    (system)
    libresolv.so.2   -> /usr/lib64/libresolv.so.2     (system)
    libz.so.1        -> /usr/lib64/libz.so.1          (system)
    libc.so.6        -> /usr/lib64/libc.so.6          (system)

    libssl.so     -> NONE (statically linked)
    libcrypto.so  -> NONE (statically linked)
    libpam.so.0   -> Present (PAM preserved)
```

### Quick Install

```bash
# 1. Download RPM
wget https://github.com/jinlingW/openssh-static-openssl/releases/latest/download/openssh-static-10.3-p1.ky10.x86_64.rpm

# 2. Install (replaces system OpenSSH)
rpm -Uvh openssh-static-10.3-p1.ky10.x86_64.rpm

# 3. Verify
ssh -V
# OpenSSH_10.3p1, OpenSSL 3.6.2
/usr/sbin/sshd -V
# OpenSSH_10.3p1, OpenSSL 3.6.2
```

> **Note**: Installation automatically restarts sshd. Your current SSH session may disconnect. Consider using console or tmux.

### Build from Source

```bash
# 1. Clone the repo
git clone https://github.com/jinlingW/openssh-static-openssl.git
cd openssh-static-openssl

# 2. Prepare build environment
yum install -y gcc make perl pam-devel zlib-devel rpm-build

# 3. Build
rpmbuild -ba openssh-static.spec

# 4. Find output
ls ~/rpmbuild/RPMS/x86_64/
```

### Package Contents

```
/usr/bin/ssh              SSH client
/usr/bin/scp              Secure copy
/usr/bin/sftp             SSH file transfer
/usr/bin/ssh-add          Key adder
/usr/bin/ssh-agent        Auth agent
/usr/bin/ssh-keygen       Key generator
/usr/bin/ssh-keyscan      Host key scanner
/usr/sbin/sshd            SSH daemon
/usr/libexec/sshd-session Session handler (OpenSSH 10.x new arch)
/usr/libexec/sshd-auth    Auth handler (OpenSSH 10.x new arch)
/usr/libexec/ssh-keysign  Host signer
/usr/libexec/sftp-server  SFTP server
/etc/ssh/ssh_config       Client config (noreplace)
/etc/ssh/sshd_config      Server config (noreplace)
```

### Compatibility

| OS | glibc Version | Status |
|----|--------------|--------|
| Kylin V10 Server (Halberd) | 2.28 | Tested |
| RHEL / CentOS 8 | 2.28 | Compatible |
| RHEL / CentOS 7 | 2.17 | Untested |
| Ubuntu 20.04 | 2.31 | Compatible |

### License

Spec file and build scripts in this repo are [BSD Licensed](LICENSE). OpenSSH and OpenSSL retain their original licenses.

</div>
