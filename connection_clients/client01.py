from client import Client

if __name__ == '__main__':
    client = Client('localhost', 50001)
    client.run()
