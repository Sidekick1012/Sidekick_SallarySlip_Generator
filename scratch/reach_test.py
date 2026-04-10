import socket
import timeout_decorator # Using a custom timeout might help if it hangs

def test_connection(host, port):
    print(f"Testing connection to {host}:{port}...")
    try:
        # Create a socket object
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        # Connect to the server
        s.connect((host, port))
        print(f"SUCCESS: Connected to {host}:{port}")
        s.close()
    except Exception as e:
        print(f"FAILED to connect to {host}:{port}: {e}")

if __name__ == "__main__":
    test_connection("smtp.gmail.com", 587)
    test_connection("smtp.gmail.com", 465)
