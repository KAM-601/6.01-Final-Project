import reciever
import server

def EasyHandle(data):
  print(data)
  return True



R = reciever.Reciever(EasyHandle)
R.connect('localhost', 10000)


S = server.Server()