import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import datetime
from playwright.sync_api import sync_playwright

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
        self.refresh_url()

        self.run_btn = tk.Button(root, text="複製を実行する", command=self.run_automation, 
                                 bg="#ffffff", font=("MS Gothic", 12, "bold"), 
                                 relief="solid", bd=2, width=30, height=2)
        self.run_btn.pack(pady=20)

        self.log_area = scrolledtext.ScrolledText(root, width=65, height=15)
        self.log_area.pack(padx=40, pady=(5, 30))

        self.root.after(100, self.initial_scan)

    def refresh_url(self):
        self.dir_entry.delete(0, tk.END)
        self.dir_entry.insert(0, f"copy-{datetime.datetime.now().strftime('%H%M%S')}")

    def add_log(self, text):
        self.log_area.insert(tk.END, f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {text}\n")
        self.log_area.see(tk.END)
        self.root.update()

    def initial_scan(self):
        try:
            self.add_log("自動ログイン・スキャン開始...")
            self.pw = sync_playwright().start()
            self.browser = self.pw.chromium.launch(headless=False)
            self.context = self.browser.new_context()
            self.page = self.context.new_page()
            
            self.page.goto("https://app.squadbeyond.com/login")
            self.page.get_by_role("textbox", name="メールアドレス").fill("youxiqiantian492@gmail.com")
            self.page.get_by_role("textbox", name="パスワード").fill("kedGAe4KtKA64J_")
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
        self.add_log(f"{name} 展開...")
        try:
            self.page.locator(f"#ts-sortableFolderGroupList p:has-text('{name}')").first.click()
            self.page.wait_for_timeout(800)
            
            # 【修正点】アクティブな子コンテナからのみ抽出
            folders = self.page.evaluate(f"""(groupName) => {{
                const containers = Array.from(document.querySelectorAll('div[id^=ts-sortableFolderGroupFolderList]'));
                const active = containers.find(c => c.offsetParent !== null);
                if (!active) return [];
                return Array.from(active.querySelectorAll('p')).map(p => p.innerText.trim()).filter(t => t && t !== groupName);
            }}""", name)
            
            self.child_combo['values'] = sorted(list(set(folders)))
            self.add_log("フォルダ取得成功。")
        except Exception as e:
            self.add_log(f"展開エラー: {e}")

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

    def run_automation(self):
        self.add_log("複製を実行します...")
        try:
            xpath_dots = '//*[@id="root"]/div[2]/div[2]/div[2]/div/div/div[2]/div[2]/div[3]/div/table/tbody/tr[2]/td[13]/div/div[1]/button'
            self.page.locator(f"xpath={xpath_dots}").click()
            self.page.wait_for_timeout(300)

            xpath_menu = '/html/body/div[9]/div[3]/ul/li[5]/a'
            self.page.locator(f"xpath={xpath_menu}").click()
            self.page.wait_for_timeout(500)

            self.page.evaluate(f"""(arg) => {{
                const inputs = Array.from(document.querySelectorAll('div[role="dialog"] input')).filter(i => i.offsetHeight > 0);
                const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                setter.call(inputs[0], arg.t);
                setter.call(inputs[1], arg.u);
                inputs[0].dispatchEvent(new Event('input', {{ bubbles: true }}));
                inputs[1].dispatchEvent(new Event('input', {{ bubbles: true }}));
            }}""", {"t": self.new_title_entry.get(), "u": self.dir_entry.get()})
            
            self.page.wait_for_timeout(300)
            
            try:
                self.page.get_by_role("button", name="複製する").click(timeout=1000)
            except:
                self.page.locator('xpath=//*[@id=":r9i:"]/div[3]/button').click()

            self.page.wait_for_timeout(1500)
            self.add_log("複製成功")
            self.refresh_url()
            messagebox.showinfo("成功", "複製完了しました")
        except Exception as e:
            self.add_log(f"エラー: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = BeyondAutoApp(root)
    root.mainloop()