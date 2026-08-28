FROM ubuntu:noble

ARG TARGETARCH
ARG SOTN_RELEASE=cc1-psx-26
ARG GCCSH_ARCHIVE=cygnus-2.7-96Q3-bin

RUN test "$TARGETARCH" = "amd64" && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        libbsd0 \
        libelf1t64 \
        libreadline8t64 \
        xfonts-utils && \
    curl -fsSL https://github.com/sozud/dosemu-deb/raw/main/fdpp_1.6-1_amd64.deb -o /tmp/fdpp.deb && \
    curl -fsSL https://github.com/sozud/dosemu-deb/raw/main/fdpp-dev_1.6-1_amd64.deb -o /tmp/fdpp-dev.deb && \
    curl -fsSL https://github.com/sozud/dosemu-deb/raw/main/comcom32_0.1~alpha3-1_all.deb -o /tmp/comcom32.deb && \
    curl -fsSL https://github.com/sozud/dosemu-deb/raw/main/dosemu2_2.0~pre9-1_amd64.deb -o /tmp/dosemu2.deb && \
    dpkg -i /tmp/fdpp.deb /tmp/fdpp-dev.deb /tmp/comcom32.deb /tmp/dosemu2.deb && \
    rm -f /tmp/*.deb && \
    mkdir -p /opt/gccsh && \
    curl -fsSL "https://github.com/Xeeynamo/sotn-decomp/releases/download/${SOTN_RELEASE}/${GCCSH_ARCHIVE}.tar.gz" -o /tmp/gccsh.tar.gz && \
    tar -xzf /tmp/gccsh.tar.gz -C /tmp && \
    cp -a "/tmp/${GCCSH_ARCHIVE}/." /opt/gccsh/ && \
    test -f /opt/gccsh/GCC.EXE && \
    test -f /opt/gccsh/CPP.EXE && \
    test -f /opt/gccsh/CC1.EXE && \
    test -f /opt/gccsh/GO32.EXE && \
    rm -rf /tmp/gccsh.tar.gz "/tmp/${GCCSH_ARCHIVE}" /var/lib/apt/lists/*

COPY compile.sh /usr/local/bin/compile-sh

ENTRYPOINT ["/usr/local/bin/compile-sh"]
