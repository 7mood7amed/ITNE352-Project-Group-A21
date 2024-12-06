# client_gui.py
import socket
import json
import tkinter as tk
from tkinter import ttk, messagebox

VALID_COUNTRIES = ["au", "ca", "jp", "ae", "sa", "kr", "us", "ma"]
VALID_LANGUAGES = ["ar", "en"]
VALID_CATEGORIES = ["business", "general", "health", "science", "sports", "technology"]

# Function to receive data with a prefixed length header
def receive_data(client_socket):
    try:
        data_length = client_socket.recv(10).decode().strip()
        if not data_length:
            return {}
        data_length = int(data_length)
        data = b""
        while len(data) < data_length:
            packet = client_socket.recv(4096)
            if not packet:
                break
            data += packet
        return json.loads(data.decode())
    except (ValueError, ConnectionResetError):
        return {}

# Function to send request and receive response
def send_request(client_socket, request):
    client_socket.sendall(json.dumps(request).encode())
    return receive_data(client_socket)

# Function to connect to the server
def connect_to_server(host="127.0.0.1", port=5000):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        return client_socket
    except Exception as e:
        messagebox.showerror("Connection Error", f"Failed to connect to the server: {e}")
        return None

# Function to handle headlines request
def get_headlines(client_socket, action, query=None, category=None, country=None):
    request = {"action": "headlines", "query": query, "category": category, "country": country}
    response = send_request(client_socket, request)
    if "error" in response:
        messagebox.showerror("Error", response["error"])
    else:
        return response.get("results", [])

# Function to handle sources request
def get_sources(client_socket, action, category=None, country=None, language=None):
    request = {"action": "sources", "category": category, "country": country, "language": language}
    response = send_request(client_socket, request)
    if "error" in response:
        messagebox.showerror("Error", response["error"])
    else:
        return response.get("results", [])

# Main Application Class
class NewsApp(tk.Tk):
    def _init_(self):
        super()._init_()
        self.title("News Client")
        self.geometry("800x600")
        self.client_socket = None

        self.create_widgets()

    def create_widgets(self):
        # Connection Frame
        self.connection_frame = ttk.LabelFrame(self, text="Server Connection")
        self.connection_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(self.connection_frame, text="Server Host:").grid(row=0, column=0, padx=5, pady=5)
        self.host_entry = ttk.Entry(self.connection_frame)
        self.host_entry.grid(row=0, column=1, padx=5, pady=5)
        self.host_entry.insert(0, "127.0.0.1")

        ttk.Label(self.connection_frame, text="Port:").grid(row=0, column=2, padx=5, pady=5)
        self.port_entry = ttk.Entry(self.connection_frame)
        self.port_entry.grid(row=0, column=3, padx=5, pady=5)
        self.port_entry.insert(0, "5000")

        self.connect_button = ttk.Button(self.connection_frame, text="Connect", command=self.connect)
        self.connect_button.grid(row=0, column=4, padx=5, pady=5)

        # Menu Frame
        self.menu_frame = ttk.LabelFrame(self, text="Menu")
        self.menu_frame.pack(fill="x", padx=10, pady=10)

        self.headlines_button = ttk.Button(self.menu_frame, text="Headlines", command=self.open_headlines)
        self.headlines_button.pack(side="left", padx=10, pady=10)

        self.sources_button = ttk.Button(self.menu_frame, text="Sources", command=self.open_sources)
        self.sources_button.pack(side="left", padx=10, pady=10)

        self.quit_button = ttk.Button(self.menu_frame, text="Quit", command=self.quit_app)
        self.quit_button.pack(side="right", padx=10, pady=10)

    def connect(self):
        host = self.host_entry.get()
        port = int(self.port_entry.get())
        self.client_socket = connect_to_server(host, port)
        if self.client_socket:
            messagebox.showinfo("Connection", "Connected to the server successfully!")

    def open_headlines(self):
        if not self.client_socket:
            messagebox.showwarning("Not Connected", "Please connect to the server first.")
            return
        HeadlinesWindow(self, self.client_socket)

    def open_sources(self):
        if not self.client_socket:
            messagebox.showwarning("Not Connected", "Please connect to the server first.")
            return
        SourcesWindow(self, self.client_socket)

    def quit_app(self):
        if self.client_socket:
            send_request(self.client_socket, {"action": "quit"})
            self.client_socket.close()
        self.destroy()

# Headlines Window
class HeadlinesWindow(tk.Toplevel):
    def _init_(self, parent, client_socket):
        super()._init_(parent)
        self.client_socket = client_socket
        self.title("Headlines")
        self.geometry("800x400")
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="Search Headlines").pack(pady=10)

        # Search Criteria
        self.criteria_frame = ttk.Frame(self)
        self.criteria_frame.pack(fill="x", pady=10)

        self.query_label = ttk.Label(self.criteria_frame, text="Keywords:")
        self.query_label.grid(row=0, column=0, padx=5, pady=5)
        self.query_entry = ttk.Entry(self.criteria_frame)
        self.query_entry.grid(row=0, column=1, padx=5, pady=5)

        self.search_button = ttk.Button(self.criteria_frame, text="Search", command=self.search_headlines)
        self.search_button.grid(row=0, column=2, padx=5, pady=5)

        # Results List
        self.results_list = tk.Text(self, wrap="word")
        self.results_list.pack(fill="both", padx=10, pady=10, expand=True)

    def search_headlines(self):
        query = self.query_entry.get()
        results = get_headlines(self.client_socket, "headlines", query=query)
        self.results_list.delete("1.0", "end")
        if not results:
            self.results_list.insert("end", "No headlines found.")
        else:
            for idx, article in enumerate(results, start=1):
                self.results_list.insert(
                    "end",
                    f"{idx}. {article['title']} ({article['source']})\nURL: {article['url']}\n\n",
                )

# Sources Window
class SourcesWindow(tk.Toplevel):
    def _init_(self, parent, client_socket):
        super()._init_(parent)
        self.client_socket = client_socket
        self.title("Sources")
        self.geometry("800x400")
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="News Sources").pack(pady=10)

        # Search Criteria
        self.criteria_frame = ttk.Frame(self)
        self.criteria_frame.pack(fill="x", pady=10)

        self.category_label = ttk.Label(self.criteria_frame, text="Category:")
        self.category_label.grid(row=0, column=0, padx=5, pady=5)
        self.category_combobox = ttk.Combobox(
            self.criteria_frame, values=VALID_CATEGORIES, state="readonly"
        )
        self.category_combobox.grid(row=0, column=1, padx=5, pady=5)

        self.search_button = ttk.Button(self.criteria_frame, text="Search", command=self.search_sources)
        self.search_button.grid(row=0, column=2, padx=5, pady=5)

        # Results List
        self.results_list = tk.Text(self, wrap="word")
        self.results_list.pack(fill="both", padx=10, pady=10, expand=True)

    def search_sources(self):
        category = self.category_combobox.get()
        results = get_sources(self.client_socket, "sources", category=category)
        self.results_list.delete("1.0", "end")
        if not results:
            self.results_list.insert("end", "No sources found.")
        else:
            for idx, source in enumerate(results, start=1):
                self.results_list.insert(
                    "end",
                    f"{idx}. {source['name']} ({source['category']})\nURL: {source['url']}\n\n",
                )

if _name_ == "_main_":
    app = NewsApp()
    app.mainloop()