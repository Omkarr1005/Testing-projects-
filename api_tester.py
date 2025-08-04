import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import time
import threading
import json
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

SECURITY_HEADERS = [
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "X-Content-Type-Options",
    "X-Frame-Options",
]

test_history = []

sample_apis = {
    "https://reqres.in/api/users": "GET",
    "https://jsonplaceholder.typicode.com/posts": "GET",
    "https://jsonplaceholder.typicode.com/comments": "GET",
    "https://reqres.in/api/users/2": "GET",
    "https://api.openweathermap.org/data/2.5/weather?q=London&appid=demo": "GET",
    "https://gorest.co.in/public/v2/users": "GET",
    "https://petstore.swagger.io/v2/pet": "GET",
    "https://api.agify.io?name=michael": "GET",
    "https://api.genderize.io?name=lucy": "GET",
    "https://api.nationalize.io?name=nathaniel": "GET",
    "https://dog.ceo/api/breeds/image/random": "GET",
    "https://catfact.ninja/fact": "GET",
    "https://official-joke-api.appspot.com/random_joke": "GET",
    "https://randomuser.me/api/": "GET",
    "https://jsonplaceholder.typicode.com/posts": "POST",
    "https://jsonplaceholder.typicode.com/posts/1": "PUT",
    "https://jsonplaceholder.typicode.com/posts/1": "DELETE"
}

