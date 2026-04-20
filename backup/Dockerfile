FROM postgres:16-alpine

COPY backup.sh /usr/local/bin/backup.sh
RUN chmod +x /usr/local/bin/backup.sh

RUN mkdir -p /etc/crontabs && \
    echo "0 4 * * * /usr/local/bin/backup.sh >> /var/log/backup.log 2>&1" \
    > /etc/crontabs/root

ENV TZ=Europe/Istanbul

CMD ["crond", "-f", "-l", "2", "-c", "/etc/crontabs"]
