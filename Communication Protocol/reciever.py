# Echo client program
import socket
import http.client

HOST = input('Please provide a host to connect to: ')
PORT = 6010    # The same port as the server


#h1 = http.client.HTTPConnection('www.python.org')


def loop(data):
  return None


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
  s.connect((HOST, PORT))
  s.sendall(b'ready')
  while True:
    data = s.recv(1024)
    data = data.decode('UTF-8')

    ### RUN THE MAIN LOOP OF THE RECIEVER
    print(data)
    sendData = loop(data)

    if sendData != None:
      s.sendall(sendData.encode('UTF-8'))
