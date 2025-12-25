#!/bin/bash
# Python 3.13用のvenvを作成し、playwrightをインストールするスクリプト

echo "Python 3.13用のvenvを作成中..."
/opt/homebrew/bin/python3.13 -m venv venv313

echo "venvをアクティブ化中..."
source venv313/bin/activate

echo "playwrightをインストール中..."
pip install playwright

echo "playwrightブラウザをインストール中..."
playwright install

echo "完了！以下のコマンドでapp.pyを実行できます："
echo "  source venv313/bin/activate"
echo "  python app.py"

