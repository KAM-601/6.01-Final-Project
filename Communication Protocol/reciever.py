# Echo client program
import socket

HOST = input('Please provide a host to connect to: ')
PORT = 6010    # The same port as the server



with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b'ready')
    counter = 100
    while True:
      data = s.recv(1024)
      print('Received', repr(data))
      counter += 1
      if counter > 1000000:
        s.sendall(b'stop')
      else:
        s.sendall(bytes(counter))