Project title : 
    Smart News Explorer: A GUI-Based Real-Time News Retrieval System

Semester :
    2024/2025 first Semester

Group: 
    Group Name: A21
    Course Code: ITNE352
    Section: 1
    Members:
    Mohammed hamed eltantawy (ID: 202207174)
    isa ebrahim alalwan (ID: 202209467)

Table of Contents :
    Requirements
    How to Run the System
    Project Description
    Scripts Overview
        1- Server Script: server.py
        2- Client Script: client.py
    Additional Concept
    Acknowledgments
    Conclusion

requiremets : 
    1- installing newapi library using cmd command : pip install newsapi-python 
    2- installing python3.


how to run the system : 
    1- first , run the server in a new window terminal : python server.py
    2- then , run the client in a new window terminal :  python client.py
    3- begin the work

Project Description : 
    is a client-server application designed to retrieve and display real-time news headlines and sources using the NewsAPI.
    The client features an interactive graphical user interface (GUI) built with tkinter, allowing users to explore top news stories, search for specific headlines, and view available news sources based on categories, countries, and languages.
    The server, powered by Python and the NewsAPI library, processes client requests and retrieves the latest news articles and sources. It supports robust communication with the client via socket programming, ensuring smooth and efficient data exchange. 

The scripts: 

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
                    json_data = json.dumps(data).encode()
                    data_length = f"{len(json_data):<10}".encode()  # 10-byte header
                    client_socket.sendall(data_length + json_data)
            
            handle_client() for handling  requests from the client : 
                def handle_client(client_socket, client_address):
                    print(f"Connection established with {client_address}")
                    try:
                        username = client_socket.recv(1024).decode()
                        print(f"Client username: {username}")

                        while True:
                            request_data = client_socket.recv(4096).decode()
                            if not request_data:
                                break
                            request = json.loads(request_data)
                            action = request.get("action")

                            if action == "headlines":
                                response = fetch_headlines(request)
                                send_data(client_socket, response)
                            elif action == "sources":
                                response = fetch_sources(request)
                                send_data(client_socket, response)
                            elif action == "quit":
                                print(f"Client {username} disconnected.")
                                break
                            else:
                                send_data(client_socket, {"error": "Invalid action."})
                    except Exception as e:
                        print(f"Error handling client {client_address}: {e}")
                    finally:
                        client_socket.close()


        
        client.py :

            Main functionalities : 
                Providing a user friendly GUI for better user interaction
                communicating with the server
                displaying news content 

            packeges used :  
                socket , json , tkinter (as tk) , ttk , messagebox 


            class NewsApp(tk.Tk) for GUI with many functions 
            
            receive_data() for receiving data with a length header :
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

            get_headlines() to handle headlines request : 
                def get_headlines(client_socket, action, query=None, category=None, country=None):
                    request = {"action": "headlines", "query": query, "category": category, "country": country}
                    response = send_request(client_socket, request)
                    if "error" in response:
                        messagebox.showerror("Error", response["error"])
                    else:
                        return response.get("results", [])
            
            get_sources() to handle sources request :
                def get_sources(client_socket, action, category=None, country=None, language=None):
                    request = {"action": "sources", "category": category, "country": country, "language": language}
                    response = send_request(client_socket, request)
                    if "error" in response:
                        messagebox.showerror("Error", response["error"])
                    else:
                        return response.get("results", [])
            


Additional concept: 
    the additional concepts we implemented is Providing a user friendly GUI for better user interaction. using tkinter library and functions to provide a clear Graphical User Interface.

Acknowledgments :
    Dr. mohammed almeer for explainig the course qith all the important concepts of network programming including socket handling and multithreading
    NewAPI : for providing this amazing API system for extracting data

Conclusion : 
    our project successfully demonstrates the integration of real-time data retrieval, client-server communication, and a user-friendly graphical interface. With the help of Python's libraries and the NewsAPI, we have created a functional application that provides users with instant access to global news and sources.

    This project highlights key concepts in software development, including:

    1- Building a robust client-server architecture using socket programming.
    2- Developing an interactive and intuitive GUI with tkinter.
    3- andling real-time API integration for dynamic and accurate data retrieval.
    4- Through this project, we gained valuable insights into network programming, error handling, and user interface design. 
    5- Challenges such as connection management, data parsing, and ensuring reliable communication were addressed with careful debugging and iterative improvements.

    In conclusion, this project provided a meaningful learning experience and a solid foundation for developing similar systems in the future. It demonstrates how technology can be harnessed to deliver timely and relevant information to users in an accessible and engaging way.