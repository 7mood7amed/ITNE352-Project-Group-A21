import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import socket
import json

# List of valid country codes, languages, and categories for filtering results
VALID_COUNTRIES = ["au", "ca", "jp", "ae", "sa", "kr", "us", "ma"]
VALID_LANGUAGES = ["ar", "en"]
VALID_CATEGORIES = ["business", "general", "health", "science", "sports", "technology"]

# Server connection details
HOST = "127.0.0.1"
PORT = 5000

# Create the client socket and connect to the server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

# Send a request to the server and receive the response
def send_request(request):
    # Send the request to the server
    client_socket.sendall(json.dumps(request).encode())
    # Receive and return the data from the server
    return receive_data()

# Receive data from the server
def receive_data():
    # Get the length of the incoming data
    data_length = int(client_socket.recv(10).decode().strip())
    data = b""  # Initialize an empty byte string for the data
    # Continue receiving data until the full response is received
    while len(data) < data_length:
        packet = client_socket.recv(4096)  # Receive up to 4096 bytes at a time
        if not packet:  # If no more data is received, break the loop
            break
        data += packet  # Add the received data to the full data
    return json.loads(data.decode())  # Decode the data as JSON and return it

# Display the results in a new window
def display_results(response, title):
    results_window = tk.Toplevel()  # Create a new window
    results_window.title(title)  # Set the window title
    result_text = scrolledtext.ScrolledText(results_window, wrap=tk.WORD, width=80, height=20)
    result_text.pack(padx=10, pady=10)  # Add the text widget to the window

    # Get the results, limiting to 15 entries
    results = response.get("results", [])[:15]
    if not results:  # If no results, display a message
        result_text.insert(tk.END, "No results found for the given query. Please try again.\n")
    else:
        # Loop through the results and display them
        for idx, item in enumerate(results, start=1):
            if "title" in item:  # For headlines
                result_text.insert(tk.END, f"\n{idx}. {item['title']}\n")
                result_text.insert(tk.END, f"   Source       : {item['source']}\n")
                result_text.insert(tk.END, f"   Author       : {item.get('author', 'Unknown')}\n")
                result_text.insert(tk.END, f"   Published At : {item['published_at']}\n")
                result_text.insert(tk.END, f"   URL          : {item['url']}\n")
                result_text.insert(tk.END, f"   Description  : {item.get('description', 'No description available.')}\n")
            elif "name" in item:  # For sources
                result_text.insert(tk.END, f"\n{idx}. {item['name']}\n")
                result_text.insert(tk.END, f"   URL          : {item['url']}\n")
                result_text.insert(tk.END, f"   Category     : {item['category']}\n")
                result_text.insert(tk.END, f"   Language     : {item['language']}\n")
                result_text.insert(tk.END, f"   Country      : {item['country']}\n")
                result_text.insert(tk.END, f"   Description  : {item.get('description', 'No description available.')}\n")

            # Add a separator between each result
            result_text.insert(tk.END, "=" * 40 + "\n")
    
    # Make the text widget read-only
    result_text.config(state=tk.DISABLED)

