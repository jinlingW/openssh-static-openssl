#!/bin/bash
# OpenSSH Static Build Script
# Downloads and compiles OpenSSL (static) + OpenSSH with PAM support
set -e

OPENSSL_VER="3.6.2"
OPENSSH_VER="10.3p1"
BUILD_DIR="/root/rpmbuild"

echo "=== OpenSSH Static Build ==="
echo "OpenSSL: ${OPENSSL_VER} (static)"
echo "OpenSSH: ${OPENSSH_VER}"

# Install build deps
echo "[1/5] Installing build dependencies..."
yum install -y gcc make perl pam-devel zlib-devel rpm-build

# Download sources
echo "[2/5] Downloading sources..."
cd /tmp
curl -sL -O "https://cdn.openbsd.org/pub/OpenBSD/OpenSSH/portable/openssh-${OPENSSH_VER}.tar.gz"
curl -sL -O "https://www.openssl.org/source/openssl-${OPENSSL_VER}.tar.gz"

cp openssh-${OPENSSH_VER}.tar.gz openssl-${OPENSSL_VER}.tar.gz ${BUILD_DIR}/SOURCES/

# Build RPM
echo "[3/5] Building RPM (this takes 5-10 minutes)..."
cd ${BUILD_DIR}
rpmbuild -ba SPECS/openssh-static.spec

echo "[4/5] RPM built!"
find ${BUILD_DIR}/RPMS -name "*.rpm" -ls

echo "[5/5] Done! Install with:"
echo "  rpm -Uvh ${BUILD_DIR}/RPMS/x86_64/openssh-static-*.rpm"
