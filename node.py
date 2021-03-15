"""
Desarrollado por David Pareja Arango
"""

import sys

import hashlib
import string
import random
import os
import math
import zmq
import json

partesDelArchivoRequerido=[] #hace parte del descargar un archivo.

class Node:
    def __init__(self,id,predId,bits):
        self.identifier = id
        self.predecessor = predId
        self.bits = bits
        self.sucesorMenorQueYo = False #Es para cumplir con el caso 3 (ver cuaderno)
    def getId(self):
        return self.identifier
    #def interval(self):
    #    if self.predecessor > self.identifier:
    #        return "[" + str(self.predecessor + 1) + "," + str(2**self.bits - 1) + "] U [0," + str(self.identifier) + "]"
    #    else:
    #        return "(" + str(self.predecessor) + "," + str(self.identifier) + "]"
    def responsible(self, hash):
        if self.predecessor > self.identifier:
            # First node in the ring
            if hash > self.predecessor and hash < 2**self.bits:
                return ["True",[[self.predecessor+1,2**self.bits],[0, self.identifier]]]
            if hash >= 0 and hash <= self.identifier:
                return ["True",[[self.predecessor+1,2**self.bits],[0, self.identifier]]]
            return ["False"]
        else:
            # Any other node in the ring
            if hash > self.predecessor and hash <= self.identifier:
                return ["True",[[self.predecessor+1,self.identifier]]]
            return ["False"]


def fingerTable(identificador, numeroDeBits, successor, predecessor, succAddr, context):
	for i in range(numeroDeBits):
		soyResponsable=False
		responsible=(identificador+2**i)%2**numeroDeBits
		successor.send_json({"option": "Responsabilidad", "valor": responsible})
		esResponsable=successor.recv_string()
		esResponsable=esResponsable.split(" ")
		nodoFinger=None
		if esResponsable[0]=="si":
			try:
				with open(sys.argv[2] + "/fingerTable"+str(identificador)+".json") as nodoApuntar: 
					nodoFinger=json.load(nodoApuntar)
					nodoApuntar.close()
					if len(esResponsable)==7:
						datosIdentificadorEnJsonFile=[esResponsable[2],[[esResponsable[3],esResponsable[4]],[esResponsable[5],esResponsable[6]]]]
						nodoFinger[esResponsable[1]]=datosIdentificadorEnJsonFile
					else:
						datosIdentificadorEnJsonFile=[esResponsable[2],[[esResponsable[3],esResponsable[4]]]]
						nodoFinger[esResponsable[1]]=datosIdentificadorEnJsonFile
					nodos = open(sys.argv[2] + "/fingerTable"+str(identificador)+".json", "w") #abro el dicc con los apuntadores del nodo.
					json.dump(nodoFinger, nodos)
					nodos.close()
			except:
				nodos = open(sys.argv[2] + "/fingerTable"+str(identificador)+".json", "w") #creo el dicc con los apuntadores del nodo.
				json.dump({esResponsable[1]:esResponsable[2]}, nodos)
				nodos.close()
		else:
			#Puede que un valor que yo como nodo calcule para encontrar su responsable, ese responsable sea el mismo,
			#por lo tanto no es necesario conectarme a mi mismo, para eso uso el condicional.
			if esResponsable[1]==predecessor: 
				break
			successor = context.socket(zmq.REQ)
			successor.connect("tcp://{}".format(esResponsable[1]))
			#Practicamente repito todo el codigo, para en caso de que yo no sea el responsble, seguir buscando
			#el responable del valor en especifico.

			while not(soyResponsable):
				print(responsible)
				successor.send_json({"option": "Responsabilidad", "valor": responsible})
				esResponsable=successor.recv_string()
				esResponsable=esResponsable.split(" ")
				
				nodoFinger=None
				if esResponsable[0]=="si":
					if esResponsable[1]==predecessor:
						break
					soyResponsable=True
					with open(sys.argv[2] + "/fingerTable"+str(identificador)+".json") as nodoApuntar: 
						nodoFinger=json.load(nodoApuntar)
						nodoApuntar.close()
						if len(esResponsable)==7:
							datosIdentificadorEnJsonFile=[esResponsable[2],[[esResponsable[3],esResponsable[4]],[esResponsable[5],esResponsable[6]]]]
							nodoFinger[esResponsable[1]]=datosIdentificadorEnJsonFile
						else:
							datosIdentificadorEnJsonFile=[esResponsable[2],[[esResponsable[3],esResponsable[4]]]]
							nodoFinger[esResponsable[1]]=datosIdentificadorEnJsonFile
						nodos = open(sys.argv[2] + "/fingerTable"+str(identificador)+".json", "w") #abro el dicc con los apuntadores del nodo.
						json.dump(nodoFinger, nodos)
						nodos.close()
				else:
					print(esResponsable[1],predecessor)
					if esResponsable[1]==predecessor:
						break
					successor = context.socket(zmq.REQ)
					successor.connect("tcp://{}".format(esResponsable[1]))

	#Busco organiczar la finger table ascendentemente, para que me quede mas facil en caso tal que en mi finger table no este
	#un nodo que pueda guardar el hash, yo pueda decirle cual es el mas cercano que tengo.
	nodos = open(sys.argv[2] + "/fingerTable"+str(identificador)+".json")
	nodoFinger=json.load(nodos)
	nodos.close()
	llaves=[]
	inicial=0
	valor=0

	for llave in nodoFinger:
		llaves.append(int(llave))

	for i in range(len(llaves)):
		for j in range(len(llaves)):
			if llaves[inicial]>llaves[j]:
				valor=llaves[inicial]
				llaves[inicial]=llaves[j]
				llaves[j]=valor
			inicial=j
		inicial=0
	print(llaves)

	fingerTableOrdenada={}
	for i in range(len(llaves)):
		for clave in nodoFinger:
			if llaves[i]==int(clave):
				fingerTableOrdenada[clave]=nodoFinger[clave]
				break

	#guardo el archivo con la table finger ordenada.
	nodos = open(sys.argv[2] + "/fingerTable"+str(identificador)+".json", "w") #abro el dicc con los apuntadores del nodo.
	json.dump(fingerTableOrdenada, nodos)
	nodos.close()
	successor = context.socket(zmq.REQ)
	successor.connect("tcp://{}".format(succAddr))
	print(succAddr)

