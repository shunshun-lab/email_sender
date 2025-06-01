# 📦 デプロイメントガイド

## 🌟 Heroku（おすすめ）

### 1. 前準備
```bash
# Heroku CLIをインストール
brew install heroku/brew/heroku

# ログイン
heroku login
```

### 2. アプリ作成
```bash
# Herokuアプリを作成
heroku create your-email-sender-app

# リモートリポジトリの確認
git remote -v
```

### 3. 環境変数設定
```bash
heroku config:set SMTP_HOST=smtp.gmail.com
heroku config:set SMTP_PORT=587
heroku config:set SMTP_USERNAME=japanxcollege@gmail.com
heroku config:set SMTP_PASSWORD="zuth dzji yfrn jbbd"
heroku config:set SENDER_EMAIL=japanxcollege@gmail.com
heroku config:set SENDER_NAME=JapanXCollege
heroku config:set FLASK_ENV=production
```

### 4. デプロイ
```bash
# 変更をコミット
git add .
git commit -m "Deploy email sender app"

# Herokuにプッシュ
git push heroku main

# ブラウザで確認
heroku open
```

### 5. ログ確認
```bash
# リアルタイムログ
heroku logs --tail

# エラー確認
heroku logs --source app
```

---

## 🐳 Docker + Railway/Render

### Dockerファイル作成
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY email_sender/ ./email_sender/

WORKDIR /app/email_sender

CMD ["gunicorn", "src.main:app", "--bind", "0.0.0.0:8000"]
```

### Railway.app
1. https://railway.app にアクセス
2. GitHubリポジトリを連携
3. 環境変数を設定
4. 自動デプロイ

### Render.com
1. https://render.com にアクセス
2. GitHubリポジトリを連携
3. Web Serviceとして設定
4. Start Command: `cd email_sender && gunicorn src.main:app --bind 0.0.0.0:$PORT`

---

## ☁️ AWS EC2

### 1. EC2インスタンス起動
```bash
# Ubuntu 22.04 LTS を選択
# セキュリティグループで80, 443, 8000ポートを開放
```

### 2. サーバー設定
```bash
# パッケージ更新
sudo apt update && sudo apt upgrade -y

# Python環境構築
sudo apt install python3-pip python3-venv nginx -y

# アプリケーション配置
git clone https://github.com/your-username/email-sender-app.git
cd email-sender-app

# 仮想環境作成
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Systemdサービス設定
```bash
# サービスファイル作成
sudo nano /etc/systemd/system/email-sender.service
```

```ini
[Unit]
Description=Email Sender App
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/email-sender-app/email_sender
Environment=PATH=/home/ubuntu/email-sender-app/venv/bin
ExecStart=/home/ubuntu/email-sender-app/venv/bin/gunicorn src.main:app --bind 127.0.0.1:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

### 4. Nginx設定
```bash
sudo nano /etc/nginx/sites-available/email-sender
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# 設定有効化
sudo ln -s /etc/nginx/sites-available/email-sender /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx

# サービス開始
sudo systemctl enable email-sender
sudo systemctl start email-sender
```

---

## 🔒 SSL証明書設定 (Let's Encrypt)

```bash
# Certbot インストール
sudo apt install certbot python3-certbot-nginx -y

# SSL証明書取得
sudo certbot --nginx -d your-domain.com

# 自動更新設定
sudo crontab -e
# 以下を追加:
# 0 12 * * * /usr/bin/certbot renew --quiet
```

---

## 📊 監視・メンテナンス

### ログ監視
```bash
# アプリケーションログ
sudo journalctl -u email-sender -f

# Nginxログ
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### バックアップ
```bash
# データベースバックアップ
cp email_sender/email_tracking.db backup_$(date +%Y%m%d).db
```

### アップデート
```bash
# コード更新
git pull origin main

# サービス再起動
sudo systemctl restart email-sender
```

---

## 🚀 推奨デプロイ方法

1. **開発・テスト**: Heroku（無料枠）
2. **本格運用**: Railway/Render（月$5-10）
3. **大規模運用**: AWS EC2 + RDS

## 注意事項

- **SMTP設定**: 本番環境では環境変数で管理
- **データベース**: 本番ではPostgreSQLを推奨
- **セキュリティ**: HTTPS必須、定期的なセキュリティ更新
- **監視**: ログ監視とエラー通知の設定 