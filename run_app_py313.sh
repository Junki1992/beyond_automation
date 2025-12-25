#!/bin/bash
# Python 3.13のvenvを使用してapp.pyを実行

if [ ! -d "venv313" ]; then
    echo "エラー: venv313が見つかりません。"
    echo "まず setup_py313.sh を実行してください。"
    exit 1
fi

source venv313/bin/activate
python app.py
