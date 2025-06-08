FROM ipfs/kubo:latest

RUN /usr/local/bin/start_ipfs version
COPY ipfs/config.sh /data/ipfs/config.sh
RUN chmod +x /data/ipfs/config.sh; /data/ipfs/config.sh

EXPOSE 4001/udp 4001 5001 8080