import re
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    
    # 1. ログイン（2回クリック維持）
    page.goto("https://app.squadbeyond.com/")
    page.get_by_role("textbox", name="メールアドレス").fill("youxiqiantian492@gmail.com")
    page.get_by_role("textbox", name="パスワード").fill("kedGAe4KtKA64J_")
    page.get_by_role("button", name="ログイン").click()
    page.get_by_role("button", name="ログイン").click()

    # 2. 画面遷移（ポップアップ閉じる ＆ 旧デザインへ）
    try:
        page.get_by_role("button", name="閉じる").first.click(timeout=5000)
    except:
        pass
    page.get_by_role("button", name="旧デザインに戻る").click()
    page.wait_for_timeout(2000)

    # 3. フォルダ展開
    page.locator('xpath=//*[@id="ts-sortableFolderGroupList"]/div[6]/div/div[1]/div').click()
    page.wait_for_timeout(2000)
    
    # 4. 記事を物理的にクリック（3点リーダー有効化のため）
    target_article_name = "【新】P3-デマンド"
    article_element = page.get_by_text(target_article_name, exact=True)
    article_element.wait_for(state="visible", timeout=10000)
    article_element.click() 
    print("記事を選択しました。")
    page.wait_for_timeout(1000)

    # 5. 3点リーダーをクリック
    menu_button = page.locator('xpath=//*[@id="root"]/div[2]/div[2]/div[2]/div/div/div[2]/div[2]/div[3]/div/table/tbody/tr[7]/td[13]/div/div[1]/button')
    menu_button.click()
    print("3点リーダーをクリックしました。")
    
    # 6. 【修正】複製メニューをクリック
    # 文字指定ではなく、メニュー内の5番目の項目（複製）を絶対パスで狙います
    # ポップアップを確実に出現させます
    page.wait_for_timeout(1000) # メニューの描画待ち
    duplicate_option = page.locator('ul[role="menu"] li:nth-child(5)')
    duplicate_option.wait_for(state="visible", timeout=5000)
    duplicate_option.click()
    print("複製メニューをクリックしました。ポップアップ出現を待ちます。")

    # --- 7. ポップアップ内への入力 ---
    # 白い箱（dialog）が出現するのを待つ
    popup = page.locator('div[role="dialog"]')
    popup.wait_for(state="visible", timeout=10000)
    print("ポップアップを確認しました。")

    # スクショに基づき、ポップアップ内の最初の入力欄を直接狙う
    # input[placeholder="beyondページ名"] を使うとタイムアウトすることがあるため
    # inputタグそのものを指定
    title_input = popup.locator('input').first
    title_input.wait_for(state="visible", timeout=5000)
    title_input.click()
    title_input.fill("") # クリア
    title_input.fill("【複製】" + target_article_name)
    print("ページ名を入力しました。")
    # --- 7. beyondページ名の入力 ---
    popup = page.locator('div[role="dialog"]')
    popup.wait_for(state="visible", timeout=10000)

    # 1番目のinput（ページ名）
    title_input = popup.locator('input').first
    title_input.fill("【複製】" + target_article_name)

    # --- 8. ディレクトリ（URL末尾）の入力 ---
    # 2番目のinput（ディレクトリ）を狙い撃ちします
    # スクリーンショットの構造上、2番目の入力欄がこれに該当します
    dir_input = popup.locator('input').nth(1) 
    
    dir_input.wait_for(state="visible", timeout=5000)
    dir_input.click()
    
    # 重複エラーを避けるため、現在時刻を末尾に付与した英数字を入力します
    import datetime
    unique_id = datetime.datetime.now().strftime("%H%M%S")
    dir_name = f"copy-{unique_id}"
    
    dir_input.fill(dir_name)
    print(f"ディレクトリ名を入力しました: {dir_name}")
    
    # 8. 「複製する」ボタンをクリックして確定
    submit_btn = popup.get_by_role("button", name="複製する")
    submit_btn.click()
    print("複製確定ボタンをクリックしました。")

    print("全工程完了。ブラウザを一時停止します。")
    page.wait_for_timeout(3000)
    page.pause()

    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)