#------------------------------------------SIGUE EL CODIGO PARA EL CLIENTE.--------------------------------------------
#me recibe el hash del archivo completo y la parte a guardar, entonces a cada hash del archivo completo le asocia las resp
#ectivas partes del archivo que se van a guardar.
def partesArchivo(hashArchivo, hashParte):
	lista=[]
	try:
		with open(sys.argv[2] + "/partesArchivo.json") as partes:
			estaHashArchivo=False 
			guardarParte=json.load(partes)
			partes.close()
		for hashGeneral in guardarParte:
			if hashArchivo==hashGeneral:
				lista=guardarParte[hashArchivo]
				lista.append(hashParte)
				guardarParte[hashArchivo]=lista
				estaHashArchivo=True
				break
		if estaHashArchivo:
			pass
		else:
			guardarParte[hashArchivo]=[hashParte]
		nodos = open(sys.argv[2] + "/partesArchivo.json", "w") #abro el dicc con los apuntadores del nodo.
		json.dump(guardarParte, nodos)
		nodos.close()
	except:
		nodos = open(sys.argv[2] + "/partesArchivo.json", "w") #creo el dicc con los apuntadores del nodo.
		json.dump({hashArchivo:[hashParte]}, nodos)
		nodos.close()

def uploadFile(filename, content):
	with open(sys.argv[2] + "/" + filename, "wb") as f:
		f.write(content)

