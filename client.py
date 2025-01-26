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

        except ConnectionRefusedError:
            print(Fore.RED + '\nNão foi possível conectar ao servidor. Verifique se ele está ativo!' + Style.RESET_ALL)
            return

        username = input('\nDigite seu nome de usuário: ').strip().capitalize()
        if not username:
            print(Fore.RED + 'Nome de usuário inválido. Encerrando conexão.' + Style.RESET_ALL)
            return

        try:
            try:
                client_socket.send(username.encode('utf-8'))
            except:
                print(Fore.RED + 'Erro ao enviar o nome de usuário. Encerrando conexão.' + Style.RESET_ALL)
                return

            print(Fore.GREEN + '\nConexão estabelecida com sucesso!' + Style.RESET_ALL)

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
                client_socket.send(message.encode('utf-8'))
        except (ConnectionResetError, BrokenPipeError):
            print(Fore.RED + '\nErro ao enviar mensagem. Conexão encerrada!' + Style.RESET_ALL)
        finally:
            client_socket.close()


if __name__ == '__main__':
    client = Client('localhost', 50000)
    client.run()
