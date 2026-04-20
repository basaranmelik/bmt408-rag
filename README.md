# Anakronik RAG - BMT-408 Dönem Projesi

## Proje Bilgileri

- **Ad Soyad:** Melik Başaran
- **Öğrenci No:** 22181616013
- **E-posta:** basaranmelik1@gmail.com
- **Ders:** BMT-408 Sistem Programlama

---

## Proje Açıklaması

 Kullanıcılar PDF dosyaları yükleyerek, yüklediği belgelerin içeriğine dayanarak tarihi kişiliklerle Türkçe diyalog kurabilirler.

### Teknoloji Stack
- **Backend:** FastAPI
- **Veritabanı:** PostgreSQL
- **Vector DB:** Qdrant
- **LLM:** Google Gemini 2.5 Flash
- **Reverse Proxy:** Nginx
- **Container:** Docker & Docker Compose

---

## Hızlı Başlangıç

### Yerel Geliştirme
```bash
# Tüm servisleri başlat (FastAPI, PostgreSQL, Qdrant, Nginx, Adminer)
docker-compose up -d

# Uygulama port 80'de çalışır (nginx üzerinden)
# Adminer (DB tarayıcı) http://127.0.0.1:8080
# Qdrant API http://127.0.0.1:6333
```

### Ortam Değişkenleri Kurulumu
`.env.example`'ı `.env` olarak kopyala ve yapılandır:
- `GOOGLE_API_KEY`: Google Gemini API anahtarı (LLM ve embeddings için)
- `TAVILY_API_KEY`: Web arama fallback'i için
- `DB_USER`: PostgreSQL kullanıcı adı (varsayılan: `anakronik`)
- `DB_PASSWORD`: PostgreSQL şifresi (üretimde değiştir!)
- `DB_NAME`: PostgreSQL veritabanı adı (varsayılan: `anakronik_rag`)
- `DATABASE_URL`: PostgreSQL bağlantı dizesi (yerel geliştirme için)
- `QDRANT_HOST/PORT`: Vector DB bağlantısı (docker-compose tarafından otomatik ayarlanır)

---

## Kurulum Adımları

### 1. AWS Üzerinde Sunucu Temini

1. AWS Free Tier kapsamına uygun **EC2 micro instance** oluşturuldu.
2. **Key pair** oluşturuldu (SSH erişimi için `.ppk` dosyası).
3. **Security Group** yapılandırıldı:
   - `22/tcp`: Sadece kendi IP'si (SSH)
   - `80/tcp`: Herkese açık (HTTP)
   - `443/tcp`: Herkese açık (HTTPS)
   - `5432` ve `6333` portları **dış dünyaya kapalı**
4. Free Tier / Budget takibi ayarlandı (maliyet alarmı).

### 2. Ön Hazırlık

#### a. `gazi` Kullanıcısı Oluşturma
```bash
# Kullanıcı oluştur ve sudo yetkisi ver
sudo adduser gazi
sudo usermod -aG sudo gazi
```

#### b. Hostname Ayarı
```bash
sudo hostnamectl set-hostname 22181616013.net

# Kontrol et
hostname
```

#### c. İşletim Sistemi Güncelleme (Ubuntu 24.04 LTS)
```bash
sudo apt update && sudo apt upgrade -y
```

#### d. History Kayıt Formatı
```bash
# ~/.bashrc veya /etc/profile.d/history.sh dosyasına eklendi:
export HISTTIMEFORMAT="%F %T "
export HISTSIZE=10000
export HISTFILESIZE=20000
export PROMPT_COMMAND='history -a'
```

#### e. Komut Satırı Web Tarayıcısı
```bash
sudo apt install -y lynx
# Kullanım:
lynx http://localhost
```

#### f. SSH Sunucusu Yapılandırması
```bash
# /etc/ssh/sshd_config düzenlendi:
# PermitRootLogin no
# PasswordAuthentication no  (key ile giriş zorunlu)
# PubkeyAuthentication yes

sudo systemctl restart sshd
```

