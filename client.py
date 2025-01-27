import socket
from colorama import Style, Fore
from threading import Thread


class Client:
    REQUIRED_PRIVATE_MESSAGE_PARTS = 2

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    def run(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect((self.host, self.port))
        except ConnectionRefusedError:
            print(Fore.RED + '\nNão foi possível conectar ao servidor. Verifique se ele está ativo!' + Style.RESET_ALL)
            return

        username = input('\nDigite seu nome de usuário: ').strip()
        if not username:
            print(Fore.RED + 'Nome de usuário inválido. Encerrando conexão.' + Style.RESET_ALL)
            return

        try:
            try:
                client_socket.send(username.encode('utf-8'))
                response = client_socket.recv(1024).decode()
                header = response[:10].strip()
                message = response[10:]
                if header == 'ERROR':
                    print(Fore.YELLOW + f'Erro recebido do servidor: {message}' + Style.RESET_ALL)
                    return
                elif header == 'OK':
                    print(Fore.GREEN + f'\n{message}' + Style.RESET_ALL)  # Mensagem de sucesso
                else:
                    print(Fore.RED + '\nResposta inesperada do servidor. Encerrando conexão.' + Style.RESET_ALL)
                    return
            except:
                print(Fore.RED + 'Erro ao enviar o nome de usuário. Encerrando conexão.' + Style.RESET_ALL)
                return

            thread_receive = Thread(target=self.receive_message, args=[client_socket])
            thread_send = Thread(target=self.send_messages, args=[client_socket, username])

            thread_receive.start()
            thread_send.start()

            # Aguarda ambas as threads finalizarem
            thread_receive.join()
            thread_send.join()
        except KeyboardInterrupt:
            print(Fore.YELLOW + '\nConexão interrompida manualmente. Encerrando...' + Style.RESET_ALL)

    def receive_message(self, client_socket: socket.socket):
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
                    print(Fore.YELLOW + 'Formato inválido para mensagem privada. Use: @username mensagem' + Style.RESET_ALL)
                    continue
                client_socket.send(message.encode('utf-8'))
        except (ConnectionResetError, BrokenPipeError):
            print(Fore.RED + '\nErro ao enviar mensagem. Conexão encerrada!' + Style.RESET_ALL)
        finally:
            client_socket.close()


if __name__ == '__main__':
    client = Client('localhost', 50000)
    client.run()
