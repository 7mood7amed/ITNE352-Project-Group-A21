import socket
import threading
import time
import json
from newsapi import NewsApiClient

# Initialize NewsAPI with API Key
API_KEY = "8a088e6064854513a3d6964c48fa989d"  # Replace with the valid NewsAPI key
newsapi = NewsApiClient(api_key=API_KEY)

# Function to send data with a length header
def send_data(client_socket, data):
    print("Sending response to client:")
    print(json.dumps(data, indent=4))  # Print the response for debugging
    json_data = json.dumps(data).encode()  # Convert data to JSON and encode as bytes
    data_length = f"{len(json_data):<10}".encode()  # 10-byte header to indicate data length
    client_socket.sendall(data_length + json_data)  # Send the length header followed by data

# Function to fetch headlines from NewsAPI
def fetch_headlines(request):
    try:
        # Get query, category, and country from the request
        query = request.get("query")
        category = request.get("category")
        country = request.get("country")

        print(f"Fetching headlines with query={query}, category={category}, country={country}")

        # Check which filter to apply based on the request
        if query:
            response = newsapi.get_top_headlines(q=query)  # Fetch headlines with query
        elif category:
            response = newsapi.get_top_headlines(category=category)  # Fetch headlines with category
        elif country:
            response = newsapi.get_top_headlines(country=country)  # Fetch headlines with country
        else:
            response = newsapi.get_top_headlines()  # Fetch all headlines without filters

        print(f"Response status: {response['status']}")
        if response["status"] != "ok":  # If the API call fails
            return {"error": response.get("message", "Failed to fetch headlines.")}

        # Extract articles from the response
        articles = response.get("articles", [])
        if not articles:
            return {"error": "No headlines found for the given query."}

        # Format the response with headlines
        return {
            "type": "headlines",
            "results": [
                {
                    "source": article["source"]["name"],  # Source of the article
                    "author": article.get("author", "Unknown"),  # Author, or "Unknown" if not available
                    "title": article["title"],  # Title of the article
                    "description": article.get("description", "No description available."),  # Description
                    "url": article["url"],  # URL to the article
                    "published_at": article["publishedAt"]  # Published date
                }
                for article in articles
            ]
        }
    except Exception as e:
        # Handle exceptions and return the error message
        print(f"Error fetching headlines: {str(e)}")
        return {"error": str(e)}

# Function to fetch sources from NewsAPI
def fetch_sources(request):
    try:
        # Get category, country, and language from the request
        category = request.get("category")
        country = request.get("country")
        language = request.get("language")

        print(f"Fetching sources with category={category}, country={country}, language={language}")

        # Fetch sources based on the provided filters
        response = newsapi.get_sources(category=category, country=country, language=language)

        print(f"Response status: {response['status']}")
        if response["status"] != "ok":  # If the API call fails
            return {"error": response.get("message", "Failed to fetch sources.")}

        # Extract sources from the response
        sources = response.get("sources", [])
        if not sources:
            return {"error": "No sources found for the given query."}

        # Format the response with sources
        return {
            "type": "sources",
            "results": [
                {
                    "name": source["name"],  # Name of the source
                    "description": source["description"],  # Description of the source
                    "url": source["url"],  # URL of the source
                    "category": source["category"],  # Category of the source
                    "language": source["language"],  # Language of the source
                    "country": source["country"]  # Country of the source
                }
                for source in sources
            ]
        }
    except Exception as e:
        # Handle exceptions and return the error message
        print(f"Error fetching sources: {str(e)}")
        return {"error": str(e)}

# Function to handle client requests
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

# Start the server
def start_server(host="127.0.0.1", port=5000):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))  # Bind server to the specified host and port
    server_socket.listen(5)  # Listen for incoming connections (up to 5 clients)
    print(f"Server started on {host}:{port}")

    try:
        while True:
            # Accept incoming client connections and start a new thread for each client
            client_socket, client_address = server_socket.accept()
            threading.Thread(target=handle_client, args=(client_socket, client_address)).start()
    except KeyboardInterrupt:
        # Gracefully shut down the server on keyboard interrupt (Ctrl+C)
        print("Shutting down server...")
    finally:
        server_socket.close()  # Close the server socket after stopping

if __name__ == "__main__":
    start_server()  # Start the server when the script is executed
