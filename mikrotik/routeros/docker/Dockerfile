FROM public.ecr.aws/docker/library/debian:bullseye-slim
LABEL org.opencontainers.image.authors="roman@dodin.dev"

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update -qy \
   && apt-get install -y --no-install-recommends \
   bridge-utils \
   iproute2 \
   python3 \
   socat \
   qemu-system-x86 \
   qemu-utils \
   iptables \
   && rm -rf /var/lib/apt/lists/*

ARG IMAGE
COPY $IMAGE* /
COPY *.py /

ENV PYTHONUNBUFFERED=1

EXPOSE 22 161/udp 830 5000 5678 8291 8728 10000-10099
HEALTHCHECK CMD ["/healthcheck.py"]
ENTRYPOINT ["/launch.py"]