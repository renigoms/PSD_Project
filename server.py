import socket
from threading import Thread

from colorama import Fore, Style


class Server:
    clients = []

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def run(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            server_socket.bind((self.host, self.port))
            server_socket.listen()
        except:
            return print(Fore.RED + '\nIt was not possible to start on to the server !!' + Style.RESET_ALL)

        while True:
            client, addr = server_socket.accept()
            self.clients.append(client)

            thread = Thread(target=self.messages_treatment, args=(client,))
            thread.start()

    def messages_treatment(self, client_socket: socket):
        while True:
            try:
                message = client_socket.recv(1024)
                self.broadcast(message, client_socket)
            except:
                self.delete_client(client_socket)
                break

    def broadcast(self, message: str, client: socket):
        for client_item in self.clients:
            if client_item != client:
                try:
                    client_item.send(message)
                except:
                    self.delete_client(client_item)

    def delete_client(self, client: socket):
        self.clients.remove(client)


if __name__ == '__main__':
    server = Server('localhost', 50000)
    server.run()
