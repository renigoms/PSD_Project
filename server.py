import socket
from threading import Thread
from colorama import Fore, Style


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = {}
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run(self):
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen()
            print(Fore.GREEN + f"Servidor iniciado em {self.host}:{self.port}" + Style.RESET_ALL)
        except OSError as e:
            print(Fore.RED + f"\nErro ao iniciar o servidor: {e}" + Style.RESET_ALL)
            return

        try:
            while True:
                client_socket, address = self.server_socket.accept()
                print(Fore.CYAN + f"Nova conexão de {address}" + Style.RESET_ALL)
                Thread(target=self.handle_new_client, args=(client_socket, address)).start()
        except KeyboardInterrupt:
            print(Fore.YELLOW + "\nServidor interrompido manualmente. Fechando conexões..." + Style.RESET_ALL)
        finally:
            self.shutdown()

    def handle_new_client(self, client_socket: socket.socket, address: tuple):
        try:
            name = client_socket.recv(1024).decode("utf-8").capitalize()
            if not name:
                client_socket.close()
                return
            if name in self.clients.values():
                header = 'ERROR'.ljust(10)
                message = 'Usuário já conectado'
                client_socket.send((header + message).encode('utf-8'))
                client_socket.close()
                return
            # Envia uma flag de sucesso para o cliente
            header = 'OK'.ljust(10)  # Header indicando sucesso
            message = 'Conexão estabelecida com sucesso!'
            client_socket.send((header + message).encode('utf-8'))
            self.clients[client_socket] = name
            print(Fore.BLUE + f"{name} ({address}) conectou-se ao servidor." + Style.RESET_ALL)

            # Mensagem de boas-vindas
            self.broadcast(f"{name} entrou no chat.", client_socket)

            # Começa a tratar mensagens desse cliente
            self.handle_client_messages(client_socket)
        except Exception as e:
            print(Fore.RED + f"Erro ao lidar com o cliente {address}: {e}" + Style.RESET_ALL)

    def handle_client_messages(self, client_socket: socket.socket):
        name = self.clients.get(client_socket, "Desconhecido")
        try:
            while True:
                message = client_socket.recv(1024).decode("utf-8").strip()
                if message:
                    if message.startswith('@'):
                        recipient_name, msg = message.split(' ', 1)
                        recipient_name = recipient_name[1:]
                        self.send_private_message(recipient_name, f'{name}: {msg}', client_socket)
                    else:
                        broadcast_message = f"{name}: {message}"
                        print(broadcast_message)
                        self.broadcast(broadcast_message, client_socket)
                else:
                    # Encerra a conexão se a mensagem estiver vazia
                    break
        except (ConnectionResetError, ConnectionAbortedError):
            print(Fore.RED + f"Conexão perdida com {name}." + Style.RESET_ALL)
        finally:
            self.remove_client(client_socket)

    def broadcast(self, message: str, sender_socket: socket.socket = None):
        for client_socket in list(self.clients.keys()):
            if client_socket != sender_socket:
                try:
                    client_socket.send(message.encode("utf-8"))
                except (ConnectionResetError, ConnectionAbortedError):
                    self.remove_client(client_socket)

    def remove_client(self, client_socket: socket.socket):
        name = self.clients.pop(client_socket, "Desconhecido")
        client_socket.close()
        print(Fore.YELLOW + f"{name} desconectou-se do servidor." + Style.RESET_ALL)

        # Mensagem de despedida
        self.broadcast(f"{name} saiu do chat.", None)

    def shutdown(self):
        for client_socket in list(self.clients.keys()):
            client_socket.close()
        self.server_socket.close()
        print(Fore.RED + "Servidor fechado." + Style.RESET_ALL)

    def send_private_message(self, recipient_name: str, message: str, sender_socket: socket.socket):
        for client_socket, client_name in self.clients.items():
            if client_name == recipient_name.capitalize():
                try:
                    client_socket.send(message.encode('utf-8'))
                    sender_name = self.clients.get(client_socket, 'Desconhecido')
                    print(Fore.YELLOW + f'Mensagem privada de {sender_name} para {recipient_name}: {message}' + Style.RESET_ALL)
                except (ConnectionResetError, ConnectionAbortedError):
                    self.remove_client(client_socket)
                return
        sender_socket.send((Fore.RED + f'Erro: {recipient_name} não encontrado' + Style.RESET_ALL).encode())


if __name__ == '__main__':
    server = Server('localhost', 50001)
    server.run()