#Me va a retornar el posible puerto del nodo que pueda contener el hash del archivo
def posibleNodoResponsable(hashParte, identificador, idSucesor):
	nodoCercanoAResponsable=""
	longitudFT=0
	with open(sys.argv[2] + "/fingerTable"+str(identificador)+".json") as nodoApuntar: 
		nodoFinger=json.load(nodoApuntar)
		nodoApuntar.close()

	for pos,identifier in enumerate(nodoFinger):
		if pos==len(nodoFinger)-1 and hashParte>int(identifier): #Es para el caso 3(ver cuaderno)
			if idSucesor: #significa que le id de mi sucesor es menor al mio.
				for identifier in nodoFinger:
					return nodoFinger[identifier][0] #Retorno el puerto del id menor de la FT.
			else:
				nodoCercanoAResponsable="Es algun nodo despues al mas grande de la FT"
				break
		if hashParte>int(identifier): #Es para el caso 2, (ver cuaderno)
			nodoCercanoAResponsable=nodoFinger[identifier][0] #voy a obtener el puerto del posible nodo cercano al responsable.
		else:
			if len(nodoFinger[identifier][1])==1: #significa que no es el nodo con id menor, ya que este tiene dos intervalos.
				if hashParte>=int(nodoFinger[identifier][1][0][0]) and hashParte<=int(nodoFinger[identifier][1][0][1]):
					nodoCercanoAResponsable=nodoFinger[identifier][0] #Este es el nodo responsble
					return nodoCercanoAResponsable
			elif (hashParte>=int(nodoFinger[identifier][1][0][0]) and hashParte<=int(nodoFinger[identifier][1][0][1])) or (hashParte>=int(nodoFinger[identifier][1][1][0]) and hashParte<=int(nodoFinger[identifier][1][1][1])):
				nodoCercanoAResponsable=nodoFinger[identifier][0] #Este es el nodo responsble
				return nodoCercanoAResponsable
			if pos==0: #Es con respecto al caso 1 (ver cuaderno.)
				nodoCercanoAResponsable="Es un nodo anterior al mas pequeno de la FT"
				break
			return nodoCercanoAResponsable

	if nodoCercanoAResponsable=="Es un nodo anterior al mas pequeno de la FT": #caso 1
		#El for solo es para obtener el ultimo id de la finger table.
		for ultimoId in nodoFinger:
			pass 
		nodoCercanoAResponsable=nodoFinger[ultimoId][0]
		return nodoCercanoAResponsable
	if nodoCercanoAResponsable=="Es algun nodo despues al mas grande de la FT": #caso 3
		#El for solo es para obtener el ultimo id de la finger table.
		for ultimoId in nodoFinger:
			pass 
		nodoCercanoAResponsable=nodoFinger[ultimoId][0]
		return nodoCercanoAResponsable

"""
					ADVERTENCIA
					Esta funcion ha sido modificada mas de un anio despues de haber presentado el trabajo,
					la modificacion consiste en que al obtener la clave del diccionario guardarParte, la
					clave seria hashGeral en la siguiente funcion, esto tiene el nombre del archivo al
					igual que con su hash, es decir, el hash del archivo subido, completo.
					el hash y nombre se separan con -, entonces en la segunda posicion esta el nombre real
					del archivo, por eso lo parto y con [1] obtengo el nombre.
					Esto no esta del todo bien, ya que se podrian subir dos o mas archios con el mismo nombre,
					pero ser archivos completamente diferentes, entonces, ¿Como obtengo el archivo que el
					cliente desea?.
					Al presentar el trabajo, el problema de esta funcion no existia, entonces supongo que
					esta es una version desactualizada y el original lo he perdido.
					Para solucionar la repecion de nombres o contenido, se puede hacer sencillo:
					Si dos archivos son iguales, con el mismo contenido, bastaria obtener cada llave
					y comparar su hash con el nuevo archivo que se quiera subir, si ninguno coincide,
					entonces significa que es un archivo diferente, pero ahora se debe comparar con el
					nombre, si el nombre ya existe en mi "base de datos" de archivos, entonces no lo acepto.
					Pero lo anterior lo dejare para otro momento o tal vez no.
"""
def buscarArchivo(filename, puertoSucesor):
	try:
		with open(sys.argv[2] + "/partesArchivo.json") as partes:
			guardarParte=json.load(partes)
			partes.close()
		for pos,hashGeneral in enumerate(guardarParte):
			nombreArchivo = hashGeneral.split("-")[1]
			if filename==nombreArchivo:
				return {"Respuesta": "Tengo partes del archivo", "NombrePartes": guardarParte[hashGeneral], "Parts":guardarParte[hashGeneral]}
			if pos==len(guardarParte)-1:
				return {"Respuesta": "No tengo partes del archivo", "PuertoSucesor": puertoSucesor}
	except:
		return {"Respuesta": "No tengo partes del archivo", "PuertoSucesor": puertoSucesor}

