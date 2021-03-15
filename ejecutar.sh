#!/bin/bash

ubicacionActual=`pwd`
listaDeIdProcesos=()

#Cada nodo será activado con el número que le corresponde, este número es importante, ya que se usará en
#el archivo config.json
#Por otra parte, con $! obtengo el process id de cada ejecución, con & mando el proceso a background y con
#${#lista[*]} obtengo la cantidad de elementos del array
#Es importante obtener el id de cada proceso segun node.py porque estos utilizan puertos del sistema y si
#vuelvo a ejecutar este script y no he terminado esos procesos, los puertos no los puedo volver a usar.

mkdir nodo4
cp node.py nodo4
cp config.json nodo4

mkdir nodo18
cp node.py nodo18
cp config.json nodo18

mkdir nodo44
cp node.py nodo44
cp config.json nodo44

mkdir nodo57
cp node.py nodo57
cp config.json nodo57

mkdir cliente1
cp client.py cliente1


xterm -hold -e python $ubicacionActual/nodo4/node.py 4 nodo4 &
listaDeIdProcesos[${#listaDeIdProcesos[*]}]=$!
xterm -hold -e python $ubicacionActual/nodo18/node.py 18 nodo18 & 
listaDeIdProcesos[${#listaDeIdProcesos[*]}]=$!
xterm -hold -e python $ubicacionActual/nodo44/node.py 44 nodo44 &
listaDeIdProcesos[${#listaDeIdProcesos[*]}]=$!
xterm -hold -e python $ubicacionActual/nodo57/node.py 57 nodo57 &
listaDeIdProcesos[${#listaDeIdProcesos[*]}]=$!


subirArchivo () {
	python $ubicacionActual/cliente1/client.py upload $1 localhost:6668 cliente1
}

bajarArchivo () {
	python $ubicacionActual/cliente1/client.py download $1 localhost:6668 cliente1
}

while :
do
	echo -e "----------------------MENU-------------------------\n"
	echo "1. Subir archivo"
	echo "2. Descargar archivo"
	echo -e "3. Salir\n"
	read -n1 -p "Ingrese la acción[1-3] que desee: " opcion

	case $opcion in
		1) echo -e "\n"
		   read -p "Ingrese el nombre del archivo que desea subir: " archivo
		   subirArchivo $archivo
		   ;;
		2) echo -e "\n"
		   read -p "Ingrese el nombre del archivo que desea descargar: " archivo
		   bajarArchivo $archivo
		   ;;
		3) clear
		   for idProceso in ${listaDeIdProcesos[*]}
		   do
		   		kill -9 $idProceso 2>/dev/null
		   done

		   echo -e "\nHASTA LA PROXIMA!!!"
		   exit 0
		   ;;
		*) echo -e "\nOpción no encontrada"
	esac
done
