if __name__ == '__main__':
    from module.server.server_controller import ServerController
    server = ServerController()
    server.run('localhost', 50001)
