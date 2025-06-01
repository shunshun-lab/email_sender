# 実際のメール送信設定ガイド

## 1. SMTP設定

### Gmail使用時
1. **Googleアカウントで2段階認証を有効化**
2. **アプリパスワードを生成**
   - Google アカウント → セキュリティ → 2段階認証プロセス → アプリパスワード
   - 「メール」を選択してパスワードを生成
3. **.envファイルを編集**

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=generated_app_password
SENDER_EMAIL=your_email@gmail.com
SENDER_NAME=あなたの名前
```

### Outlook/Hotmail使用時
```env
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME=your_email@outlook.com
SMTP_PASSWORD=your_password
SENDER_EMAIL=your_email@outlook.com
SENDER_NAME=あなたの名前
```

### その他のSMTPサービス
- **SendGrid**, **Mailgun**, **Amazon SES** なども使用可能

## 2. 受信者CSVファイル準備

CSVファイルは以下の形式で作成してください：

```csv
名前,会社名,メールアドレス
田中太郎,株式会社サンプル,tanaka@example.com
佐藤花子,テスト株式会社,sato@test.co.jp
```

**重要**: 実際のテストでは、**自分のメールアドレス**を使用してください。

## 3. 実際の使用手順

1. **アプリケーション起動**
   ```bash
   cd email_sender
   source venv/bin/activate
   python src/main.py
   ```

2. **ブラウザでアクセス**
   - http://localhost:8000

3. **メール送信手順**
   - テンプレート管理 → サンプルテンプレートを確認
   - メール送信 → CSVファイルをアップロード
   - SMTP設定を入力
   - テスト送信を実行

4. **追跡結果確認**
   - 追跡結果ページで送信状況を確認
   - メール開封時にトラッキングが更新される

## 4. セキュリティ注意事項

- **.envファイルは絶対にGitにコミットしない**
- **本番環境では強力なパスワードを使用**
- **テスト時は自分のメールアドレスのみ使用**
- **大量送信前にスパム規制を確認**

## 5. トラブルシューティング

### よくあるエラー
- **認証エラー**: アプリパスワードが正しく設定されているか確認
- **接続エラー**: ファイアウォールやネットワーク設定を確認
- **送信制限**: Gmail等は1日の送信制限があります

### ログ確認
アプリケーション実行中のコンソールでエラーメッセージを確認してください。 