import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from client import Client

if __name__ == '__main__':
    client = Client('localhost', 50001)
    client.run()
