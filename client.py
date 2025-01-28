import socket
from colorama import Style, Fore
from threading import Thread
from constants import REQUIRED_MESSAGE_PARTS


class Client:

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    def run(self):
        client_socket = self._connect_to_server()
        if not client_socket:
            return
        username = Client._get_username()
        if not username:
            return
        if not Client._authenticate_user(client_socket, username):
            return
        Client._start_message_threads(client_socket, username)

    @staticmethod
    def _get_username():
        username = input('\nDigite seu nome de usuário: ').strip()
        if not username:
            print(Fore.RED + 'Nome de usuário inválido. Encerrando conexão.' + Style.RESET_ALL)
        return username

    def _connect_to_server(self) -> socket.socket | None:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect((self.host, self.port))
            return client_socket
        except ConnectionRefusedError:
            print(Fore.RED + '\nNão foi possível conectar ao servidor. Verifique se ele está ativo!' + Style.RESET_ALL)
            return None

    @staticmethod
    def _authenticate_user(client_socket: socket.socket, username: str) -> bool:
        try:
            client_socket.send(username.encode('utf-8'))
            response = client_socket.recv(1024).decode()
            header = response[:10].strip()
            message = response[10:]
            if header == 'ERROR':
                print(Fore.YELLOW + f'Erro recebido do servidor: {message}' + Style.RESET_ALL)
                return False
            elif header == 'OK':
                print(Fore.GREEN + f'\n{message}' + Style.RESET_ALL)  # Mensagem de sucesso
                return True
            else:
                print(Fore.RED + '\nResposta inesperada do servidor. Encerrando conexão.' + Style.RESET_ALL)
                return False
        except Exception as e:
            print(Fore.RED + f'Erro ao enviar o nome de usuário. Encerrando conexão. \n{e}' + Style.RESET_ALL)
            return False

    @staticmethod
    def _start_message_threads(client_socket: socket.socket, username: str):
        try:
            thread_receive = Thread(target=Client._receive_message, args=[client_socket])
            thread_send = Thread(target=Client._send_messages, args=[client_socket, username])

            thread_receive.start()
            thread_send.start()

            # Aguarda ambas as threads finalizarem
            thread_receive.join()
            thread_send.join()
        except KeyboardInterrupt:
            print(Fore.YELLOW + '\nConexão interrompida manualmente. Encerrando...' + Style.RESET_ALL)

    @staticmethod
    def _receive_message(client_socket: socket.socket):
        while True:
            try:
                message = client_socket.recv(1024).decode('utf-8')
                if not message:
                    break
                print(Fore.YELLOW + message + Style.RESET_ALL)
            except ConnectionResetError:
                print(Fore.RED + '\nConexão perdida com o servidor!' + Style.RESET_ALL)
                print('Pressione <Enter> para sair...')
                client_socket.close()
                break

    @staticmethod
    def _send_messages(client_socket: socket.socket, username: str):
        try:
            while True:
                message = input()
                if not message.strip():
                    print(Fore.RED + 'Mensagem vazia. Digite algo válido.' + Style.RESET_ALL)
                    continue
                parts = message.split(' ', 3)  # Divide em até 4 partes: comando, "tag", username e mensagem
                if len(parts) != REQUIRED_MESSAGE_PARTS or not message.startswith('-msg'):
                    print(
                        Fore.YELLOW
                        + 'Formato inválido para mensagem. Use: -msg tag <usuário|grupo> <mensagem>'
                        + '\nSubstitua tag por U mensagem privada G grupo'
                        + Style.RESET_ALL
                    )
                    continue
                if message.startswith('-msg') and parts[1].upper() == 'U':
                    client_socket.send(message.encode('utf-8'))
                    continue
                else:
                    print(
                        Fore.YELLOW
                        + 'Formato inválido para mensagem privada. Use: -msg U <usuário> <mensagem>'
                        + Style.RESET_ALL
                    )
                    continue
        except (ConnectionResetError, BrokenPipeError):
            print(Fore.RED + '\nErro ao enviar mensagem. Conexão encerrada!' + Style.RESET_ALL)
        finally:
            client_socket.close()


if __name__ == '__main__':
    client = Client('localhost', 50000)
    client.run()
