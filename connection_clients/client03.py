# from client import Client
from module.client.client_controller import ClientController

if __name__ == '__main__':
    # client = Client('localhost', 50001)
    # client.run()
    client = ClientController()
    client.run('localhost', 50001)
