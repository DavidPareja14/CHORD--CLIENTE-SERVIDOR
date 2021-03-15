#!/bin/bash

ubicacionActual=$(pwd)

#Esta instruccion es para que pueda borrar todo excepto los archivos especific
shopt -s extglob 

#Este for es para eliminar todas las partes que estén en las carpetas de los nodos
#No se borrará node.py, luego, como el archivo config.json es modificado al hacer
#las partes, necesito borrarlo también y copiar el que está intacto
for numeroNodo in 4 18 44 57
do
	cd $ubicacionActual/nodo$numeroNodo
	rm -v !("node.py")
	cp ../config.json .
done

shopt -u extglob
