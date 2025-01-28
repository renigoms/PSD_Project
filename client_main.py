from module.client.client_controller import ClientController

if __name__ == '__main__':
    client = ClientController()
    client.run('localhost', 50001)
