import socket
import json
 
# Function to receive data with a prefixed length header
def receive_data(client_socket):
    data_length = int(client_socket.recv(10).decode().strip())
    data = b""
    while len(data) < data_length:
        packet = client_socket.recv(4096)
        if not packet:
            break
        data += packet
    return json.loads(data.decode())
 
# Function to send request and receive response
def send_request(client_socket, request):
    client_socket.sendall(json.dumps(request).encode())
    return receive_data(client_socket)
 
# Function to display headlines
def display_headlines(response):
    results = response.get("results", [])
    if not results:
        print("\nNo headlines found for the given query. Please try again with different parameters.")
        return
 
    print("\nTop Headlines:\n" + "=" * 40)
    for idx, article in enumerate(results, start=1):
        print(f"\n{idx}. {article['title']}")
        print(f"   Source       : {article['source']}")
        print(f"   Author       : {article.get('author', 'Unknown')}")
        print(f"   Published At : {article['published_at']}")
        print(f"   URL          : {article['url']}")
        print(f"   Description  : {article.get('description', 'No description available.')}")
    print("=" * 40)
 
# Function to display sources
def display_sources(response):
    results = response.get("results", [])
    if not results:
        print("\nNo sources found for the given query. Please try again with different parameters.")
        return
 
    print("\nNews Sources:\n" + "=" * 40)
    for idx, source in enumerate(results, start=1):
        print(f"\n{idx}. {source['name']}")
        print(f"   Description  : {source.get('description', 'No description available.')}")
        print(f"   Category     : {source['category']}")
        print(f"   Language     : {source['language']}")
        print(f"   Country      : {source['country']}")
        print(f"   URL          : {source['url']}")
    print("=" * 40)
 
# Function to handle headlines menu
def handle_headlines(client_socket):
    print("\nHeadlines Menu:")
    print("1. Search by keywords")
    print("2. Search by category")
    print("3. Search by country")
    print("4. List all")
    print("5. Back to main menu")
    choice = input("Enter your choice: ")
 
    request = {}
    if choice == "1":
        query = input("Enter keywords: ")
        request = {"action": "headlines", "query": query}
    elif choice == "2":
        category = input("Enter category (e.g., technology, business): ")
        request = {"action": "headlines", "category": category}
    elif choice == "3":
        country = input("Enter country code (e.g., us, gb): ")
        request = {"action": "headlines", "country": country}
    elif choice == "4":
        request = {"action": "headlines"}
    elif choice == "5":
        return
    else:
        print("Invalid choice.")
        return
 
    response = send_request(client_socket, request)
    if "error" in response:
        print(f"Error: {response['error']}")
    else:
        display_headlines(response)
 
# Function to handle sources menu
def handle_sources(client_socket):
    print("\nSources Menu:")
    print("1. Search by category")
    print("2. Search by country")
    print("3. Search by language")
    print("4. List all")
    print("5. Back to main menu")
    choice = input("Enter your choice: ")
 
    request = {}
    if choice == "1":
        category = input("Enter category (e.g., technology, business): ")
        request = {"action": "sources", "category": category}
    elif choice == "2":
        country = input("Enter country code (e.g., us, gb): ")
        request = {"action": "sources", "country": country}
    elif choice == "3":
        language = input("Enter language code (e.g., en, fr): ")
        request = {"action": "sources", "language": language}
    elif choice == "4":
        request = {"action": "sources"}
    elif choice == "5":
        return
    else:
        print("Invalid choice.")
        return
 
    response = send_request(client_socket, request)
    if "error" in response:
        print(f"Error: {response['error']}")
    else:
        display_sources(response)
 
# Main function
def main():
    host = "127.0.0.1"
    port = 5000
 
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
 
    username = input("Enter your username: ")
    client_socket.sendall(username.encode())
 
    while True:
        print("\nMain Menu:")
        print("1. Search headlines")
        print("2. List sources")
        print("3. Quit")
        choice = input("Enter your choice: ")
 
        if choice == "1":
            handle_headlines(client_socket)
        elif choice == "2":
            handle_sources(client_socket)
        elif choice == "3":
            send_request(client_socket, {"action": "quit"})
            print("Goodbye!")
            break
        else:
            print("Invalid choic.")
 
    client_socket.close()
 
if __name__ == "__main__":
    main()