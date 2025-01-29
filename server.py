import socket
from threading import Thread
from colorama import Fore, Style
from constants import REQUIRED_MESSAGE_PARTS
from datetime import datetime


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = {}
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run(self):
        self._start_server()
        self._accept_connections()

    def _start_server(self):
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen()
            print(Fore.GREEN + f"Servidor iniciado em {self.host}:{self.port}" + Style.RESET_ALL)
        except OSError as e:
            print(Fore.RED + f"\nErro ao iniciar o servidor: {e}" + Style.RESET_ALL)
            return

    def _accept_connections(self):
        try:
            while True:
                client_socket, address = self.server_socket.accept()
                print(Fore.CYAN + f"Nova conexão de {address}" + Style.RESET_ALL)
                Thread(target=self._handle_new_client, args=(client_socket, address)).start()
        except KeyboardInterrupt:
            print(Fore.YELLOW + "\nServidor interrompido manualmente. Fechando conexões..." + Style.RESET_ALL)
        finally:
            self._shutdown()

    def _handle_new_client(self, client_socket: socket.socket, address: tuple):
        try:
            username = self._receive_username(client_socket)
            if not username:
                return
            Server._send_success_response(client_socket, 'Conexão estabelecida com sucesso!')
            self.clients[client_socket] = username
            print(Fore.BLUE + f"{username} ({address}) conectou-se ao servidor." + Style.RESET_ALL)

            # Mensagem de boas-vindas
            self._broadcast(f"{username} entrou no chat.", client_socket)

            # Começa a tratar mensagens desse cliente
            self._handle_client_messages(client_socket)
        except Exception as e:
            print(Fore.RED + f"Erro ao lidar com o cliente {address}: {e}" + Style.RESET_ALL)

    def _receive_username(self, client_socket: socket.socket) -> str:
        username = client_socket.recv(1024).decode('utf-8').capitalize()
        if not username:
            client_socket.close()
            return ''
        if username in self.clients.values():
            Server._send_error_response(client_socket, 'Usuário já conectado')
            client_socket.close()
            return ''
        return username

    def _handle_client_messages(self, client_socket: socket.socket):
        msg = ''
        username = self.clients.get(client_socket, "Desconhecido")
        try:
            while True:
                message = client_socket.recv(1024).decode("utf-8").strip()
                if not message:
                    continue
                if message.startswith('-msg') and REQUIRED_MESSAGE_PARTS == len((parts := message.split(' ', 3))):
                    command, tag, recipient_name, msg = parts
                    if command == '-msg' and tag.upper() == 'U':
                        self._handle_private_message(client_socket, recipient_name, msg)
                    else:
                        broadcast_message = f"{username}: {message}"
                        print(broadcast_message)
                        self._broadcast(broadcast_message, client_socket)
                elif message == '-listarusuarios':
                    self._send_user_list(client_socket)
                else:
                    continue
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
            print(Fore.RED + f"Conexão perdida com {username}." + Style.RESET_ALL)
        finally:
            self._remove_client(client_socket)

    def _handle_private_message(self, client_socket: socket.socket, sender_username: str, message: str):
        formatted_message = f'({sender_username}, {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}): {message}'
        self._send_private_message(sender_username, formatted_message, client_socket)

    def _send_private_message(self, recipient_name: str, message: str, sender_socket: socket.socket):
        for client_socket, client_name in self.clients.items():
            if client_name == recipient_name.capitalize():
                try:
                    Server.send_message_safe(client_socket, message)
                    sender_name = self.clients.get(client_socket, 'Desconhecido')
                    print(
                        Fore.YELLOW
                        + f'Mensagem privada de {sender_name} para {recipient_name}: {message}'
                        + Style.RESET_ALL
                    )
                except (ConnectionResetError, ConnectionAbortedError):
                    self._remove_client(client_socket)
                return
        sender_socket.send((Fore.RED + f'Erro: {recipient_name} não encontrado' + Style.RESET_ALL).encode())

    def _broadcast(self, message: str, sender_socket: socket.socket = None):
        for client_socket in list(self.clients.keys()):
            if client_socket != sender_socket:
                try:
                    Server.send_message_safe(client_socket, message)
                except (ConnectionResetError, ConnectionAbortedError):
                    self._remove_client(client_socket)

    def _remove_client(self, client_socket: socket.socket):
        username = self.clients.pop(client_socket, "Desconhecido")
        client_socket.close()
        print(Fore.YELLOW + f"{username} desconectou-se do servidor." + Style.RESET_ALL)

        # Mensagem de despedida
        self._broadcast(f"{username} saiu do chat.", None)

    def _shutdown(self):
        for client_socket in list(self.clients.keys()):
            client_socket.close()
        self.server_socket.close()
        print(Fore.RED + "Servidor fechado." + Style.RESET_ALL)

    @staticmethod
    def _send_success_response(client_socket: socket.socket, message: str):
        header = 'OK'.ljust(10)
        client_socket.send((header + message).encode('utf-8'))

    @staticmethod
    def _send_error_response(client_socket: socket.socket, mensagem: str):
        header = 'ERROR'.ljust(10)
        client_socket.send((header + mensagem).encode('utf-8'))

    @staticmethod
    def send_message_safe(client_socket: socket.socket, message):
        try:
            client_socket.send(message.encode('utf-8'))
        except (BrokenPipeError, ConnectionResetError) as e:
            print(Fore.RED + f"Erro ao enviar mensagem: {e}" + Style.RESET_ALL)
            # Aqui você pode fechar a conexão ou remover o cliente da lista
            client_socket.close()

    def _send_user_list(self, client_socket: socket.socket):
        """Envia a lista de todos os usuários conectados para o cliente"""
        users = '\n'.join(self.clients.values())
        try:
            client_socket.send((Fore.CYAN + 'Usuários online:\n' + users + Style.RESET_ALL).encode('utf-8'))
        except (ConnectionResetError, ConnectionAbortedError):
            self._remove_client(client_socket)


if __name__ == '__main__':
    server = Server('localhost', 50001)
    server.run()
