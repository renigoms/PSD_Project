from threading import Thread

from colorama import Fore, Style

from module.server.server_model import Server


class ServerController:

    @staticmethod
    def run(host, port):
        from module.server.server_service import ServerService
        server_service = ServerService()
        try:
            server = Server(host, port)
            server.server_socket.bind((host, port))
            server.server_socket.listen()
            print(Fore.GREEN + f"Servidor iniciado em {host}:{port}" + Style.RESET_ALL)
        except OSError as e:
            print(Fore.RED + f"\nErro ao iniciar o servidor: {e}" + Style.RESET_ALL)
            return

        try:
            while True:
                client_socket, address = server.server_socket.accept()
                print(Fore.CYAN + f"Nova conexão de {address}" + Style.RESET_ALL)
                Thread(target=server_service.handle_new_client, args=(client_socket, address, server)).start()
        except KeyboardInterrupt:
            print(Fore.YELLOW + "\nServidor interrompido manualmente. Fechando conexões..." + Style.RESET_ALL)
        finally:
            server_service.shutdown(server)
