import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import socket
import json

VALID_COUNTRIES = ["au", "ca", "jp", "ae", "sa", "kr", "us", "ma"]
VALID_LANGUAGES = ["ar", "en"]
VALID_CATEGORIES = ["business", "general", "health", "science", "sports", "technology"]

HOST = "127.0.0.1"
PORT = 5000

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

def send_request(request):
    client_socket.sendall(json.dumps(request).encode())
    return receive_data()

def receive_data():
    data_length = int(client_socket.recv(10).decode().strip())
    data = b""
    while len(data) < data_length:
        packet = client_socket.recv(4096)
        if not packet:
            break
        data += packet
    return json.loads(data.decode())

def display_results(response, title):
    results_window = tk.Toplevel()
    results_window.title(title)
    result_text = scrolledtext.ScrolledText(results_window, wrap=tk.WORD, width=80, height=20)
    result_text.pack(padx=10, pady=10)

    results = response.get("results", [])[:15]  # Limit to 15 results
    if not results:
        result_text.insert(tk.END, "No results found for the given query. Please try again.\n")
    else:
        for idx, item in enumerate(results, start=1):
            if "title" in item:
                result_text.insert(tk.END, f"\n{idx}. {item['title']}\n")
                result_text.insert(tk.END, f"   Source       : {item['source']}\n")
                result_text.insert(tk.END, f"   Author       : {item.get('author', 'Unknown')}\n")
                result_text.insert(tk.END, f"   Published At : {item['published_at']}\n")
                result_text.insert(tk.END, f"   URL          : {item['url']}\n")
                result_text.insert(tk.END, f"   Description  : {item.get('description', 'No description available.')}\n")
            result_text.insert(tk.END, "=" * 40 + "\n")
    result_text.config(state=tk.DISABLED)

def handle_headlines():
    menu_window = tk.Toplevel()
    menu_window.title("Headlines Menu")
    def send_headlines_request(param_name=None, options=None):
        request = {"action": "headlines"}
        if param_name:
            value = param_entry.get()
            if options and value not in options:
                messagebox.showerror("Error", f"Invalid {param_name}. Choose from {options}.")
                return
            elif not value.strip():
                messagebox.showerror("Error", f"{param_name.capitalize()} cannot be empty.")
                return
            request[param_name] = value.strip()
        response = send_request(request)
        if "error" in response:
            messagebox.showerror("Error", response["error"])
        else:
            display_results(response, "Headlines Results")
    param_entry = tk.Entry(menu_window, width=50)
    param_entry.pack(pady=5)
    ttk.Button(menu_window, text="Search by keywords", command=lambda: send_headlines_request("query")).pack(pady=5)
    ttk.Button(menu_window, text="Search by category", command=lambda: send_headlines_request("category", VALID_CATEGORIES)).pack(pady=5)
    ttk.Button(menu_window, text="Search by country", command=lambda: send_headlines_request("country", VALID_COUNTRIES)).pack(pady=5)
    ttk.Button(menu_window, text="List all headlines", command=lambda: send_headlines_request()).pack(pady=5)
    ttk.Button(menu_window, text="Back to Main Menu", command=menu_window.destroy).pack(pady=10)

def handle_sources():
    menu_window = tk.Toplevel()
    menu_window.title("Sources Menu")
    def send_sources_request(param_name=None, options=None):
        request = {"action": "sources"}
        if param_name:
            value = param_entry.get()
            if options and value not in options:
                messagebox.showerror("Error", f"Invalid {param_name}. Choose from {options}.")
                return
            elif not value.strip():
                messagebox.showerror("Error", f"{param_name.capitalize()} cannot be empty.")
                return
            request[param_name] = value.strip()
        response = send_request(request)
        if "error" in response:
            messagebox.showerror("Error", response["error"])
        else:
            display_results(response, "Sources Results")
    param_entry = tk.Entry(menu_window, width=50)
    param_entry.pack(pady=5)
    ttk.Button(menu_window, text="Search by category", command=lambda: send_sources_request("category", VALID_CATEGORIES)).pack(pady=5)
    ttk.Button(menu_window, text="Search by country", command=lambda: send_sources_request("country", VALID_COUNTRIES)).pack(pady=5)
    ttk.Button(menu_window, text="Search by language", command=lambda: send_sources_request("language", VALID_LANGUAGES)).pack(pady=5)
    ttk.Button(menu_window, text="List all sources", command=lambda: send_sources_request()).pack(pady=5)
    ttk.Button(menu_window, text="Back to Main Menu", command=menu_window.destroy).pack(pady=10)

def main_menu():
    main_window = tk.Tk()
    main_window.title("News Client")
    main_window.geometry("400x300")
    main_window.minsize(400, 300)
    ttk.Label(main_window, text="Main Menu").pack(pady=10)
    ttk.Button(main_window, text="Search Headlines", command=handle_headlines).pack(pady=5)
    ttk.Button(main_window, text="List Sources", command=handle_sources).pack(pady=5)
    ttk.Button(main_window, text="Quit", command=lambda: (client_socket.sendall(json.dumps({"action": "quit"}).encode()), main_window.destroy())).pack(pady=10)
    main_window.mainloop()

if __name__ == "__main__":
    username = input("Enter your username: ")
    client_socket.sendall(username.encode())
    main_menu()
    client_socket.close()
