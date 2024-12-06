import socket
import threading
import json
from newsapi import NewsApiClient

# Initialize NewsAPI with API key
API_KEY = "2d263a3775564465be7a49f1c04e1af7"  
newsapi = NewsApiClient(api_key=API_KEY)

def receive_data(client_socket): # New receive function on the server
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


# Function to send data with a length header
def send_data(client_socket, data):
    json_data = json.dumps(data).encode()
    data_length = f"{len(json_data):<10}".encode()
    client_socket.sendall(data_length + json_data)

# Function to fetch headlines from NewsAPI
def fetch_headlines(request):
    try:
        query = request.get("query")
        category = request.get("category")
        country = request.get("country")

        if query:
            response = newsapi.get_top_headlines(q=query)
        elif category:
            response = newsapi.get_top_headlines(category=category)
        elif country:
            response = newsapi.get_top_headlines(country=country)
        else:
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
        return {"error": str(e)}

# Function to fetch sources from NewsAPI
def fetch_sources(request):
    try:
        category = request.get("category")
        country = request.get("country")
        language = request.get("language")

        response = newsapi.get_sources(category=category, country=country, language=language)

        if response["status"] != "ok":
            return {"error": response.get("message", "Failed to fetch sources.")}

        return {
            "type": "sources",
            "results": [
                {
                    "name": source["name"],
                    "description": source["description"],
                    "url": source["url"],
                    "category": source["category"],
                    "language": source["language"],
                    "country": source["country"]
                }
                for source in response.get("sources", [])
            ]
        }
    except Exception as e:
        return {"error": str(e)}

# Function to handle client requests
def handle_client(client_socket, client_address):
    try:
        while True:
            request = receive_data(client_socket) # Use receive_data here!
            if request is None:
                break  # Client disconnected

            action = request.get("action")
            if action == "headlines":
                response = fetch_headlines(request)
            elif action == "sources":
                response = fetch_sources(request)
            elif action == "quit":
                break
            else:
                response = {"error": "Invalid action."}

            send_data(client_socket, response) # Send the response back

    except Exception as e:
        print(f"Error handling client {client_address}: {e}")
    finally:
        client_socket.close()

# Start the server
def start_server(host="127.0.0.1", port=5000):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            threading.Thread(target=handle_client, args=(client_socket, client_address)).start()
    except KeyboardInterrupt:
        print("Shutting down server...")
    finally:
        server_socket.close()

if __name__ == "__main__":
  start_server()