#### g. GCC Kurulumu
```bash
sudo apt install -y gcc build-essential
gcc --version
```

#### h. Java Kurulumu
```bash
sudo apt install -y default-jdk
java -version
```

#### i. Nmap Kurulumu
```bash
sudo apt install -y nmap

# Açık portları tara
sudo nmap -sT -O localhost
```

#### j. Yönetim Aracı (Cockpit)
```bash
sudo apt install -y cockpit
sudo systemctl enable --now cockpit.socket
# Erişim: https://sunucu-ip:9090
```

#### k. NTFS-3G Driver
```bash
sudo apt install -y ntfs-3g
```

#### l. Rootkit Hunter
```bash
sudo apt install -y rkhunter
sudo rkhunter --update
sudo rkhunter --check
```

#### m. Kötü Amaçlı Yazılım Taraması (ClamAV)
```bash
sudo apt install -y clamav clamav-daemon
sudo freshclam
sudo clamscan -r /home
```

#### n. Speedtest-cli
```bash
sudo apt install -y speedtest-cli
speedtest-cli
```

---

### 3. Sunucu Kurulumları (Konteynerlar)

#### a. Docker Engine ve Docker Compose Kurulumu
```bash
# Docker Engine kur
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker gazi

# Docker Compose
sudo apt install -y docker-compose-plugin

# Kontrol et
docker --version
docker compose version
```

#### b. `.env` Dosyası Hazırlama
```bash
# .env.example'ı kopyala
cp .env.example .env
```

`.env` içeriğini düzenle:
```
GOOGLE_API_KEY=your-google-api-key
TAVILY_API_KEY=your-tavily-api-key
DB_USER=anakronik
DB_PASSWORD=your-secure-password
DB_NAME=anakronik_rag
DATABASE_URL=postgresql+asyncpg://anakronik:your-secure-password@db:5432/anakronik_rag
QDRANT_HOST=qdrant
QDRANT_PORT=6333
```

#### c. Docker Compose ile Servisleri Başlatma
```bash
# Tüm servisleri başlat
docker-compose up -d

# Durum kontrol et
docker-compose ps
```

**Başlayan Servisler:**
| Servis | Açıklama | Port |
|--------|----------|------|
| `nginx` | Reverse proxy, dış erişim noktası | 80 |
| `app` | FastAPI uygulaması (Nginx arkasında) | - |
| `db` | PostgreSQL (internal only) | - |
| `qdrant` | Vector DB (internal only) | - |
| `adminer` | DB yönetim arayüzü | 127.0.0.1:8080 |
| `backup` | Otomatik günlük yedekleme | - |

#### d. Uygulamaya Erişim

| Servis | URL | Açıklama |
|--------|-----|----------|
| **API** | `http://localhost` | FastAPI uygulaması |
| **Swagger UI** | `http://localhost/docs` | API dokümantasyonu |
| **Adminer** | `http://127.0.0.1:8080` | Database yönetim aracı |
| **Qdrant** | `http://127.0.0.1:6333` | Vector DB API |

#### e. Dosya Aktarımı / Deploy (SFTP)
```bash
# SFTP ile sunucuya bağlan (FTP kullanılmaz)
sftp -i bmt-408.ppk gazi@http://3.69.255.22/

# Proje dosyalarını yükle
put -r compose.yml
put -r app/
put -r nginx/
put -r backup/
put .env

# SSH ile sunucuya gir ve servisleri başlat
ssh -i bmt-408.ppk gazi@http://3.69.255.22/
docker-compose up -d --build
```

**Git ile Deploy (Alternatif):**
```bash
git clone https://github.com/basaranmelik/bmt408-rag
cd anakronik-rag
git pull origin main
docker-compose up -d --build
```

---

### 4. Firewall Ayarları

#### a. AWS Security Group
```
Inbound Rules:
  - SSH (22):   Sadece kendi IP
  - HTTP (80):  0.0.0.0/0 (Herkese açık)
  - HTTPS (443): 0.0.0.0/0 (Herkese açık)

Kapalı Portlar:
  - 5432 (PostgreSQL) - Dış dünyaya kapalı
  - 3306 (MariaDB)    - Dış dünyaya kapalı
  - 6333 (Qdrant)     - Dış dünyaya kapalı
```

