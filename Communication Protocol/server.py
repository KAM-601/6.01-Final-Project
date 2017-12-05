import socket
import sys

class Server:
  
  def __init__(self, handler):
    # create server socket
    self.Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.handler = handler
    self.connection = None

  def start(self,HOST='localhost', PORT = 6010):
    self.Socket.bind((HOST, PORT))
    self.Socket.listen(1)
    self.connection, client_address = self.Socket.accept()
    
  def sendData(self, data):
    try:
      if self.connection:
        self.connection.sendall(data)
        return True
      else:
        return False
    except:
      print("could not send data to client")

  def close(self):
    self.connection.close()
    self.Socket.close()
