import signal
from socket import *

PORT = 8085

# Create a server socket, bind it to a port and start listening
tcpSerSock = socket(AF_INET, SOCK_STREAM)
tcpSerSock.bind(('127.0.0.1', PORT))
tcpSerSock.listen()

# keyboardInterrupt excpetion treatment


def at_exit(signum,  frame):
    print('exit')
    tcpSerSock.close()
    exit()


signal.signal(signal.SIGINT, at_exit)

while 1:
    # Strat receiving data from the client
    print('Ready to serve...')
    tcpCliSock, addr = tcpSerSock.accept()
    print('Received a connection from:', addr)
    message = tcpCliSock.recv(4096)  # Fill in start. # Fill in end.
    print('Received Message: ', message)
    # Extract the filename from the given message
    print('Splited Message: ', message.split()[1])
    filename = message.split()[1].partition(b"/")[2]
    print('Filename: ', filename)
    fileExist = False
    filetouse = b"/" + filename
    print('Filetouse: ', filetouse)
    try:
        # Check wether the file exist in the cache
        f = open(filetouse[1:], "rb")
        print('File found on cache')
        outputdata = f.read()
        fileExist = True
        # ProxyServer finds a cache hit and generates a response message
        response = b"HTTP/1.1 200 OK\r\n"
        response += b"Content-Type:text/html\r\n"
        response += b'\r\n'
        response += outputdata
        tcpCliSock.send(response)
        print('Reponse: ', response)
        print('Read from cache')
        # Error handling for file not found in cache
    except IOError:
        if fileExist == False:
            print('File not found in cache')
            # Create a socket on the proxkyserver
            c = socket(AF_INET, SOCK_STREAM)
            hostn = filename.replace(b"www.", b"", 1)
            print('Remote Hostname: ', hostn)
            try:
                ip = gethostbyname(hostn)
                print('Remote Host IP: ', ip)
                c.connect((ip, 80))

                c.send(b"GET / HTTP/1.1\r\nHost: " + hostn + b"\r\n\r\n")
                response = c.recv(4096)
                print('Response:', response)

                tcpCliSock.send(response)
                c.close()
            except error:
                response = b"HTTP/1.1 404 File Not Found\r\nContent-Type:text/html\r\n\r\n"
                tcpCliSock.send(response)
                tcpCliSock.close()
                print(error)
                print("Illegal request")
        else:
            response = b"HTTP/1.1 500 Internal Server Error\r\nContent-Type:text/html\r\n\r\n"
            tcpCliSock.send(response)
            tcpCliSock.close()
    # Close the client and the server sockets
    except:
        tcpCliSock.close()

    tcpCliSock.close()
