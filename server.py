import socket
import threading
import json
from newsapi import NewsApiClient
import time

API_KEY = "2d263a3775564465be7a49f1c04e1af7"  
newsapi = NewsApiClient(api_key=API_KEY)

# Function to send data with a length header
def send_data(client_socket, data):
    try:
        json_data = json.dumps(data).encode()
        data_length = f"{len(json_data):<10}".encode()  # 10-byte header
        client_socket.sendall(data_length + json_data)
    except socket.error as e:
        print(f"Error sending data to client: {e}")

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
        print(f"Error fetching sources: {e}")
        return {"error": str(e)}

# Function to handle client requests
import time  # Add this import at the top

def handle_client(client_socket, client_address):
    print(f"Connection established with {client_address}")
    try:
        username = client_socket.recv(1024).decode().strip()
        print(f"Client {username} connected from {client_address}")

        while True:
            request_data = client_socket.recv(4096).decode()
            if not request_data:
                print(f"Client {username} disconnected.")
                break

            try:
                request = json.loads(request_data)
                action = request.get("action")

                start_time = time.time()  # Start timing the request processing

                if action == "headlines":
                    response = fetch_headlines(request)
                elif action == "sources":
                    response = fetch_sources(request)
                elif action == "quit":
                    print(f"Client {username} requested to quit.")
                    break
                else:
                    response = {"error": "Invalid action."}

                processing_time = time.time() - start_time  # Calculate elapsed time
                print(f"Processed {action} request from {username} in {processing_time:.2f} seconds")

                send_data(client_socket, response)

            except json.JSONDecodeError:
                print(f"Error decoding request from {client_address}. Sending error response.")
                send_data(client_socket, {"error": "Invalid request format."})
            except Exception as e:
                print(f"Error processing request from {client_address}: {e}")
                send_data(client_socket, {"error": "An error occurred while processing your request."})

    except Exception as e:
        print(f"Unexpected error with client {client_address}: {e}")
    finally:
        print(f"Closing connection with {client_address}.")
        client_socket.close()

# Start the server
def start_server(host="127.0.0.1", port=5000):
    # Warm-up: Make a dummy request to NewsAPI to ensure quicker responses later
    try:
        print("Warming up NewsAPI connection...")
        newsapi.get_top_headlines(q="test")
    except Exception as e:
        print(f"Warning: NewsAPI warm-up failed: {e}")

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print(f"Server started on {host}:{port}. Waiting for connections...")

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            threading.Thread(target=handle_client, args=(client_socket, client_address)).start()
    except KeyboardInterrupt:
        print("\nShutting down server gracefully...")
    except Exception as e:
        print(f"Unexpected server error: {e}")
    finally:
        server_socket.close()
        print("Server shut down.")


    print(f"Server started on {host}:{port}. Waiting for connections...")

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            threading.Thread(target=handle_client, args=(client_socket, client_address)).start()
    except KeyboardInterrupt:
        print("\nShutting down server gracefully...")
    except Exception as e:
        print(f"Unexpected server error: {e}")
    finally:
        server_socket.close()
        print("Server shut down.")

if __name__ == "__main__":
    start_server()
