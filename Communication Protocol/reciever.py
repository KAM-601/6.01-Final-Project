# Echo client program
import socket
import http.client

HOST = input('Please provide a host to connect to: ')
PORT = 6010    # The same port as the server


h1 = http.client.HTTPConnection('www.python.org')

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b'ready')
    while True:
      data = s.recv(1024)
      print(data.decode('UTF-8'))
      sendData = input("Send data to server:").encode()
      s.sendall(sendData)
