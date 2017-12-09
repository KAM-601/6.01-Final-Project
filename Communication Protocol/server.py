import socket
import time
# Function to Figure out what IP address we are using,
# using the following code snippet: https://stackoverflow.com/questions/24196932/how-can-i-get-the-ip-address-of-eth0-in-python

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))  # we don't actually care about connecting to the google DNS, instead we are using the
    return s.getsockname()[0]   # garbage collector to remove our socket on return



HOSTNAME = get_ip_address()
PORT = 6010



# create the server socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOSTNAME, PORT))
    s.listen(1)
    print("Now Listening on: " + str(HOSTNAME) + ":" + str(PORT))
    while True:
        connection, addr = s.accept()
        print("Connection to " + str(addr) + " initialized")
        with connection:
            while True:             # this would be the main loop of the glove brain
                data = connection.recv(1024)
                literal = data.decode('UTF-8')
                if literal == 'stop':
                    connection.close()
                literal = literal.upper()
                connection.sendall(literal.encode())
        connection.close()
    print("Connection to " + str(addr) + " closed")