class APITester(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🚀 API Testing Tool")
        self.geometry("1200x800")
        self.is_dark = True

        self.style = ttk.Style(self)
        self.set_theme()

        self.create_widgets()
        self.bind("<Configure>", self.on_resize)

    def set_theme(self):
        theme = {
            "dark": {
                "bg": "#000000", "fg": "white", "entrybg": "#0F3460",
                "button": "#0F3460", "button_active": "#16213E",
                "progress": "#00FFAB"
            },
            "light": {
                "bg": "#F0F0F0", "fg": "black", "entrybg": "white",
                "button": "#0078D7", "button_active": "#005BB5",
                "progress": "#4CAF50"
            }
        }

        scheme = theme["dark"] if self.is_dark else theme["light"]
        self.configure(bg=scheme["bg"])
        self.style.theme_use("clam")

        self.style.configure("TLabel", font=("Segoe UI", 11), background=scheme["bg"], foreground=scheme["fg"])
        self.style.configure("TButton", font=("Segoe UI", 10, "bold"), background=scheme["button"], foreground="white", padding=6)
        self.style.map("TButton", background=[('active', scheme["button_active"])])
        self.style.configure("TEntry", font=("Segoe UI", 11), fieldbackground=scheme["entrybg"], foreground=scheme["fg"])
        self.style.configure("TCombobox", font=("Segoe UI", 11), fieldbackground=scheme["entrybg"], foreground=scheme["fg"])
        self.style.configure("TCheckbutton", background=scheme["bg"], foreground=scheme["fg"])
        self.style.configure("TProgressbar", troughcolor=scheme["entrybg"], background=scheme["progress"], thickness=10)

    def toggle_theme(self):
        self.is_dark = not self.is_dark
        self.set_theme()
        self.update_all_colors()

    def update_all_colors(self):
        bg = "#0F3460" if self.is_dark else "white"
        fg = "white" if self.is_dark else "black"
        self.json_text.config(bg=bg, fg=fg, insertbackground=fg)
        self.report_area.config(bg=bg, fg=fg, insertbackground=fg)

    def create_widgets(self):
        self.main_frame = ttk.Frame(self, padding=15)
        self.main_frame.pack(fill="both", expand=True)

        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(7, weight=1)

        ttk.Label(self.main_frame, text="🔽 Choose API:").grid(row=0, column=0, sticky="w")
        self.api_var = tk.StringVar()
        self.api_menu = ttk.Combobox(self.main_frame, textvariable=self.api_var, values=list(sample_apis.keys()), width=65)
        self.api_menu.grid(row=0, column=1, columnspan=2, sticky="we")
        self.api_menu.bind("<<ComboboxSelected>>", self.on_api_selected)

        self.theme_button = ttk.Button(self.main_frame, text="🌗 Toggle Theme", command=self.toggle_theme)
        self.theme_button.grid(row=0, column=3, sticky="e")

        ttk.Label(self.main_frame, text="🔗 API URL (Editable):").grid(row=1, column=0, sticky="w")
        self.url_entry = ttk.Entry(self.main_frame, width=65)
        self.url_entry.grid(row=1, column=1, columnspan=3, sticky="we")

        ttk.Label(self.main_frame, text="📡 HTTP Method:").grid(row=2, column=0, sticky="w")
        self.method_var = tk.StringVar(value="GET")
        self.method_menu = ttk.Combobox(self.main_frame, textvariable=self.method_var, values=["GET", "POST", "PUT", "DELETE"], state="readonly")
        self.method_menu.grid(row=2, column=1, sticky="w")

        self.auth_var = tk.BooleanVar()
        self.auth_check = ttk.Checkbutton(self.main_frame, text="Use Auth", variable=self.auth_var)
        self.auth_check.grid(row=2, column=2, sticky="e")

        ttk.Label(self.main_frame, text="🔑 Token/Auth (Bearer or Basic):").grid(row=3, column=0, sticky="w")
        self.token_entry = ttk.Entry(self.main_frame, width=65)
        self.token_entry.grid(row=3, column=1, columnspan=3, sticky="we")

        ttk.Label(self.main_frame, text="📝 JSON Body (POST/PUT):").grid(row=4, column=0, sticky="nw")
        self.json_text = scrolledtext.ScrolledText(self.main_frame, height=5, width=80, wrap=tk.WORD)
        self.json_text.grid(row=4, column=1, columnspan=3, sticky="we")

        self.test_button = ttk.Button(self.main_frame, text="🚀 Test API", command=self.run_tests)
        self.test_button.grid(row=5, column=0, columnspan=4, pady=5)

        self.progress = ttk.Progressbar(self.main_frame, mode="indeterminate")
        self.progress.grid(row=6, column=0, columnspan=4, sticky="we")

        self.report_area = scrolledtext.ScrolledText(self.main_frame, wrap=tk.WORD, width=100, height=15, font=("Courier", 12))
        self.report_area.grid(row=7, column=0, columnspan=4, pady=10, sticky="nsew")

        self.history_button = ttk.Button(self.main_frame, text="📜 View Past Results", command=self.show_history)
        self.history_button.grid(row=8, column=0, sticky="w")

        self.canvas_frame = ttk.Frame(self.main_frame)
        self.canvas_frame.grid(row=9, column=0, columnspan=4, pady=10, sticky="nsew")

        self.update_all_colors()

    def on_resize(self, event):
        self.report_area.config(width=max(60, int(self.winfo_width() / 12)))
        self.json_text.config(width=max(60, int(self.winfo_width() / 12)))

    def on_api_selected(self, event):
        selected_api = self.api_var.get()
        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, selected_api)
        if selected_api in sample_apis:
            self.method_var.set(sample_apis[selected_api])

    def run_tests(self):
        self.test_button.config(state=tk.DISABLED)
        self.progress.start()
        self.report_area.delete(1.0, tk.END)
        threading.Thread(target=self.perform_tests, daemon=True).start()

    def perform_tests(self):
        url = self.url_entry.get().strip()
        method = self.method_var.get().strip().upper()
        headers = {}

        if self.auth_var.get() and self.token_entry.get().strip():
            headers["Authorization"] = self.token_entry.get().strip()

        data = None
        if method in ["POST", "PUT"]:
            try:
                data = json.loads(self.json_text.get("1.0", tk.END).strip())
            except:
                messagebox.showerror("JSON Error", "Invalid JSON format.")
                self.reset_ui()
                return

        if not url:
            messagebox.showerror("⚠ Error", "Please enter an API URL.")
            self.reset_ui()
            return

        self.append_report(f"🌍 Testing API: {url} ({method})\n\n")

        functionality = self.test_functionality(url, method, headers, data)
        reliability, avg_time = self.test_reliability(url, method, headers, data)
        security = self.test_security(url, method, headers, data)
        performance = max(0, 100 - avg_time / 10)
        performance = round(performance, 2)

        self.append_report("\n✅ API testing complete.\n")
        self.append_report(f"🛠 Functionality Score: {functionality}/100\n")
        self.append_report(f"🔄 Reliability Score: {reliability}/100 (Avg: {avg_time:.2f} ms)\n")
        self.append_report(f"🚀 Performance Score: {performance}/100\n")
        self.append_report(f"🔒 Security Score: {security}/100\n")

        test_history.append({
            "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "URL": url,
            "Method": method,
            "Functionality Score": functionality,
            "Reliability Score": reliability,
            "Performance Score": performance,
            "Security Score": security
        })

        self.after(0, self.show_graph, [functionality, reliability, performance, security])
        self.reset_ui()

    def test_functionality(self, url, method, headers, data):
        try:
            response = requests.request(method, url, headers=headers, json=data)
            return 100 if response.status_code == 200 else 50
        except:
            return 0

    def test_reliability(self, url, method, headers, data):
        response_times = []
        for _ in range(3):
            try:
                start = time.time()
                requests.request(method, url, headers=headers, json=data)
                response_times.append((time.time() - start) * 1000)
            except:
                response_times.append(None)

        avg_time = sum(filter(None, response_times)) / len(response_times) if response_times else 1000
        reliability_score = max(0, 100 - avg_time / 10)
        return round(reliability_score, 2), avg_time

    def test_security(self, url, method, headers, data):
        try:
            response = requests.request(method, url, headers=headers, json=data)
            https_check = 100 if url.startswith("https://") else 50
            headers_score = sum(25 for header in SECURITY_HEADERS if header in response.headers)
            return min(100, https_check + headers_score)
        except:
            return 0

    def show_graph(self, scores):
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

        labels = ["Functionality", "Reliability", "Performance", "Security"]

        # Theme-based styling
        if self.is_dark:
            bg_color = "#1A1A2E"
            text_color = "white"
            bar_color = "green"
        else:
            bg_color = "white"
            text_color = "black"
            bar_color = "#4CAF50"  # Default green for light theme

        fig, ax = plt.subplots(figsize=(6, 4))
        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor(bg_color)
        ax.bar(labels, scores, color=bar_color)

        ax.set_ylabel("Score (0-100)", color=text_color)
        ax.set_title("API Test Scores", color=text_color)
        ax.set_ylim([0, 100])
        ax.tick_params(axis='x', colors=text_color)
        ax.tick_params(axis='y', colors=text_color)

        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        canvas.draw()

    def append_report(self, text):
        self.report_area.insert(tk.END, text)
        self.report_area.see(tk.END)

    def reset_ui(self):
        self.test_button.config(state=tk.NORMAL)
        self.progress.stop()

    def show_history(self):
        hist_text = ""
        for h in test_history:
            hist_text += f"{h['Time']} | {h['Method']} | {h['URL']}\n"
            hist_text += f"Functionality: {h['Functionality Score']} | Reliability: {h['Reliability Score']} | Performance: {h['Performance Score']} | Security: {h['Security Score']}\n\n"
        messagebox.showinfo("📜 Past Results", hist_text or "No past results yet.")

if __name__ == "__main__":
    app = APITester()
    app.mainloop()
