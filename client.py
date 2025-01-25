import socket
from colorama import Style, Fore
from threading import Thread


class Client:

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    def run(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            client_socket.connect((self.host, self.port))
        except:
            return print(Fore.RED + '\nit was not possible to connect to the server !!!\n' + Style.RESET_ALL)

        username = input('\nUsername > ')
        print(Fore.GREEN + '\nConnected user!' + Style.RESET_ALL)

        thread01 = Thread(target=self.receive_message, args=[client_socket])
        thread02 = Thread(target=self.send_messages, args=[client_socket, username])

        thread01.start()
        thread02.start()

    def receive_message(self, client_socket: socket):
        while True:
            try:
                message = client_socket.recv(1024).decode('utf-8')
                print(Fore.YELLOW+message + '\n'+Style.RESET_ALL)
            except:
                print(Fore.RED + '\nit was not possible stay to connect on to the server !!\n' + Style.RESET_ALL)
                print('Press <Enter> to continue...')
                client_socket.close()
                break

    def send_messages(self, client_socket: socket, username: str):
        while True:
            try:
                message = input('\n')
                client_socket.send(f'{username}: {message}'.encode('utf-8'))
            except:
                return



if __name__ == '__main__':
    client = Client('localhost', 50000)
    client.run()


