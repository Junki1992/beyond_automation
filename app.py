import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import datetime
import os
# Playwrightは後でインポート（tk.Tk()呼び出し後）

# .envファイルを読み込む
try:
    from dotenv import load_dotenv
    # スクリプトのディレクトリを基準に.envファイルのパスを取得
    script_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(script_dir, '.env')
    # load_dotenv()の戻り値でファイルが読み込まれたか確認
    loaded = load_dotenv(env_path)
    if not loaded:
        # パスを指定しない場合も試す（カレントディレクトリから）
        loaded = load_dotenv()
    if loaded:
        print(f".envファイルを読み込みました: {env_path}")
    else:
        print(f"警告: .envファイルが見つかりませんでした: {env_path}")
except ImportError:
    print("警告: python-dotenvがインストールされていません。環境変数から直接読み込みを試みます。")
except Exception as e:
    print(f"警告: .envファイルの読み込みでエラーが発生しました: {e}")
    print("環境変数から直接読み込みを試みます。")

class BeyondAutoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SquadBeyond 複製ツール - フォルダ取得修正版")
        self.root.geometry("600x900")
        self.root.configure(bg="#ffffff")

        self.pw = None
        self.browser = None
        self.context = None
        self.page = None

        container = tk.Frame(root, bg="#ffffff", padx=40, pady=20)
        container.pack(fill="both", expand=True)

        self.status_label = tk.Label(container, text="起動待機中...", font=("MS Gothic", 10, "bold"), bg="#ffffff", fg="#ff0000")
        self.status_label.pack(pady=(0, 10))

        tk.Label(container, text="2. グループを選択", font=("MS Gothic", 10, "bold"), bg="#ffffff").pack(anchor="w")
        self.parent_combo = ttk.Combobox(container, state="readonly")
        self.parent_combo.pack(fill="x", pady=5)
        self.parent_combo.bind("<<ComboboxSelected>>", self.scan_sub_folders)

        tk.Label(container, text="3. フォルダを選択", font=("MS Gothic", 10, "bold"), bg="#ffffff").pack(anchor="w")
        self.child_combo = ttk.Combobox(container, state="readonly")
        self.child_combo.pack(fill="x", pady=5)
        self.child_combo.bind("<<ComboboxSelected>>", self.scan_articles)

        tk.Label(container, text="4. 複製元を選択", font=("MS Gothic", 10, "bold"), bg="#ffffff").pack(anchor="w")
        self.target_combo = ttk.Combobox(container, state="readonly")
        self.target_combo.pack(fill="x", pady=5)

        tk.Label(container, text="5. 新タイトル", font=("MS Gothic", 10, "bold"), bg="#ffffff").pack(anchor="w")
        self.new_title_entry = tk.Entry(container, bd=1, relief="solid")
        self.new_title_entry.pack(fill="x", pady=5, ipady=3)

        tk.Label(container, text="6. URL末尾", font=("MS Gothic", 10, "bold"), bg="#ffffff").pack(anchor="w")
        self.dir_entry = tk.Entry(container, bd=1, relief="solid")
        self.dir_entry.pack(fill="x", pady=5, ipady=3)
        # デフォルトは空欄（refresh_url()は呼ばない）

        # ボタン用のフレーム
        button_frame = tk.Frame(root, bg="#ffffff")
        button_frame.pack(pady=10)
        
        self.reload_btn = tk.Button(button_frame, text="ページをリロード", command=self.reload_page,
                                   bg="#ffffff", font=("MS Gothic", 10, "bold"),
                                   relief="solid", bd=1, width=15, height=1)
        self.reload_btn.pack(side="left", padx=5)
        
        self.run_btn = tk.Button(button_frame, text="複製を実行する", command=self.run_automation, 
                                 bg="#ffffff", font=("MS Gothic", 12, "bold"), 
                                 relief="solid", bd=2, width=20, height=2)
        self.run_btn.pack(side="left", padx=5)

        self.log_area = scrolledtext.ScrolledText(root, width=65, height=15)
        self.log_area.pack(padx=40, pady=(5, 30))

        # アプリ終了時のクリーンアップ処理を設定
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 実行中フラグを初期化
        self._is_running = False
        self._is_reloading = False  # リロード処理中フラグ

        self.root.after(100, self.initial_scan)

    def refresh_url(self):
        self.dir_entry.delete(0, tk.END)
        self.dir_entry.insert(0, f"copy-{datetime.datetime.now().strftime('%H%M%S')}")

    def add_log(self, text):
        self.log_area.insert(tk.END, f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {text}\n")
        self.log_area.see(tk.END)
        self.root.update()

    def cleanup(self):
        """ブラウザとPlaywrightのリソースをクリーンアップ"""
        try:
            self.add_log("リソースをクリーンアップ中...")
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.pw:
                self.pw.stop()
            self.add_log("クリーンアップ完了")
        except Exception as e:
            print(f"クリーンアップ中にエラーが発生しました: {e}")

    def on_closing(self):
        """アプリ終了時の処理"""
        if hasattr(self, '_is_running') and self._is_running:
            if not messagebox.askokcancel("終了確認", "実行中の処理があります。終了しますか？"):
                return
        
        self.cleanup()
        self.root.destroy()

    def initial_scan(self):
        try:
            # 環境変数からログイン情報を取得
            email = os.getenv("SQUADBEYOND_EMAIL")
            password = os.getenv("SQUADBEYOND_PASSWORD")
            
            # デバッグ情報
            self.add_log(f"環境変数チェック: EMAIL={'設定済み' if email else '未設定'}, PASSWORD={'設定済み' if password else '未設定'}")
            
            if not email or not password:
                self.add_log("エラー: 環境変数が設定されていません")
                self.add_log("SQUADBEYOND_EMAIL と SQUADBEYOND_PASSWORD を設定してください")
                # .envファイルのパスを表示
                script_dir = os.path.dirname(os.path.abspath(__file__))
                env_path = os.path.join(script_dir, '.env')
                self.add_log(f".envファイルのパス: {env_path}")
                self.add_log(f".envファイルの存在確認: {os.path.exists(env_path)}")
                self.status_label.config(text="環境変数未設定", fg="#ff0000")
                messagebox.showerror("エラー", "環境変数が設定されていません\n\nSQUADBEYOND_EMAIL と SQUADBEYOND_PASSWORD を設定してください")
                return
            
            self.add_log("自動ログイン・スキャン開始...")
            # Playwrightを遅延インポート（tk.Tk()呼び出し後）
            from playwright.sync_api import sync_playwright
            self.pw = sync_playwright().start()
            self.browser = self.pw.chromium.launch(headless=False)
            self.context = self.browser.new_context()
            self.page = self.context.new_page()
            
            self.page.goto("https://app.squadbeyond.com/login")
            self.page.get_by_role("textbox", name="メールアドレス").fill(email)
            self.page.get_by_role("textbox", name="パスワード").fill(password)
            self.page.locator('button[type="submit"]').click()
            self.page.wait_for_timeout(1500)

            if "/users/teams" in self.page.url:
                self.page.get_by_role("button", name="ログイン").first.click()
                self.page.wait_for_timeout(1500)

            try:
                self.page.get_by_role("button", name="旧デザインに戻る").click(timeout=1000)
                self.page.wait_for_timeout(1000)
            except: pass

            groups = self.page.evaluate("""() => Array.from(document.querySelectorAll('#ts-sortableFolderGroupList p.MuiTypography-body1')).map(p => p.innerText.trim())""")
            self.parent_combo['values'] = sorted(list(set(groups)))
            
            self.status_label.config(text="自動スキャン完了", fg="#00aa00")
            self.add_log("準備完了。")
        except Exception as e:
            self.add_log(f"エラー: {e}")

    def scan_sub_folders(self, event):
        name = self.parent_combo.get()
        if not name:
            return
        
        self.add_log(f"{name} 展開...")
        try:
            # グループ一覧ページにいることを確認（必要に応じて戻る）
            # グループ一覧の要素が存在するか確認
            try:
                group_list = self.page.locator('#ts-sortableFolderGroupList')
                group_list.wait_for(state="visible", timeout=3000)
            except:
                self.add_log("警告: グループ一覧が見つかりません。ページをリロードしてください。")
                return
            
            # 既に展開されているグループの場合は、一度閉じてから再度開く
            # アクティブなコンテナを確認
            is_already_open = self.page.evaluate(f"""(groupName) => {{
                const containers = Array.from(document.querySelectorAll('div[id^=ts-sortableFolderGroupFolderList]'));
                const active = containers.find(c => c.offsetParent !== null);
                if (active) {{
                    const groupText = active.closest('div')?.querySelector('p.MuiTypography-body1')?.innerText.trim();
                    return groupText === groupName;
                }}
                return false;
            }}""", name)
            
            if is_already_open:
                self.add_log(f"{name} は既に展開されています。一度閉じてから再度開きます...")
                # 一度クリックして閉じる
                self.page.locator(f"#ts-sortableFolderGroupList p:has-text('{name}')").first.click()
                self.page.wait_for_timeout(500)
            
            # グループをクリックして展開
            group_element = self.page.locator(f"#ts-sortableFolderGroupList p:has-text('{name}')").first
            group_element.wait_for(state="visible", timeout=5000)
            group_element.click()
            self.page.wait_for_timeout(1000)  # 展開アニメーションを待つ
            
            # 【修正点】アクティブな子コンテナからのみ抽出
            folders = self.page.evaluate(f"""(groupName) => {{
                const containers = Array.from(document.querySelectorAll('div[id^=ts-sortableFolderGroupFolderList]'));
                const active = containers.find(c => c.offsetParent !== null);
                if (!active) {{
                    console.log('アクティブなコンテナが見つかりません');
                    return [];
                }}
                const folderElements = Array.from(active.querySelectorAll('p'));
                const folderNames = folderElements.map(p => p.innerText.trim()).filter(t => t && t !== groupName);
                console.log('取得したフォルダ:', folderNames);
                return folderNames;
            }}""", name)
            
            if not folders:
                self.add_log(f"警告: {name} のフォルダが見つかりませんでした")
                # デバッグ情報を追加
                debug_info = self.page.evaluate("""() => {{
                    const containers = Array.from(document.querySelectorAll('div[id^=ts-sortableFolderGroupFolderList]'));
                    return containers.map(c => ({{
                        visible: c.offsetParent !== null,
                        id: c.id,
                        text: c.innerText.trim().substring(0, 50)
                    }}));
                }}""")
                self.add_log(f"デバッグ情報: {debug_info}")
            else:
                self.child_combo['values'] = sorted(list(set(folders)))
                self.add_log(f"フォルダ取得成功: {len(folders)}個")
        except Exception as e:
            self.add_log(f"展開エラー: {e}")
            import traceback
            self.add_log(f"詳細: {traceback.format_exc()}")

    def scan_articles(self, event):
        name = self.child_combo.get()
        self.add_log(f"{name} の記事を取得中...")
        try:
            self.page.get_by_text(name, exact=True).first.click()
            self.page.wait_for_timeout(800)
            articles = self.page.evaluate("""() => Array.from(document.querySelectorAll('table tr td:first-child p')).map(p => p.innerText.split('\\n')[0].trim())""")
            self.target_combo['values'] = sorted(list(set(articles)))
            self.add_log("完了。")
        except Exception as e:
            self.add_log(f"記事取得エラー: {e}")

    def reload_page(self):
        """ページをリロードして、グループ一覧を再取得し、選択と入力をリセット"""
        # リロード処理の重複実行を防止
        if hasattr(self, '_is_reloading') and self._is_reloading:
            self.add_log("警告: 既にリロード処理実行中です。完了をお待ちください。")
            return
        
        # 複製処理実行中はリロードをスキップ
        if hasattr(self, '_is_running') and self._is_running:
            self.add_log("警告: 複製処理実行中です。完了後にリロードしてください。")
            return
        
        if not self.page:
            self.add_log("エラー: ページが初期化されていません")
            return
        
        self._is_reloading = True
        try:
            self.add_log("ページをリロード中...")
            self.status_label.config(text="リロード中...", fg="#ff9900")
            
            # リロード中はボタンを一時的に無効化
            self.reload_btn.config(state="disabled")
            self.run_btn.config(state="disabled")
            
            # 現在のURLを取得してリロード
            current_url = self.page.url
            self.page.reload()
            self.page.wait_for_timeout(2000)
            
            # 旧デザインに戻るボタンがあればクリック
            try:
                self.page.get_by_role("button", name="旧デザインに戻る").click(timeout=1000)
                self.page.wait_for_timeout(1000)
            except:
                pass
            
            # グループ一覧を再取得
            groups = self.page.evaluate("""() => Array.from(document.querySelectorAll('#ts-sortableFolderGroupList p.MuiTypography-body1')).map(p => p.innerText.trim())""")
            self.parent_combo['values'] = sorted(list(set(groups)))
            
            # すべての選択をクリア（必ず実行されるように順序を明確化）
            self.parent_combo.set('')  # グループ選択をクリア
            self.child_combo.set('')  # フォルダ選択をクリア
            self.child_combo['values'] = []  # フォルダ選択肢をクリア
            self.target_combo.set('')  # 記事選択をクリア
            self.target_combo['values'] = []  # 記事選択肢をクリア
            
            # 入力フィールドをクリア（必ず実行されるように）
            self.new_title_entry.delete(0, tk.END)  # タイトルをクリア
            self.dir_entry.delete(0, tk.END)  # URL末尾をクリア
            
            self.status_label.config(text="リロード完了", fg="#00aa00")
            self.add_log("ページのリロードが完了しました（選択と入力もリセットされました）")
        except Exception as e:
            self.add_log(f"リロードエラー: {e}")
            self.status_label.config(text="リロードエラー", fg="#ff0000")
        finally:
            # リロード完了後はフラグをリセットしてボタンを再有効化
            self._is_reloading = False
            self.reload_btn.config(state="normal")
            self.run_btn.config(state="normal")

    def run_automation(self):
        # 実行中の重複実行を防止
        if hasattr(self, '_is_running') and self._is_running:
            self.add_log("警告: 既に実行中のため、新しい実行をスキップします")
            return
        
        self._is_running = True
        # 実行中はボタンを無効化
        self.run_btn.config(state="disabled")
        self.reload_btn.config(state="disabled")
        
        try:
            self.add_log("複製を実行します...")
            # 入力値のバリデーション
            target_article = self.target_combo.get().strip()
            if not target_article:
                self.add_log("エラー: 複製元の記事が選択されていません")
                messagebox.showerror("エラー", "複製元の記事を選択してください")
                self._is_running = False
                self.run_btn.config(state="normal")
                self.reload_btn.config(state="normal")
                return
            
            title = self.new_title_entry.get().strip()
            url = self.dir_entry.get().strip()
            
            # タイトルが空欄の場合の警告（必須ではないが推奨）
            if not title:
                response = messagebox.askyesno("警告", "新タイトルが空欄です。\n\n空欄のまま続行しますか？\n（推奨: タイトルを入力してください）")
                if not response:
                    self.add_log("ユーザーがタイトル未入力でキャンセルしました")
                    self._is_running = False
                    self.run_btn.config(state="normal")
                    self.reload_btn.config(state="normal")
                    return
                self.add_log("警告: タイトルが空欄のまま続行します")
            
            if not url:
                self.add_log("エラー: URL末尾が空欄です")
                messagebox.showerror("エラー", "URL末尾を入力してください")
                self._is_running = False
                self.run_btn.config(state="normal")
                self.reload_btn.config(state="normal")
                return
            
            self.add_log(f"複製元記事: {target_article}")
            self.add_log(f"新タイトル: {title if title else '(空欄)'}")
            self.add_log(f"URL末尾: {url}")
            
            # 選択された記事名に一致するテーブル行を見つけて、その行の3点リーダーボタンをクリック
            row_index = self.page.evaluate(f"""(articleName) => {{
                const rows = Array.from(document.querySelectorAll('table tbody tr'));
                for (let i = 0; i < rows.length; i++) {{
                    const firstCell = rows[i].querySelector('td:first-child p');
                    if (firstCell) {{
                        const cellText = firstCell.innerText.split('\\n')[0].trim();
                        if (cellText === articleName) {{
                            return i + 1; // 1-indexed for XPath
                        }}
                    }}
                }}
                return -1; // 見つからない場合
            }}""", target_article)
            
            if row_index == -1:
                self.add_log(f"エラー: 記事 '{target_article}' が見つかりませんでした")
                messagebox.showerror("エラー", f"記事 '{target_article}' がテーブル内に見つかりませんでした")
                self._is_running = False
                self.run_btn.config(state="normal")
                self.reload_btn.config(state="normal")
                return
            
            # 見つかった行の3点リーダーボタンをクリック
            dots_button = self.page.locator(f'table tbody tr:nth-child({row_index}) td:nth-child(13) div div button').first
            dots_button.wait_for(state="visible", timeout=5000)
            dots_button.click()
            self.add_log(f"記事 '{target_article}' の3点リーダーをクリックしました")
            self.page.wait_for_timeout(300)

            # メニュー内の「複製」リンクを探す（XPathではなく、テキストとrole属性で検索）
            try:
                # まず、メニューが表示されるまで待つ
                menu = self.page.locator('ul[role="menu"]')
                menu.wait_for(state="visible", timeout=5000)
                
                # メニュー内の「複製」というテキストを持つリンクを探す
                duplicate_link = menu.locator('li a:has-text("複製")')
                duplicate_link.wait_for(state="visible", timeout=5000)
                duplicate_link.click()
                self.add_log("複製メニューをクリックしました")
            except Exception as e:
                # フォールバック: 5番目のメニュー項目をクリック（従来の方法）
                self.add_log(f"警告: テキスト検索で見つからなかったため、フォールバック方法を使用: {e}")
                try:
                    duplicate_link = self.page.locator('ul[role="menu"] li:nth-child(5) a')
                    duplicate_link.wait_for(state="visible", timeout=5000)
                    duplicate_link.click()
                    self.add_log("メニューをクリック（フォールバック）")
                except Exception as e2:
                    self.add_log(f"エラー: メニュー項目が見つかりませんでした: {e2}")
                    raise Exception(f"複製メニューのクリックに失敗しました: {e2}")

            # 入力画面（Playwrightのfill()メソッドを使用）
            popup = self.page.locator('div[role="dialog"]')
            popup.wait_for(state="visible", timeout=10000)
            self.add_log("ポップアップを確認しました")
            
            self.add_log(f"指定タイトル: {title if title else '(空欄)'} / URL: {url} を書き込み中...")
            
            # タイトル入力欄（1番目のinput）
            title_input = popup.locator('input').first
            title_input.wait_for(state="visible", timeout=5000)
            title_input.click()
            # 既存の値を完全にクリア
            title_input.press("Control+a")
            title_input.press("Backspace")
            self.page.wait_for_timeout(200)
            title_input.fill(title)
            self.page.wait_for_timeout(500)
            self.add_log("ページ名を入力しました")
            
            # URL入力欄（2番目のinput）
            dir_input = popup.locator('input').nth(1)
            dir_input.wait_for(state="visible", timeout=5000)
            dir_input.click()
            self.page.wait_for_timeout(200)
            
            # 既存の値を完全にクリアしてから新しい値を設定
            # Reactの状態を確実に更新するため、evaluate()を使用
            self.page.evaluate(f"""(url) => {{
                const inputs = Array.from(document.querySelectorAll('div[role="dialog"] input')).filter(i => i.offsetHeight > 0);
                if (inputs.length >= 2) {{
                    const urlInput = inputs[1];
                    // 既存の値を完全にクリア
                    urlInput.value = '';
                    // Reactの状態を更新
                    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                    nativeInputValueSetter.call(urlInput, url);
                    // イベントを発火
                    urlInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    urlInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    urlInput.dispatchEvent(new Event('blur', {{ bubbles: true }}));
                }}
            }}""", url)
            
            self.page.wait_for_timeout(1000)
            self.add_log(f"ディレクトリ名を入力しました: {url}")
            
            # バリデーションが完了するまで待機
            self.page.wait_for_timeout(2000)
            
            # エラーメッセージが表示されていないか確認
            error_detected = False
            try:
                error_message = popup.locator('text=配信URL設定は不正な値です')
                if error_message.is_visible(timeout=2000):
                    error_detected = True
                    self.add_log("警告: バリデーションエラーが検出されました")
                    # エラーが表示されている場合、Playwrightのfill()メソッドで再試行
                    dir_input.click()
                    self.page.wait_for_timeout(200)
                    dir_input.press("Control+a")
                    dir_input.press("Backspace")
                    self.page.wait_for_timeout(300)
                    dir_input.fill(url)
                    self.page.wait_for_timeout(2000)
                    # 再度エラーチェック
                    if error_message.is_visible(timeout=1000):
                        self.add_log("エラー: バリデーションエラーが解消されませんでした")
                        raise Exception("URLバリデーションエラー: 配信URL設定は不正な値です")
                    else:
                        self.add_log("バリデーション成功（再試行後）")
                else:
                    self.add_log("バリデーション成功")
            except Exception as e:
                if "バリデーションエラー" in str(e):
                    raise
                # エラーメッセージが見つからない場合は成功とみなす
                self.add_log("バリデーション確認完了")
            
            # エラーが解消されていない場合は処理を中断
            if error_detected:
                try:
                    if popup.locator('text=配信URL設定は不正な値です').is_visible(timeout=500):
                        raise Exception("URLバリデーションエラー: 配信URL設定は不正な値です")
                except:
                    pass
            
            # 「複製する」ボタンをクリック
            submit_btn = popup.get_by_role("button", name="複製する")
            submit_btn.click()
            self.add_log("複製確定ボタンをクリックしました")

            # 複製成功の確認
            self.add_log("複製処理の完了を待機中...")
            try:
                # ポップアップが非表示になるまで待つ（最大10秒）
                popup.wait_for(state="hidden", timeout=10000)
                self.add_log("ポップアップが閉じられました")
            except Exception as e:
                self.add_log(f"警告: ポップアップの非表示確認でタイムアウト: {e}")
                # タイムアウトしても続行（処理が完了している可能性がある）
            
            # 追加の待機時間（ページの更新を待つ）
            self.page.wait_for_timeout(2000)
            
            # エラーメッセージが表示されていないか確認
            error_found = False
            try:
                # 一般的なエラーメッセージをチェック
                error_selectors = [
                    'text=エラー',
                    'text=失敗',
                    'text=error',
                    '[role="alert"]',
                    '.MuiAlert-root'  # Material-UIのアラート
                ]
                for selector in error_selectors:
                    try:
                        error_elem = self.page.locator(selector).first
                        if error_elem.is_visible(timeout=1000):
                            error_text = error_elem.inner_text()
                            self.add_log(f"エラーメッセージが検出されました: {error_text}")
                            error_found = True
                            break
                    except:
                        continue
            except Exception as e:
                self.add_log(f"エラーチェック中に例外が発生: {e}")
            
            if error_found:
                raise Exception("複製処理中にエラーが検出されました")
            
            # 成功を確認（テーブルに新しい記事が追加されているか、またはURLが変更されているか）
            # ここでは簡易的に、エラーがなければ成功とみなす
            self.add_log(f"【成功】複製元: {target_article} → 新タイトル: {title} で複製を完了しました")
            messagebox.showinfo("成功", f"複製完了\n\n複製元: {target_article}\n新タイトル: {title}")
            self.refresh_url()
        except Exception as e:
            import traceback
            error_type = type(e).__name__
            error_message = str(e)
            
            # エラー種別に応じた詳細メッセージ
            if "バリデーションエラー" in error_message or "URLバリデーションエラー" in error_message:
                detailed_msg = f"バリデーションエラー\n\n{error_message}\n\nURL末尾の形式を確認してください。"
            elif "タイムアウト" in error_message or "timeout" in error_message.lower():
                detailed_msg = f"タイムアウトエラー\n\n{error_message}\n\nページの読み込みに時間がかかっています。ネットワーク接続を確認してください。"
            elif "見つかりません" in error_message or "not found" in error_message.lower():
                detailed_msg = f"要素が見つかりません\n\n{error_message}\n\nページの構造が変更された可能性があります。"
            elif "複製メニュー" in error_message:
                detailed_msg = f"メニュー操作エラー\n\n{error_message}\n\nページをリロードして再試行してください。"
            else:
                detailed_msg = f"エラーが発生しました\n\n種類: {error_type}\nメッセージ: {error_message}"
            
            # ログに詳細情報を記録
            self.add_log(f"【エラー】種類: {error_type}")
            self.add_log(f"【エラー】メッセージ: {error_message}")
            self.add_log(f"【エラー】詳細:\n{traceback.format_exc()}")
            
            # ユーザーには分かりやすいメッセージを表示
            messagebox.showerror("エラー", detailed_msg)
        finally:
            # 実行完了後はボタンを再有効化
            self._is_running = False
            self.run_btn.config(state="normal")
            self.reload_btn.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = BeyondAutoApp(root)
    root.mainloop()