# Handle the headlines section
def handle_headlines():
    menu_window = tk.Toplevel()  # Create a new window for the headlines menu
    menu_window.title("Headlines Menu")
    
    # Function to send the request for headlines based on user input
    def send_headlines_request(param_name=None, options=None):
        request = {"action": "headlines"}
        # Get the user input for the parameter
        if param_name:
            value = param_entry.get()
            # Check if the input value is valid
            if options and value not in options:
                messagebox.showerror("Error", f"Invalid {param_name}. Choose from {options}.")
                return
            elif not value.strip():  # Check if the input is empty
                messagebox.showerror("Error", f"{param_name.capitalize()} cannot be empty.")
                return
            request[param_name] = value.strip()  # Add the valid input to the request
        
        response = send_request(request)  # Send the request to the server and get the response
        
        # Check if the response contains an error
        if "error" in response:
            messagebox.showerror("Error", response["error"])
        else:
            display_results(response, "Headlines Results")  # Display the results if no error
    
    # Create an entry widget for user input
    param_entry = tk.Entry(menu_window, width=50)
    param_entry.pack(pady=5)
    
    # Add buttons to allow the user to search by different parameters
    ttk.Button(menu_window, text="Search by keywords", command=lambda: send_headlines_request("query")).pack(pady=5)
    ttk.Button(menu_window, text="Search by category", command=lambda: send_headlines_request("category", VALID_CATEGORIES)).pack(pady=5)
    ttk.Button(menu_window, text="Search by country", command=lambda: send_headlines_request("country", VALID_COUNTRIES)).pack(pady=5)
    ttk.Button(menu_window, text="List all headlines", command=lambda: send_headlines_request()).pack(pady=5)
    ttk.Button(menu_window, text="Back to Main Menu", command=menu_window.destroy).pack(pady=10)

# Handle the sources section
def handle_sources():
    menu_window = tk.Toplevel()  # Create a new window for the sources menu
    menu_window.title("Sources Menu")
    
    # Function to send the request for sources based on user input
    def send_sources_request(param_name=None, options=None):
        request = {"action": "sources"}
        # Get the user input for the parameter
        if param_name:
            value = param_entry.get()
            # Check if the input value is valid
            if options and value not in options:
                messagebox.showerror("Error", f"Invalid {param_name}. Choose from {options}.")
                return
            elif not value.strip():  # Check if the input is empty
                messagebox.showerror("Error", f"{param_name.capitalize()} cannot be empty.")
                return
            request[param_name] = value.strip()  # Add the valid input to the request
        
        response = send_request(request)  # Send the request to the server and get the response
        
        # Check if the response contains an error
        if "error" in response:
            messagebox.showerror("Error", response["error"])
        else:
            display_results(response, "Sources Results")  # Display the results if no error
    
    # Create an entry widget for user input
    param_entry = tk.Entry(menu_window, width=50)
    param_entry.pack(pady=5)
    
    # Add buttons to allow the user to search by different parameters
    ttk.Button(menu_window, text="Search by category", command=lambda: send_sources_request("category", VALID_CATEGORIES)).pack(pady=5)
    ttk.Button(menu_window, text="Search by country", command=lambda: send_sources_request("country", VALID_COUNTRIES)).pack(pady=5)
    ttk.Button(menu_window, text="Search by language", command=lambda: send_sources_request("language", VALID_LANGUAGES)).pack(pady=5)
    ttk.Button(menu_window, text="List all sources", command=lambda: send_sources_request()).pack(pady=5)
    ttk.Button(menu_window, text="Back to Main Menu", command=menu_window.destroy).pack(pady=10)

# Main menu to navigate through the application
def main_menu():
    main_window = tk.Tk()  # Create the main window
    main_window.title("News Client")
    main_window.geometry("400x300")  # Set the window size
    main_window.minsize(400, 300)  # Set the minimum window size
    
    ttk.Label(main_window, text="Main Menu").pack(pady=10)  # Add a label to the main window
    
    # Add buttons for navigating to headlines and sources
    ttk.Button(main_window, text="Search Headlines", command=handle_headlines).pack(pady=5)
    ttk.Button(main_window, text="List Sources", command=handle_sources).pack(pady=5)
    
    # Add a quit button to close the application
    ttk.Button(main_window, text="Quit", command=lambda: (client_socket.sendall(json.dumps({"action": "quit"}).encode()), main_window.destroy())).pack(pady=10)
    
    main_window.mainloop()  # Start the GUI event loop

# Main entry point of the program
if __name__ == "__main__":
    username = input("Enter your username: ")  # Get the username from the user
    client_socket.sendall(username.encode())  # Send the username to the server
    main_menu()  # Show the main menu
    client_socket.close()  # Close the connection when the program ends