def descargarParte(parte):
	with open(sys.argv[2] + "/" + parte, 'rb') as f:
		return f.read()

def puertoSucesorCliente(puertoSucesor):
	with open(sys.argv[2] + "/config.json") as diccionaro: 
		configuracion=json.load(diccionaro)
		diccionaro.close()

	for identifiero in configuracion:
		print(identifiero)
		if configuracion[identifiero]=="bits":
			pass
		elif configuracion[identifiero]["predPort"]==puertoSucesor:
			print(configuracion[identifiero]["clients"])
			return configuracion[identifiero]["clients"] #Retorno el puerto del id menor de la FT.

def main():
	# python node.py id carpeta
	if len(sys.argv) != 3:
	    print("Error!!!")
	    exit()

	context = zmq.Context()
	id = int(sys.argv[1])

	with open(sys.argv[2] + "/config.json") as nodosId: 
		infoNodos=json.load(nodosId)
	# Socket to listen predecessor's messages
	predAddr = infoNodos[sys.argv[1]]["predPort"]
	predecessor = context.socket(zmq.REP)
	predecessor.bind("tcp://*:{}".format(predAddr))

	# Socket to communicate with the successor
	succAddr = infoNodos[sys.argv[1]]["succesor"]
	succAddrOriginal=infoNodos[sys.argv[1]]["succesor"].split(":")[1] #solo le paso el puerto
	successor = context.socket(zmq.REQ)
	successor.connect("tcp://{}".format(succAddr))

	# Socket to listen clients's messages
	clientAddr = infoNodos[sys.argv[1]]["clients"]
	client = context.socket(zmq.REP)
	client.bind("tcp://*:{}".format(infoNodos[sys.argv[1]]["clients"].split(":")[1]))

	#folder = infoNodos[sys.argv[1]]["folder"]
	bits = infoNodos["bits"]

	#------------------------------------ADVERTENCIA----------------------------------
	#Lo que se hace a continuacion no es debido, al campo bits que tiene un numero asociado, lo cambio luego de ser asignado
	#por un diccionario que me contenga predPort, esto es porque cuando necesite descargar un archivo, voy a tener que encontrar
	#el puerto del cliente de mi nodo sucesor, para pasarlo al cliente en caso de que ya no tenga mas partes para mandar o que 
	#no tenga partes, para recorrer ese diccionario al parecer necesito tener en todas las llaves predPort (no tengo internet)
	infoNodos["bits"]={"predPort":str(bits)}
	nodos = open(sys.argv[2] + "/config.json", "w") #abro el dicc con los apuntadores del nodo.
	json.dump(infoNodos, nodos)
	nodos.close()

	poller = zmq.Poller()
	poller.register(predecessor, zmq.POLLIN)
	poller.register(client, zmq.POLLIN)

	successor.send_json({"option": "registerPredecessor", "id": id})

	print("Ready! {}: predecessor {} successor {} client {}".format(id,predAddr,succAddr,clientAddr))
	n = None
	controlSendPredecessor=0

	while True:
		socks = dict(poller.poll())
		if predecessor in socks:
			print("Message from predecessor!!")
			m = predecessor.recv_json()
			print(m)			
			if m["option"] == "registerPredecessor":
			    print("New predecessor!!! {}".format(m["id"]))
			    n = Node(id, int(m["id"]), bits)
			    #predecessor.send_string("ok")
			    #print(n.interval())
				#Significa que el anillo se ha completado, entoces todos los nodos pueden calcular la finger table.
			    if m["id"]>id:
			    	#_=input("Todos los nodos estan listos, de enter para empezar")
			    	controlSendPredecessor=1
			    	predecessor.send_string("soyMayorAlSucesor")#caso 3 (ver cuaderno)
			    	successor.recv_string()
			    	_=input("presione enter para Empezar con todo: ")
			    	successor.send_json({"option": "Empezar"})#predMQY caso 3 nodo mas cercano
			    	
			elif m["option"] == "Empezar":
				#finaliza el mensaje empesar, ya todos empezaron.
				if n.identifier<n.predecessor:
					print("Todos ya empezaron") 
					successor.recv_string()
					print("hola kjhhk")
					fingerTable(n.identifier, n.bits, successor, predAddr, succAddr, context)
					print("Empece a calcular mi finger table")
				else:
					respuesta=successor.recv_string()	
					if respuesta=="soyMayorAlSucesor":
						n.sucesorMenorQueYo=True				
					print("hola kjhhk")
					fingerTable(n.identifier, n.bits, successor, predAddr, succAddr, context)
					successor.send_json({"option": "Empezar"})
					#successor.recv_string()	
					print("Empece a calcular mi finger table")
			elif m["option"] == "Responsabilidad":
				controlSendPredecessor=1
				soyResponsable=n.responsible(m["valor"])
				if soyResponsable[0]=="True":
					if len(soyResponsable[1])==2:
						predecessor.send_string("si "+str(n.identifier)+" "+clientAddr+" "+str(soyResponsable[1][0][0])+" "+str(soyResponsable[1][0][1])+" "+str(soyResponsable[1][1][0])+" "+str(soyResponsable[1][1][1]))
					else:
						predecessor.send_string("si "+str(n.identifier)+" "+clientAddr+" "+str(soyResponsable[1][0][0])+" "+str(soyResponsable[1][0][1]))
				else:
					predecessor.send_string("no "+succAddr)

			if controlSendPredecessor==0:
				predecessor.send_string("ok")
			else:
				controlSendPredecessor=0
			
		if client in socks:
		    print("Message from client!!")
		    men = client.recv_string() #Debo recibir la operacion, el hashArchivo, numero de la parte y el hash de la parte.
		    datosCliente=men.split(" ")
		    print(men)
		    if datosCliente[0] == "upload":
		    	numParteYParte=[int(datosCliente[2])]
		    	veamosSiEsResponsable=n.responsible(int(datosCliente[3]))
		    	print(veamosSiEsResponsable)
		    	if veamosSiEsResponsable[0]=="True":
		    		client.send_string("Responsable ")
		    		parte = client.recv_multipart() #voy a recibir la parte del archivo como tal.
		    		numParteYParte.append(parte[0].decode("utf-8"))
		    		partesArchivo(datosCliente[1], numParteYParte)
		    		print("Estoy guardando la parte")
		    		uploadFile(parte[0].decode("utf-8"), parte[1]) #recibo en nomb en hash del file y la parte.
		    		client.send_string("ok")
		    	else:
		    		puerto=posibleNodoResponsable(int(datosCliente[3]), n.identifier, n.sucesorMenorQueYo)
		    		print("si no, es responsable: "+puerto)
		    		client.send_string("NuevaConexion "+puerto)
		    elif datosCliente[0] == "download":
		    	print("succAddrO "+succAddrOriginal)
		    	puertoSucesorDelCliente=puertoSucesorCliente(succAddrOriginal)
		    	respuestaParaCliente=buscarArchivo(datosCliente[1], puertoSucesorDelCliente)
		    	client.send_json(respuestaParaCliente)
		    	respuestaCliente=client.recv_string()
		    	if respuestaCliente=="Ya puede mandar el contenido de las partes":
		    		print("Estoy mandando el contenido de las partes.")
		    		partesDelArchivoRequerido=respuestaParaCliente["Parts"]
		    		print(partesDelArchivoRequerido)
		    		for parte in partesDelArchivoRequerido:
		    			contenidoParte=descargarParte(parte[1])
		    			client.send_multipart([parte[1].encode("utf-8"), contenidoParte])
		    			client.recv_string()
		    		client.send_string(puertoSucesorDelCliente)
		    		print("Termine de mandar las partes")
		    	elif respuestaCliente=="Gracias":
		    		client.send_string("ok")



if __name__ == "__main__":
    main()
 