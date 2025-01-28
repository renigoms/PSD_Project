import socket

from colorama import Style, Fore

from module.server.server_model import Server


class ServerService:

    @staticmethod
    def shutdown(server: Server):
        for client_socket in list(server.clients.keys()):
            client_socket.close()
        server.server_socket.close()
        print(Fore.RED + "Servidor fechado." + Style.RESET_ALL)

    def handle_new_client(self, client_socket: socket.socket, address: tuple, server: Server):
        try:
            name = client_socket.recv(1024).decode("utf-8").capitalize()
            if not name:
                client_socket.close()
                return
            if name in server.clients.values():
                header = 'ERROR'.ljust(10)
                message = 'Usuário já conectado'
                client_socket.send((header + message).encode('utf-8'))
                client_socket.close()
                return
            # Envia uma flag de sucesso para o cliente
            header = 'OK'.ljust(10)  # Header indicando sucesso
            message = 'Conexão estabelecida com sucesso!'
            client_socket.send((header + message).encode('utf-8'))
            server.clients[client_socket] = name
            print(Fore.BLUE + f"{name} ({address}) conectou-se ao servidor." + Style.RESET_ALL)

            # Mensagem de boas-vindas
            self._broadcast(f"{name} entrou no chat.", server, client_socket)

            # Começa a tratar mensagens desse cliente
            self._handle_client_messages(client_socket, server)
        except Exception as e:
            print(Fore.RED + f"Erro ao lidar com o cliente {address}: {e}" + Style.RESET_ALL)

    def _handle_client_messages(self, client_socket: socket.socket, server: Server):
        name = server.clients.get(client_socket, "Desconhecido")
        try:
            while True:
                message = client_socket.recv(1024).decode("utf-8").strip()
                if message:
                    if message.startswith('@'):
                        recipient_name, msg = message.split(' ', 1)
                        recipient_name = recipient_name[1:]
                        self._send_private_message(recipient_name, f'{name}: {msg}', client_socket)
                    else:
                        broadcast_message = f"{name}: {message}"
                        print(broadcast_message)
                        self._broadcast(broadcast_message, server, client_socket)
                else:
                    # Encerra a conexão se a mensagem estiver vazia
                    break
        except (ConnectionResetError, ConnectionAbortedError):
            print(Fore.RED + f"Conexão perdida com {name}." + Style.RESET_ALL)
        finally:
            self._remove_client(client_socket, server)

    def _broadcast(self, message: str, server: Server, sender_socket: socket.socket = None):
        for client_socket in list(server.clients.keys()):
            if client_socket != sender_socket:
                try:
                    client_socket.send(message.encode("utf-8"))
                except (ConnectionResetError, ConnectionAbortedError):
                    self._remove_client(client_socket, server)

    def _send_private_message(self, recipient_name: str, message: str, sender_socket: socket.socket, server: Server):
        for client_socket, client_name in server.clients.items():
            if client_name == recipient_name.capitalize():
                try:
                    client_socket.send(message.encode('utf-8'))
                    sender_name = server.clients.get(client_socket, 'Desconhecido')
                    print(
                        Fore.YELLOW + f'Mensagem privada de {sender_name} para {recipient_name}: {message}' + Style.RESET_ALL)
                except (ConnectionResetError, ConnectionAbortedError):
                    self._remove_client(client_socket, server)
                return
        sender_socket.send((Fore.RED + f'Erro: {recipient_name} não encontrado' + Style.RESET_ALL).encode())

    def _remove_client(self, client_socket: socket.socket, server: Server):
        name = server.clients.pop(client_socket, "Desconhecido")
        client_socket.close()
        print(Fore.YELLOW + f"{name} desconectou-se do servidor." + Style.RESET_ALL)

        # Mensagem de despedida
        self._broadcast(f"{name} saiu do chat.", server, None)
