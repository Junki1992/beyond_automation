#!/bin/bash
# Playwrightキャッシュを移動してからapp.pyを実行

PLAYWRIGHT_CACHE="$HOME/Library/Caches/ms-playwright"
PLAYWRIGHT_BACKUP="/tmp/ms-playwright-backup-$$"

# Playwrightキャッシュを移動
if [ -d "$PLAYWRIGHT_CACHE" ]; then
    echo "[DEBUG] Playwrightキャッシュを移動中: $PLAYWRIGHT_CACHE -> $PLAYWRIGHT_BACKUP"
    mv "$PLAYWRIGHT_CACHE" "$PLAYWRIGHT_BACKUP"
    echo "[DEBUG] 移動完了"
fi

# 環境変数を設定
export MACOSX_DEPLOYMENT_TARGET=11.0
export DYLD_FALLBACK_LIBRARY_PATH=""
export DYLD_LIBRARY_PATH=""
unset DYLD_INSERT_LIBRARIES

# app.pyを実行
cd "$(dirname "$0")"
python app.py
EXIT_CODE=$?

# エラー発生時もPlaywrightキャッシュを復元
if [ -d "$PLAYWRIGHT_BACKUP" ] && [ ! -d "$PLAYWRIGHT_CACHE" ]; then
    echo "[DEBUG] Playwrightキャッシュを復元中..."
    mv "$PLAYWRIGHT_BACKUP" "$PLAYWRIGHT_CACHE"
    echo "[DEBUG] 復元完了"
fi

exit $EXIT_CODE

