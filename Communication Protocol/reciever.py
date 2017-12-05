# This is reciever side code, It contains a number of functions that would be useful for the reciever (robot side)
import sys
import socket

class Reciever:
  #class variables
      
  def __init__(self, dataHandler):
    self.Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # construct a socket 
    self.handler = dataHandler
    self.listening = True

  def connect(self, HOST='localhost', PORT='6010'):
    try:
      self.Socket.connect((HOST, PORT))
    except socket.error:
      print('Failed to connect to Server')
      return
    try:
      while self.listening:
        self.Socket.sendall(b'Ready')
        data = self.Socket.recv(1024) # stall until data recieved from the server
        self.listening = self.handler(data) # set listening to the return value of the listener
    except:
      print('Server communication broken')
    finally:
      self.Socket.close()
