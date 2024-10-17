
import uuid
from client_server_group20 import server
from client_server_group20 import client_input
import threading
import time

# We generate our own ID for the protocol
personal_id = str(uuid.uuid4())

if __name__ == '__main__':
    server_thread = threading.Thread(target = server, args = (personal_id, ))
    client_thread = threading.Thread(target = client_input, args = (personal_id, ))

    server_thread.start()
    time.sleep(1)
    client_thread.start()

    server_thread.join()
    client_thread.join()
