FROM ghcr.io/nunu27/vrnetlab/base:latest
LABEL org.opencontainers.image.authors="roman@dodin.dev"

RUN apt-get update -qy \
   && apt-get install -y --no-install-recommends \
   qemu-system-x86 \
   qemu-efi-aarch64 \
   ftp \
   && rm -rf /var/lib/apt/lists/*

ARG IMAGE
COPY $IMAGE* /
COPY *.py /

EXPOSE 22 161/udp 830 5000 5678 8291 8728 10000-10099
