import socket
import http.client

PORT = 6010    # The same port as the server



# --------------------------------
# GET IP ADDRESS FROM COMMON POINT
# --------------------------------
h1 = http.client.HTTPConnection('next205.mit.edu')
h1.request('GET', '/glove')
res = h1.getresponse();
HOST = res.read().decode('UTF-8')


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
