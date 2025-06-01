FROM python:3.11-slim

# 作業ディレクトリを設定
WORKDIR /app

# 依存関係をコピーしてインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションファイルをコピー
COPY email_sender/ ./email_sender/

# 作業ディレクトリを変更
WORKDIR /app/email_sender

# ポート8000を公開
EXPOSE 8000

# アプリケーションを起動
CMD ["gunicorn", "src.main:app", "--bind", "0.0.0.0:8000", "--workers", "2"] 