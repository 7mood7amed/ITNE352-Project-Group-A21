# Project title  
Smart News Explorer: A GUI-Based Real-Time News Retrieval System
 
## Semester
2024/2025 first Semester
 
## Group:
Group Name: A21
Course Code: ITNE352
Section: 1
Members:
Mohammed hamed eltantawy (ID: 202207174)
Isa ebrahim alalwan (ID: 202209467)
 
## Table of Contents :
- [Requirements](#requirements)
- [How to Run the System](#how-to-run-the-system)
- [Project Description](#project-description)
- [Scripts Overview](#scripts-overview)
- [Additional Concept](#additional-concept)
- [Acknowledgments](#acknowledgments)
- [Conclusion](#conclusion)
 
## Requirements:
 1- installing newapi library using cmd command : pip install newsapi-python
 2- installing python3.
 
 
## How to Run the System:
 1- first , run the server in a new window terminal : python server.py
 2- then , run the client in a new window terminal :  python client.py
 3- begin the work
 
### Project Description:
is a client-server application designed to retrieve and display real-time news headlines and sources using the NewsAPI.
The client features an interactive graphical user interface (GUI) built with tkinter, allowing users to explore top news stories, search for specific headlines, and view available news sources based on categories, countries, and languages.
The server, powered by Python and the NewsAPI library, processes client requests and retrieves the latest news articles and sources. It supports robust communication with the client via socket programming, ensuring smooth and efficient data exchange.
 
## Scripts Overview:
 
    server.py :
 
        Main functionalities :
            Interaction with newsAPI
            Handling client requests
            provides news headlines and sources to client
           
 
         packeges used :  
            socket , threading , json , newapi ( installed using CMD and Api key )
 
         key functions of the server :
 
            fetch_headlines() to fetch headlines from NewsAPI :
                def fetch_headlines(request):
                    try:
                        query = request.get("query")
                        category = request.get("category")
                        country = request.get("country")
 
                        if query:
                            print(f"Fetching headlines for query: {query}")
                            response = newsapi.get_top_headlines(q=query)
                        elif category:
                            print(f"Fetching headlines for category: {category}")
                            response = newsapi.get_top_headlines(category=category)
                        elif country:
                            print(f"Fetching headlines for country: {country}")
                            response = newsapi.get_top_headlines(country=country)
                        else:
                            print("Fetching all headlines")
                            response = newsapi.get_top_headlines()
 
                        if response["status"] != "ok":
                            return {"error": response.get("message", "Failed to fetch headlines.")}
 
                        return {
                            "type": "headlines",
                            "results": [
                                {
                                    "source": article["source"]["name"],
                                    "author": article.get("author", "Unknown"),
                                    "title": article["title"],
                                    "description": article.get("description", "No description available."),
                                    "url": article["url"],
                                    "published_at": article["publishedAt"]
                                }
                                for article in response.get("articles", [])
                            ]
                        }
                    except Exception as e:
                        print(f"Error fetching headlines: {e}")
                        return {"error": str(e)}
 
 
            send_data() for sending data with a length header :
                def send_data(client_socket, data):
                    print("Sending response to client:")
                    print(json.dumps(data, indent=4))  # Print the response for debugging
                    json_data = json.dumps(data).encode()  # Convert data to JSON and encode as bytes
                    data_length = f"{len(json_data):<10}".encode()  # 10-byte header to indicate data length
                    client_socket.sendall(data_length + json_data)  # Send the length header followed by data
           
            handle_client() for handling  requests from the client :
                def handle_client(client_socket, client_address):
                    print(f"Connection established with {client_address}")
                    try:
                        # Receive the username from the client
                        username = client_socket.recv(1024).decode()
                        print(f"Client username: {username}")
 
                        # Keep handling requests until client disconnects
                        while True:
                            request_data = client_socket.recv(4096).decode()
                            if not request_data:  # If no data received, client has disconnected
                                break
 
                            # Parse the received request as JSON
                            request = json.loads(request_data)
                            action = request.get("action")  # Get the action from the request
 
                            # Perform action based on the client's request
                            if action == "headlines":
                                response = fetch_headlines(request)  # Fetch headlines
                                send_data(client_socket, response)  # Send response back to the client
                            elif action == "sources":
                                response = fetch_sources(request)  # Fetch sources
                                send_data(client_socket, response)  # Send response back to the client
                            elif action == "quit":  # If client sends quit action, disconnect
                                print(f"Client {username} disconnected.")
                                break
                            else:
                                send_data(client_socket, {"error": "Invalid action."})  # Handle invalid action
                               
                    except Exception as e:
                        # Handle any errors that occur during the client handling process
                        print(f"Error handling client {client_address}: {e}")
                    finally:
                        client_socket.close()  # Close the client socket after handling
 
       
         client.py :
 
            Main functionalities :
                Providing a user friendly GUI for better user interaction
                communicating with the server
                displaying news content
 
            packeges used :  
                socket , json , tkinter (as tk) , ttk , messagebox , scrolledtext
           
            receive_data() for receiving data with a length header :
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
           
 
 
## Additional concept:
the additional concepts we implemented is Providing a user friendly GUI for better user interaction. using tkinter library and functions to provide a clear Graphical User Interface.
 
## Acknowledgments:
we would like to thank Dr. mohammed almeer for explainig the course with all the important concepts of network programming including socket handling and multithreading
NewAPI : for providing this amazing API system for extracting data
 
## Conclusion:
In conclusion, we built a project that successfully demonstrates the integration of real-time data retrieval, client-server communication, and a user-friendly graphical interface. With the help of Python's libraries and the NewsAPI, we have created a functional application that provides users with instant access to global news and sources. This project was one of our best experiences since we learned a lot about the concept of network programming and it will definitely help us in our future career