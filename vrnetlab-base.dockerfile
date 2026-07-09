FROM public.ecr.aws/docker/library/debian:trixie-slim
LABEL org.opencontainers.image.authors="roman@dodin.dev"

COPY --from=ghcr.io/astral-sh/uv:0.11.23 /uv /uvx /bin/

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update -qy \
   && apt-get install -y --no-install-recommends \
   ca-certificates \
   bridge-utils \
   iproute2 \
   socat \
   qemu-kvm \
   qemu-utils \
   tcpdump \
   tftpd-hpa \
   ssh \
   inetutils-ping \
   dnsutils \
   iptables \
   nftables \
   telnet \
   git \
   dosfstools \
   genisoimage \
   ovmf \
   cloud-utils \
   sshpass \
   && rm -rf /var/lib/apt/lists/*

# copying the uv project
COPY pyproject.toml /pyproject.toml
COPY uv.lock /uv.lock
RUN /bin/uv sync --frozen

# copy core vrnetlab scripts
COPY ./common/healthcheck.py ./common/vrnetlab.py /

# Default HEALTHCHECK options give a 0s start-period, so with the default 30s
# interval / 3 retries, any node whose boot legitimately takes longer than ~90s
# gets marked unhealthy while it's still booting. That's shorter than a typical
# VM-based kind's boot time under qemu, so orchestrators that auto-heal on
# "unhealthy" (e.g. vlab) end up restarting the node before it ever finishes
# booting, looping forever regardless of whether the boot itself would have
# succeeded.
HEALTHCHECK --start-period=300s --interval=15s --retries=3 CMD ["uv", "run", "/healthcheck.py"]
ENTRYPOINT ["uv", "run", "/launch.py"]