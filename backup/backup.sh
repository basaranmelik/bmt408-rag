#!/bin/sh
set -e

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
FILENAME="backup_${DATE}.sql.gz"
KEEP_DAYS="${BACKUP_KEEP_DAYS:-7}"

mkdir -p "$BACKUP_DIR"

echo "[$(date)] Backup başlıyor: $FILENAME"

pg_dump \
    -h "$PGHOST" \
    -p "${PGPORT:-5432}" \
    -U "$PGUSER" \
    -d "$PGDATABASE" \
    --no-password \
| gzip > "$BACKUP_DIR/$FILENAME"

echo "[$(date)] Backup tamamlandı: $FILENAME ($(du -sh "$BACKUP_DIR/$FILENAME" | cut -f1))"

# Rotation: KEEP_DAYS günden eski dosyaları sil
find "$BACKUP_DIR" -name "backup_*.sql.gz" -mtime "+${KEEP_DAYS}" -delete
echo "[$(date)] Eski backup'lar temizlendi (>${KEEP_DAYS} gün)"

# Mevcut backup listesi
echo "[$(date)] Mevcut backup'lar:"
ls -lh "$BACKUP_DIR"/backup_*.sql.gz 2>/dev/null || echo "  (yok)"
