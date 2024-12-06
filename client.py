# client.py
import socket
import json
import tkinter as tk
from tkinter import ttk, messagebox

VALID_COUNTRIES = ["au", "ca", "jp", "ae", "sa", "kr", "us", "ma"]
VALID_LANGUAGES = ["ar", "en"]
VALID_CATEGORIES = ["business", "general", "health", "science", "sports", "technology"]

def receive_data(client_socket):
    try:
        data_length = client_socket.recv(10).decode().strip()
        if not data_length:
            return None
        data_length = int(data_length)
        data = b""
        while len(data) < data_length:
            packet = client_socket.recv(4096)
            if not packet:
                return None
            data += packet
        return json.loads(data.decode())
    except (ValueError, ConnectionResetError, ConnectionAbortedError, json.JSONDecodeError) as e:
        print(f"Error receiving data: {e}")
        return None

def send_request(client_socket, request):
    try:
        client_socket.sendall(json.dumps(request).encode())
        return receive_data(client_socket)
    except (socket.error, ConnectionError) as e:
        raise ConnectionError(f"Error sending request: {e}. Check your connection.")

def connect_to_server(host="127.0.0.1", port=5000):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(5)
        client_socket.connect((host, port))
        return client_socket
    except (socket.timeout, socket.error) as e:
        raise ConnectionError(f"Failed to connect to the server: {e}")

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
        try:
            self.client_socket = connect_to_server(host, port)
            messagebox.showinfo("Connection", "Connected to the server successfully!")
        except ConnectionError as e:
            messagebox.showerror("Connection Error", str(e))

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
            try:
                send_request(self.client_socket, {"action": "quit"})
            except ConnectionError:
                pass
            self.client_socket.close()
        self.destroy()

class HeadlinesWindow(tk.Toplevel):
    def _init_(self, parent, client_socket):
        super()._init_(parent)
        self.client_socket = client_socket
        self.title("Headlines")
        self.geometry("800x400")
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="Search Headlines").pack(pady=10)
        self.criteria_frame = ttk.Frame(self)
        self.criteria_frame.pack(fill="x", pady=10)

        self.query_label = ttk.Label(self.criteria_frame, text="Keywords:")
        self.query_label.grid(row=0, column=0, padx=5, pady=5)
        self.query_entry = ttk.Entry(self.criteria_frame)
        self.query_entry.grid(row=0, column=1, padx=5, pady=5)

        self.search_button = ttk.Button(self.criteria_frame, text="Search", command=self.search_headlines)
        self.search_button.grid(row=0, column=2, padx=5, pady=5)

        self.results_list = tk.Text(self, wrap="word")
        self.results_list.pack(fill="both", padx=10, pady=10, expand=True)

    def search_headlines(self):
        query = self.query_entry.get().strip()
        if not query:
            messagebox.showwarning("Invalid Input", "Please enter keywords for the search.")
            return
        try:
            request = {"action": "headlines", "query": query}
            response = send_request(self.client_socket, request)
            if response is None:
                messagebox.showerror("Error", "Connection to server lost.")
                self.destroy()
                return

            results = response.get("results", [])
            self.results_list.delete("1.0", "end")
            if not results:
                self.results_list.insert("end", "No headlines found.")
            else:
                for idx, article in enumerate(results, start=1):
                    self.results_list.insert(
                        "end",
                        f"{idx}. {article['title']} ({article['source']})\nURL: {article['url']}\n\n",
                    )
        except ConnectionError as e:
            messagebox.showerror("Error", str(e))


class SourcesWindow(tk.Toplevel):
    def _init_(self, parent, client_socket):
        super()._init_(parent)
        self.client_socket = client_socket
        self.title("Sources")
        self.geometry("800x400")
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="News Sources").pack(pady=10)
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

        self.results_list = tk.Text(self, wrap="word")
        self.results_list.pack(fill="both", padx=10, pady=10, expand=True)

    def search_sources(self):
        category = self.category_combobox.get()
        if not category:
            messagebox.showwarning("Invalid Input", "Please select a category.")
            return
        try:
            request = {"action": "sources", "category": category}
            response = send_request(self.client_socket, request)
            if response is None:
                messagebox.showerror("Error", "Connection to server lost.")
                self.destroy()
                return

            results = response.get("results", [])
            self.results_list.delete("1.0", "end")
            if not results:
                self.results_list.insert("end", "No sources found.")
            else:
                for idx, source in enumerate(results, start=1):
                    self.results_list.insert(
                        "end",
                        f"{idx}. {source['name']} ({source['category']})\nURL: {source['url']}\n\n",
                    )
        except ConnectionError as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    app = NewsApp()
    app.mainloop()