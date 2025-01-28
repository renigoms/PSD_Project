import socket

from colorama import Style, Fore


class ClientService:

    REQUIRED_PRIVATE_MESSAGE_PARTS = 2

    @staticmethod
    def receive_message(client_socket: socket.socket):
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

    def send_messages(self, client_socket: socket.socket, username: str):
        try:
            while True:
                message = input()
                if not message.strip():
                    print(Fore.RED + 'Mensagem vazia. Digite algo válido.' + Style.RESET_ALL)
                    continue
                if message.startswith('@') and len(message.split(' ', 1)) == self.REQUIRED_PRIVATE_MESSAGE_PARTS:
                    client_socket.send(message.encode('utf-8'))
                    continue
                if message.startswith('@'):
                    print(
                        Fore.YELLOW + 'Formato inválido para mensagem privada. Use: @username mensagem' + Style.RESET_ALL)
                    continue
                client_socket.send(message.encode('utf-8'))
        except (ConnectionResetError, BrokenPipeError):
            print(Fore.RED + '\nErro ao enviar mensagem. Conexão encerrada!' + Style.RESET_ALL)
        finally:
            client_socket.close()
