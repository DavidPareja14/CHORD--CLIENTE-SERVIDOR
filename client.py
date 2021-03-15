"""
Desarrollado por David Pareja Arango

Para subir archivos, procure que los nombres de los archivos no esten con - (guiones).
"""

import sys
import zmq
import hashlib
import json
import os #La utilizaré para eliminar las partes de archivos que sean descargados.

BUF_SIZE = 1024*1024*20
listaNombrePartes=[] #Me va a guardar el los hashes de todas las partes con su respectivo orden.

def hashesFile(filename):
    sha1 = hashlib.sha1()
    hashes=""
    with open(sys.argv[4] + "/" + filename, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            sha1.update(data)
            hashes+=sha1.hexdigest()+"-"
        sha1.update(filename.encode("utf-8'"))
        hashGeneralFile=sha1.hexdigest()
        hashes+=hashGeneralFile
    return hashes #La ultima cadena separada por - es el hash total del archivo

#Me convierte los hashes que estan en hexadecimal a enteros:
def hexToInt(hashes):
    hashesEnteros=[]
    for has in hashes:
        hashEntero=int(has, 16)%64
        hashesEnteros.append(hashEntero)
    return hashesEnteros

#Me va a retornar una lista con todas las partes del archivo en bits.
def partesDelArchivo(filename):
    contenidoHash=[]
    with open(sys.argv[4] + "/" + filename, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            contenidoHash.append(data)
    return contenidoHash

def enlistarNombrePartes(nombrePartes):
    for indiceParte in nombrePartes:
        listaNombrePartes.append(indiceParte)

def guardarParte(nombreParte, contenido):
    with open(sys.argv[4] + "/" + nombreParte, "wb") as f:
        f.write(contenido)

def juntarPartes(filename): #las partes tienen un orden y las juntare en ese orden.
	with open(sys.argv[4] + "/" + filename, 'ab') as f:
	    for i in range(len(listaNombrePartes)):
	        for parte in listaNombrePartes:
	            if i==parte[0]:
	                with open(sys.argv[4] + "/" + parte[1], 'rb') as contenidoParte:
	                    contenidoparteReal=contenidoParte.read()
	                    f.write(contenidoparteReal)
	                    contenidoParte.close()
	                    break
	eliminarPartes()

def eliminarPartes():
	for parte in listaNombrePartes:
		os.remove(sys.argv[4] + "/" + parte[1])

def main():
    if len(sys.argv) != 5: #La estructura es python client.py upload filename port nombreCarpetaCliente
        print("Error!!!")
        exit()

    context = zmq.Context()
    serverAddr = sys.argv[3]
    serverAddrOriginal = sys.argv[3]
    print(serverAddr)
    server = context.socket(zmq.REQ)
    server.connect("tcp://{}".format(serverAddr))

    message = sys.argv[1]
    filename = sys.argv[2]
    nombreReal="" #sirve para guardar el nombre real del archivo y no solo su hash
    

    if message == "upload":
        hashes = hashesFile(filename) #calcula los nombres de los hashes para cada archivo
        partes = partesDelArchivo(filename) #obtiene el contenido de cada parte.
        listaHashes=hashes.split("-")
        hashesEnteros = hexToInt(listaHashes) #obtengo los hashes como enteros hasta el num 64
        nombreReal=filename

        for numParte,hashInt in enumerate(hashesEnteros):
            #Debo romper el ciclo porque en realidad el numero de partes del archivo es la longitud de la lista hashesEnteros-1
            #ya que en la ultima posicion meto el hash general del archivo, y este no es una parte.
            if numParte==len(hashesEnteros)-1:
                break
            noEncuentreServidorResponsable=True
            server.send_string(message+" "+listaHashes[-1]+"-"+filename+" "+str(numParte)+" "+str(hashInt))
            respuestaServidor=server.recv_string() #El servidor responde si es el responsable, o si necesita esttablecer otra conexion.
            respuestaServidor=respuestaServidor.split(" ")
            if respuestaServidor[0]=="Responsable":
                server.send_multipart([listaHashes[numParte].encode("utf-8"), partes[numParte]]) #Envio en name del file en hash y el contenido.
                server.recv_string()
                print("Parte {} {} subida con exito al servidor: {}".format(hashInt, listaHashes[numParte], serverAddr))
            elif respuestaServidor[0]=="NuevaConexion":
                serverAddr = respuestaServidor[1]
                server = context.socket(zmq.REQ)
                server.connect("tcp://{}".format(serverAddr))
                server.send_string(message+" "+listaHashes[-1]+"-"+filename+" "+str(numParte)+" "+str(hashInt))
                respuestaServidor=server.recv_string() #El servidor responde si es el responsable, o si necesita esttablecer otra conexion.
                respuestaServidor=respuestaServidor.split(" ")
                while noEncuentreServidorResponsable:
                    print(respuestaServidor)
                    if respuestaServidor[0]=="Responsable":
                        server.send_multipart([listaHashes[numParte].encode("utf-8"), partes[numParte]]) #Envio en name del file en hash y el contenido.
                        server.recv_string()
                        print("Parte {} {} subida con exito al servidor: {}".format(hashInt, listaHashes[numParte], serverAddr))
                        noEncuentreServidorResponsable=False
                    elif respuestaServidor[0]=="NuevaConexion":
                        serverAddr = respuestaServidor[1]
                        server = context.socket(zmq.REQ)
                        server.connect("tcp://{}".format(serverAddr))
                        server.send_string(message+" "+listaHashes[-1]+"-"+filename+" "+str(numParte)+" "+str(hashInt))
                        respuestaServidor=server.recv_string() #El servidor responde si es el responsable, o si necesita esttablecer otra conexion.
                        respuestaServidor=respuestaServidor.split(" ")
                        print(respuestaServidor)
        print("Todas las partes fueron subidas con exito!!")

    if message == "download":
        todoElAnilloRecorrido=False
        serverAddrSucesor=""
        while not(todoElAnilloRecorrido):
            print(serverAddrSucesor)
            print(serverAddrOriginal)
            if serverAddrSucesor==serverAddrOriginal:
                print("Ya descargue todas las partes")
                todoElAnilloRecorrido=True
            else:
                server.send_string(message+" "+filename)
                respuestaServidor=server.recv_json()
                if respuestaServidor["Respuesta"]=="Tengo partes del archivo":
                    enlistarNombrePartes(respuestaServidor["NombrePartes"])
                    server.send_string("Ya puede mandar el contenido de las partes")
                    print("Empezare a recibir las partes")
                    for i in range(len(respuestaServidor["NombrePartes"])):
                        partesDelServidor=server.recv_multipart() #voy a recibir las partes que el servidor tenga de mi archivo con el name.
                        guardarParte(partesDelServidor[0].decode("utf-8"), partesDelServidor[1]) #mando el nombre de la parte y el contenido.
                        server.send_string("ok")
                    serverAddrSucesor=server.recv_string()
                    server = context.socket(zmq.REQ)
                    server.connect("tcp://{}".format(serverAddrSucesor))
                elif respuestaServidor["Respuesta"]=="No tengo partes del archivo":
                    server.send_string("Gracias")
                    server.recv_string()
                    serverAddrSucesor=respuestaServidor["PuertoSucesor"]
                    server = context.socket(zmq.REQ)
                    server.connect("tcp://{}".format(serverAddrSucesor))
        #print(listaNombrePartes)
        juntarPartes(filename+"-Descargado")
        print("El archivo fue descargado con exito.!!!!")

if __name__ == "__main__":
    main()