#### b. Sunucu İçi Firewall (nftables)
```bash
# Mevcut kuralları temizle
sudo nft flush ruleset

# Kural seti oluştur
sudo nft add table inet filter
sudo nft add chain inet filter input  '{ type filter hook input priority 0; policy drop; }'
sudo nft add chain inet filter forward '{ type filter hook forward priority 0; policy drop; }'
sudo nft add chain inet filter output '{ type filter hook output priority 0; policy accept; }'

# İzin verilen bağlantılar
sudo nft add rule inet filter input iif lo accept
sudo nft add rule inet filter input ct state established,related accept
sudo nft add rule inet filter input tcp dport 22 accept   # SSH
sudo nft add rule inet filter input tcp dport 80 accept   # HTTP
sudo nft add rule inet filter input tcp dport 443 accept  # HTTPS

# Kuralları kalıcı kaydet
sudo nft list ruleset | sudo tee /etc/nftables.conf
sudo systemctl enable nftables

# Kontrol
sudo nft list ruleset
```

---

### 5. Rutin Görev (Otomatik Yedekleme)

Yedekleme `backup` konteyneri üzerinden otomatik olarak çalışır:

- **Zaman:** Her gün saat **04:00 (Europe/Istanbul)**
- **Format:** `.sql.gz` (sıkıştırılmış dump)
- **Saklama:** **7 gün** (rotation, eski yedekler otomatik silinir)
- **Konum:** `backup_data/` volume'ü içinde

#### Manuel Yedek Alma
```bash
# Manuel yedek al
docker exec anakronik-rag-db-1 pg_dump -U anakronik -d anakronik_rag | gzip > backup_manual.sql.gz

# Mevcut yedekleri listele
docker exec anakronik-rag-backup-1 ls -lh /backups/
```

#### Restore Testi
```bash
# Yedekten geri yükle
docker exec -T anakronik-rag-db-1 sh -c \
  'gunzip -c /backups/backup_YYYYMMDD_HHMMSS.sql.gz | psql -U anakronik -d anakronik_rag'

# Başarılı olup olmadığını kontrol et
docker exec anakronik-rag-db-1 psql -U anakronik -d anakronik_rag \
  -c "SELECT COUNT(*) FROM chat_sessions;"
```

---

## Test Adımları

### 1. Health Check
```bash
curl http://localhost/health
# Beklenen: {"status":"ok"}
```

### 2. Swagger UI ile Test
1. `http://localhost/docs` adresine git
2. İstenen endpoint'i aç → "Try it out" → "Execute"
3. 200 OK yanıtını gör

### 3. Database Bağlantısı
```bash
docker exec anakronik-rag-db-1 psql -U anakronik -d anakronik_rag -c "SELECT 1"
```

### 4. Docker Kontrol
```bash
docker-compose ps
docker-compose logs app
docker-compose logs db
```

### 5. Port Denetimi
```bash
# Açık portları listele
ss -tulpn

# nftables kuralları
sudo nft list ruleset

# Nginx kontrol
curl -I http://localhost
```

---

## API Endpoints

### Health Check
```
GET /health
Yanıt: {"status":"ok"}
```

### PDF Upload
```
POST /upload
Content-Type: multipart/form-data
Parametreler:
  - user_id: int
  - historical_figure_id: int
  - file: PDF dosyası
```

### Soru Sorma (QA)
```
POST /ask
Body:
{
  "session_id": int,
  "question": "Türkçe soru"
}
Yanıt:
{
  "answer": "Türkçe cevap",
  "sources": [...]
}
```

### Chat Oturumları
```
GET  /chat-sessions
GET  /chat-sessions/{session_id}
POST /chat-sessions
```

### Tarihi Kişilikler
```
GET  /historical-figures
POST /historical-figures
```

---
