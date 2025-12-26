# SquadBeyond 複製ツール

SquadBeyondの記事を自動的に複製するためのGUIアプリケーションです。Playwrightを使用してブラウザを自動操作し、記事の複製作業を効率化します。

## 機能

- **自動ログイン**: SquadBeyondに自動的にログイン
- **グループ・フォルダ選択**: 階層構造からグループとフォルダを選択
- **記事選択**: 選択したフォルダ内の記事一覧を取得
- **記事複製**: 選択した記事を新しいタイトルとURLで複製
- **ログ表示**: 操作の進行状況をリアルタイムで表示

## 必要な環境

- Python 3.9以上
- Playwright
- python-dotenv
- Tkinter（通常はPythonに標準で含まれています）

## セットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

または個別にインストールする場合：

```bash
pip install playwright python-dotenv
```

### 2. Playwrightブラウザのインストール

```bash
playwright install chromium
```

### 3. 環境変数の設定

ログイン情報を`.env`ファイルに設定します。

プロジェクトルートに`.env`ファイルを作成し、以下の形式で記述してください：

```env
SQUADBEYOND_EMAIL=your_email@example.com
SQUADBEYOND_PASSWORD=your_password
```

**重要**: `.env`ファイルの記述時の注意点
- 各行は `変数名=値` の形式で記述してください
- 値にスペースが含まれる場合は、引用符で囲む必要はありません（囲んでも問題ありません）
- コメントは `#` で始まる行に記述してください
- 空行は無視されます
- 等号（`=`）の前後に不要なスペースを入れないでください

**注意**: `.env`ファイルは`.gitignore`に含まれているため、Gitにはコミットされません。セキュリティのため、実際のログイン情報を直接コミットしないでください。

#### 環境変数として直接設定する場合（オプション）

`.env`ファイルの代わりに、環境変数として直接設定することもできます。

**macOS / Linux の場合:**

```bash
export SQUADBEYOND_EMAIL="your_email@example.com"
export SQUADBEYOND_PASSWORD="your_password"
```

**Windows の場合:**

コマンドプロンプト:
```cmd
set SQUADBEYOND_EMAIL=your_email@example.com
set SQUADBEYOND_PASSWORD=your_password
```

PowerShell:
```powershell
$env:SQUADBEYOND_EMAIL="your_email@example.com"
$env:SQUADBEYOND_PASSWORD="your_password"
```

## 使い方

### アプリケーションの起動

環境変数を設定した後、アプリケーションを起動します：

```bash
python app.py
```

**注意**: `.env`ファイルまたは環境変数が設定されていない場合、アプリケーションはエラーメッセージを表示して終了します。

### 操作手順

1. **起動**: アプリケーションを起動すると、自動的にSquadBeyondにログインし、グループ一覧を取得します
2. **グループを選択**: ドロップダウンから複製元のグループを選択します
3. **フォルダを選択**: 選択したグループ内のフォルダを選択します
4. **複製元を選択**: 選択したフォルダ内の記事を選択します
5. **新タイトルを入力**: 複製先の記事タイトルを入力します
6. **URL末尾を入力**: URL末尾を入力します（デフォルトで `copy-HHMMSS` 形式が自動生成されます）
7. **複製を実行**: 「複製を実行する」ボタンをクリックして複製処理を開始します

### ログ表示

画面下部のログエリアに、各操作の進行状況とエラーメッセージが表示されます。

## 注意事項

- **ログイン情報**: ログイン情報は環境変数（`SQUADBEYOND_EMAIL`、`SQUADBEYOND_PASSWORD`）から読み込まれます。セキュリティ上の理由から、コード内に直接記載することは避けてください
- **環境変数の設定**: アプリケーション起動前に必ず環境変数を設定してください。設定されていない場合、アプリケーションは正常に動作しません
- **ブラウザ表示**: アプリケーション実行中は、PlaywrightがChromiumブラウザを起動します（`headless=False`）。ブラウザウィンドウを閉じないでください
- **ネットワーク接続**: SquadBeyondへのアクセスにはインターネット接続が必要です
- **XPath依存**: 一部の操作でXPathを使用しているため、SquadBeyondのUIが変更された場合、動作しなくなる可能性があります

## トラブルシューティング

### .envファイルのパースエラー

`python-dotenv could not parse statement starting at line X` というエラーが表示される場合：

1. `.env`ファイルの形式を確認してください
2. 各行は `変数名=値` の形式である必要があります
3. 等号（`=`）の前後にスペースを入れないでください
4. コメントは `#` で始まる行に記述してください
5. 空行や不正な文字が含まれていないか確認してください

正しい形式の例：
```env
SQUADBEYOND_EMAIL=your_email@example.com
SQUADBEYOND_PASSWORD=your_password
```

間違った形式の例：
```env
SQUADBEYOND_EMAIL = your_email@example.com  # 等号の前後にスペースがある
SQUADBEYOND_PASSWORD="your_password"  # 引用符は不要（あっても問題ないが、パースエラーの原因になる場合がある）
```

### エラーが発生した場合

- ログエリアに表示されるエラーメッセージを確認してください
- ブラウザが正常に起動しているか確認してください
- ネットワーク接続を確認してください
- SquadBeyondのUIが変更されていないか確認してください

### Playwrightのインストールエラー

```bash
# 再インストールを試す
pip uninstall playwright
pip install playwright
playwright install chromium
```

### macOSバージョンエラー

`macOS 26 (2601) or later required, have instead 16 (1601)` というエラーが表示される場合：

これはPlaywrightのブラウザバイナリがmacOSのバージョンを正しく認識できていない可能性があります。以下の手順を試してください：

1. **Playwrightを最新版にアップグレード**
```bash
pip install --upgrade playwright
```

2. **ブラウザを再インストール**
```bash
playwright install --force chromium
```

3. **すべてのブラウザを再インストール（推奨）**
```bash
playwright install --force
```

4. **それでも解決しない場合**
   - Playwrightのバージョンを確認: `pip show playwright`
   - 最新の安定版を使用しているか確認してください
   - 問題が続く場合は、PlaywrightのGitHubリポジトリで既知の問題を確認してください

## ライセンス

このプロジェクトのライセンス情報は記載されていません。

