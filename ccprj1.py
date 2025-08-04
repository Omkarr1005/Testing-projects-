import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import time
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Security headers to check
SECURITY_HEADERS = [
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "X-Content-Type-Options",
    "X-Frame-Options",
]

# Store test history
test_history = []


class APITester(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("\U0001F680 API Testing Tool")
        self.geometry("1000x750")
        self.configure(bg="#2E2E2E")

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TLabel", font=("Arial", 12), background="#2E2E2E", foreground="white")
        self.style.configure("TButton", font=("Arial", 11, "bold"), background="#0078D7", foreground="white", padding=6)
        self.style.configure("TEntry", font=("Arial", 11), fieldbackground="#1E1E1E", foreground="white")
        self.style.configure("TCombobox", font=("Arial", 11), fieldbackground="#1E1E1E", foreground="white")
        self.style.configure("TProgressbar", troughcolor="#444", background="green", thickness=10)

        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self, padding=15)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="🔗 API URL:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.url_entry = ttk.Entry(frame, width=65)
        self.url_entry.grid(row=0, column=1, padx=5, pady=5, columnspan=2, sticky="we")

        ttk.Label(frame, text="📡 HTTP Method:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.method_var = tk.StringVar(value="GET")
        self.method_menu = ttk.Combobox(frame, textvariable=self.method_var, values=["GET", "POST", "PUT", "DELETE"],
                                        width=10, state="readonly")
        self.method_menu.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        self.test_button = ttk.Button(frame, text="\U0001F680 Test API", command=self.run_tests)
        self.test_button.grid(row=1, column=2, padx=5, pady=5, sticky="e")

        self.progress = ttk.Progressbar(frame, mode="indeterminate", length=200)
        self.progress.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky="we")

        self.report_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=100, height=18, font=("Courier", 12),
                                                     bg="#1E1E1E", fg="white")
        self.report_area.grid(row=3, column=0, columnspan=3, padx=5, pady=10, sticky="nsew")

        self.history_button = ttk.Button(frame, text="📜 View Past Results", command=self.show_history)
        self.history_button.grid(row=4, column=0, padx=5, pady=5, sticky="w")

        self.canvas_frame = ttk.Frame(frame)
        self.canvas_frame.grid(row=5, column=0, columnspan=3, pady=10, sticky="nsew")

        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(3, weight=1)

    def run_tests(self):
        self.test_button.config(state=tk.DISABLED)
        self.progress.start()
        self.report_area.delete(1.0, tk.END)

        threading.Thread(target=self.perform_tests, daemon=True).start()

    def perform_tests(self):
        url = self.url_entry.get().strip()
        method = self.method_var.get().strip().upper()

        if not url:
            messagebox.showerror("⚠ Error", "Please enter an API URL.")
            self.reset_ui()
            return

        self.append_report(f"🌍 Testing API: {url} ({method})\n\n")

        functionality = self.test_functionality(url, method)
        reliability, avg_time = self.test_reliability(url, method)
        security = self.test_security(url, method)
        performance = max(0, 100 - avg_time / 10)
        performance = round(performance, 2)

        # Reasoning for scores
        functionality_reason = "✔ Fully functional" if functionality == 100 else "⚠ Partial functionality issues detected"
        reliability_reason = "✔ Stable response times" if reliability > 80 else "⚠ Inconsistent response times"
        performance_reason = "✔ Fast response" if performance > 80 else "⚠ Slower than expected"
        security_reason = "✔ Secure headers and HTTPS" if security > 80 else "⚠ Some security headers missing"

        self.append_report("\n✅ API testing complete.\n")
        self.append_report(f"🛠 **Functionality Score**: {functionality}/100 - {functionality_reason}\n")
        self.append_report(f"🔄 **Reliability Score**: {reliability}/100 - {reliability_reason} (Avg Response Time: {avg_time:.2f} ms)\n")
        self.append_report(f"🚀 **Performance Score**: {performance}/100 - {performance_reason}\n")
        self.append_report(f"🔒 **Security Score**: {security}/100 - {security_reason}\n")

        # Store results
        test_history.append({
            "URL": url,
            "Method": method,
            "Functionality Score": functionality,
            "Reliability Score": reliability,
            "Performance Score": performance,
            "Security Score": security
        })

        # Update graph dynamically
        self.after(0, self.show_graph, [functionality, reliability, performance, security])
        self.reset_ui()

    def test_functionality(self, url, method):
        try:
            response = requests.request(method, url)
            return 100 if response.status_code == 200 else 50
        except:
            return 0

    def test_reliability(self, url, method):
        response_times = []
        for _ in range(3):
            try:
                start = time.time()
                requests.request(method, url)
                response_times.append((time.time() - start) * 1000)
            except:
                response_times.append(None)

        avg_time = sum(filter(None, response_times)) / len(response_times) if response_times else 1000
        reliability_score = max(0, 100 - avg_time / 10)
        return round(reliability_score, 2), avg_time

    def test_security(self, url, method):
        try:
            response = requests.request(method, url)
            https_check = 100 if url.startswith("https://") else 50
            headers_score = sum(25 for header in SECURITY_HEADERS if header in response.headers)
            return min(100, https_check + headers_score)
        except:
            return 0

    def show_graph(self, scores):
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

        labels = ["Functionality", "Reliability", "Performance", "Security"]
        fig, ax = plt.subplots()
        ax.bar(labels, scores, color="green")
        ax.set_ylabel("Score (0-100)")
        ax.set_title("API Test Scores")
        ax.set_ylim([0, 100])

        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        canvas.get_tk_widget().pack()
        canvas.draw()

    def append_report(self, text):
        self.report_area.insert(tk.END, text)
        self.report_area.see(tk.END)

    def reset_ui(self):
        self.test_button.config(state=tk.NORMAL)
        self.progress.stop()

    def show_history(self):
        messagebox.showinfo("📜 Past Results", "\n".join([str(h) for h in test_history]))


if __name__ == "__main__":
    app = APITester()
    app.mainloop()
