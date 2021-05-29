import socket
import argparse
import threading
from hashlib import md5
from base64 import b64decode

def clientUDP():
    # print("INICIO DE UDP")
    global msg

    #Set UDP socket
    socket_UDP = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    # Set UDP bind
    try:
        socket_UDP.bind(('0.0.0.0',10000))
    except socket.error as err:
        print('\nCliente UDP:\n',err.strerror)
        return
    #Set timeout limit in seconds
    socket_UDP.settimeout(5)
    
    try:
        msg,addr = socket_UDP.recvfrom(65507)
        if (client_mode == 'a' or client_mode == 'A'):
            print("Cliente UDP: Mensaje recibido desde",addr,"\n",b64decode(msg).decode('utf-8'),"\n")
        else:
            print("Mensaje recibido:\n",b64decode(msg).decode('utf-8'),"\n")
    except socket.timeout:
        print('Cliente UDP: Error agotado tiempo de espera')
        
    socket_UDP.close()
    # print("FIN DE UDP")

def clientTCP():
    #print("INICIO DE TCP")
    global t2
    global msg
    global client_server_IP
    global client_port

    socket_TCP = socket.socket()
    try:
        socket_TCP.connect( (client_server_IP,client_port) )  
    except socket.error as err:
        print('\nCliente TCP:\n',err.strerror)
        return
    
    comand_to_send = "helloiam "+client_user

    try:
        socket_TCP.send(comand_to_send.encode('utf-8'))
        ans = socket_TCP.recv(1024)
        if(ans != b'ok\n'):
            print('\nCliente TCP:',ans.decode('utf-8'))
            socket_TCP.close()
            return
        if (client_mode == 'a' or client_mode == 'A'):
            print('\nCliente TCP: Usuario',client_user,'autenticado')
        else:
            print('\nUsuario',client_user,'autenticado')
    except socket.error as err:
        print('\nCliente TCP:',err.strerror)
        return

    comand_to_send = "msglen"

    try:
        socket_TCP.send(comand_to_send.encode('utf-8'))
        ans = socket_TCP.recv(1024)
        if (client_mode == 'a' or client_mode == 'A'):
            print('\nCliente TCP: Tamaño del mensaje',ans.decode('utf-8').replace('ok ',''))

    except socket.error as err:
        print('\nCliente TCP:',err.strerror)
        return

    # Send Meessage 4 times

    comand_to_send = "givememsg 10000"

    for i in range(4):
        #Create thread for client UDP
        t2 = threading.Thread(target=clientUDP)
        t2.start()
        try:
            socket_TCP.send(comand_to_send.encode('utf-8'))
            ans = socket_TCP.recv(1024)
            if(ans != b'ok\n'):
                print('\nCliente TCP:',ans.decode('utf-8'))
                
            if (client_mode == 'a' or client_mode == 'A'):
                print('\nCliente TCP: Mensaje enviado\n')
            
            t2.join()#wait for UDP thread
        
        except socket.error as err:
            print('\nCliente TCP:',err.strerror)
            t2.join()#wait for UDP thread

        if(msg == 'void'):
            print('\nCliente TCP: Mensaje perdido')
            
        dato = md5(b64decode(msg))
        comand_to_send = "chkmsg "+ dato.hexdigest()

        try:
            socket_TCP.send(comand_to_send.encode('utf-8'))
            ans = socket_TCP.recv(1024)
            if(ans != b'ok\n'):
                print('\nCliente TCP:',ans.decode('utf-8'))
                
            if (client_mode == 'a' or client_mode == 'A'):
                print('\nCliente TCP: Mensaje validado')
            break
        except socket.error as err:
            print('\nCliente TCP:',err.strerror)

    comand_to_send = "bye"

    try:
        socket_TCP.send(comand_to_send.encode('utf-8'))
        ans = socket_TCP.recv(1024)
        if (client_mode == 'a' or client_mode == 'A'):
            print('\nCliente TCP: Conexion terminada')
        
    except socket.error as err:
        print('\nCliente TCP:',err.strerror)
        return

    socket_TCP.close()
    #print("FIN DE TCP")

def main():
    #default vaules
    global client_server_IP
    global client_port
    global client_user
    global client_mode
    global msg

    msg = 'void'
    client_server_IP = '10.2.126.2'
    client_port = 19876
    client_user = "jrequena.17"
    client_mode = "s"
    client_mode_show = "Basico"
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-u","--user",type=str, help='Establece el numbre de usuario a utilizar')
    parser.add_argument("-p","--port",type=str, help='Establece el puerto a utilizar')
    parser.add_argument("-s","--server",type=str, help='Establece la dirección IP a utilizar')
    parser.add_argument("-m","--mode",type=str, help="Establece el tipo de usuario: s=standard(deafult) a=admin")
    valor = parser.parse_args()
    
    if(valor.user):
        client_user = valor.user
    
    if(valor.server):
        client_server_IP = valor.server

    if(valor.port):
        client_port = int(valor.port)

    if(valor.mode):
        client_mode = valor.mode
    
    if (client_mode == 'a' or client_mode == 'A'):
        client_mode_show = "Administrador"

    #Show data to use
    print("Configuración\nUsuario:",client_user,"\nDirección IP:",client_server_IP,"\nPuerto",client_port,"\nModo:",client_mode_show,"\n")

    global t1
    global t2

    #Create thread for clenT TCP
    t1 = threading.Thread(target=clientTCP)

    #start threads
    t1.start()
    
    t1.join()
    #finish the thread if clientTCP can't continue
    if(t2.is_alive):
        t2.join()

if __name__ == '__main__':
    main()