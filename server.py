import socket
import threading
import json
from newsapi import NewsApiClient

# Initialize NewsAPI with your API key
API_KEY = "2d263a3775564465be7a49f1c04e1af7"  # Replace with your valid NewsAPI key
newsapi = NewsApiClient(api_key=API_KEY)

# Function to send data with a length header
def send_data(client_socket, data):
    json_data = json.dumps(data).encode()
    data_length = f"{len(json_data):<10}".encode()  # 10-byte header
    client_socket.sendall(data_length + json_data)

# Function to fetch headlines from NewsAPI
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

# Start the server
def start_server(host="127.0.0.1", port=5000):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Server started on {host}:{port}")

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
