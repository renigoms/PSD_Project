import platform
import select
import socket
import sys
import threading
from threading import Thread

from colorama import Style, Fore

from constants import REQUIRED_MESSAGE_PARTS


class Client:

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.running = threading.Event()
        self.running.set()

    def run(self):
        client_socket = self._connect_to_server()
        if not client_socket:
            return
        username = Client._get_username()
        if not username:
            return
        if not Client._authenticate_user(client_socket, username):
            return
        self._start_message_threads(client_socket, username)

    @staticmethod
    def _get_username():
        try:
            username = input('\nDigite seu nome de usuário: ').strip()
            if not username:
                print(Fore.RED + 'Nome de usuário inválido. Encerrando conexão.' + Style.RESET_ALL)
            return username
        except KeyboardInterrupt:
            print(Fore.YELLOW + '\nEntrada cancelada pelo usuário. Encerrando conexão...' + Style.RESET_ALL)
            return None

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

    def _start_message_threads(self, client_socket: socket.socket, username: str):
        try:
            thread_receive = Thread(target=Client._receive_message, args=[client_socket])
            thread_send = Thread(target=self._send_messages, args=[client_socket, username])

            thread_receive.start()
            thread_send.start()

            # Aguarda ambas as threads finalizarem
            thread_receive.join()
            thread_send.join()
        except KeyboardInterrupt:
            self.running.clear()  # Desativa a flag, indicando que o programa está encerrando
            print(Fore.YELLOW + '\nEncerrando conexão...' + Style.RESET_ALL)
            try:
                client_socket.send('-sair'.encode('utf-8'))  # Envia comando de saída ao servidor
            except (BrokenPipeError, OSError):
                pass  # Se a conexão já estiver encerrada, não faz nada
            finally:
                client_socket.close()
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
            except OSError as e:
                print(Fore.RED + f'\nErro no socket: {e}' + Style.RESET_ALL)
                break

    def _send_messages(self, client_socket: socket.socket, username: str):
        try:
            while self.running.is_set():
                # Usa select para verificar se há entrada disponível no stdin
                message = Client.check_stdin()
                if message is None:
                    continue
                if not message:
                    print(Fore.RED + 'Mensagem vazia. Digite algo válido.' + Style.RESET_ALL)
                    continue
                if message == '-sair':
                    client_socket.send(message.encode('utf-8'))
                    print(Fore.YELLOW + f"{username} solicitou desconexão." + Style.RESET_ALL)
                    break
                if message == '-listargrupos':
                    client_socket.send(message.encode('utf-8'))
                    continue
                if message.startswith('-criargrupo '):
                    parts = message.split(' ', 1)  # Divide em 2 partes, o comando e o nome do grupo
                    if not parts[1].strip():  # Verifica se o nome do grupo está vazio ou só tem espaços
                        print(Fore.YELLOW
                              + 'Erro: Nome do grupo não pode estar vazio. Use: -criargrupo <nome_do_grupo>'
                              + Style.RESET_ALL)
                        continue
                    client_socket.send(message.encode('utf-8'))
                    continue
                parts = message.split(' ', 3)  # Divide em até 4 partes: comando, "tag", username e mensagem
                if len(parts) != REQUIRED_MESSAGE_PARTS and message.startswith('-msg'):
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
                client_socket.send(message.encode('utf-8'))
        except (ConnectionResetError, BrokenPipeError):
            print(Fore.RED + '\nErro ao enviar mensagem. Conexão encerrada!' + Style.RESET_ALL)
        finally:
            client_socket.close()
            print(Fore.YELLOW + "Conexão encerrada." + Style.RESET_ALL)

    @staticmethod
    def check_stdin():
        if platform.system() == 'Windows':
            import msvcrt
            # No Windows, usa msvcrt para verificar se há dados no stdin
            if msvcrt.kbhit():
                return sys.stdin.readline().strip()
            return None
        # No Linux/macOS, usa select para verificar se há dados no stdin
        if sys.stdin in select.select([sys.stdin], [], [], 0.1)[0]:
            return input().strip()
        return None


if __name__ == '__main__':
    client = Client('localhost', 50000)
    client.run()
