import socket
from threading import Thread

from colorama import Fore, Style

from module.client.client_service import ClientService


class ClientController:
    client_service = ClientService()

    def run(self, host: str, port: int):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect((host, port))
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

            thread_receive = Thread(target=self.client_service.receive_message, args=[client_socket])
            thread_send = Thread(target=self.client_service.send_messages, args=[client_socket, username])

            thread_receive.start()
            thread_send.start()

            # Aguarda ambas as threads finalizarem
            thread_receive.join()
            thread_send.join()
        except KeyboardInterrupt:
            print(Fore.YELLOW + '\nConexão interrompida manualmente. Encerrando...' + Style.RESET_ALL)
