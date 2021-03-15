# CHORD -> Cliente-Servidor
Este proyecto le permite a una computadora cliente subir y bajar archivos en un sistema conformado por varios nodos los cuales guardarán partes de los archivos subidos para luego, poder efectuar descargas.

## Especificación

Este trabajo implementa el algoritmo y protocolo CHORD, el cual funciona sobre una red descentralizada p2p, en
donde cada nodo que la conforme tendrá un nodo antecesor y predecesor, formando así un anillo entre los nodos de
la red. Un cliente, al conectarse a cualquier nodo del anillo puede descargar y subir archivos. Este anillo es estático,
es decir, por el momento se crea con una cantidad fija de nodos o servidores, por lo tanto, si se desea agregar un
nuevo servidor, no es posible.

Para que funcione CHORD, el programa debe ejecutarse en orden, es decir, en este caso trabajo con 4 nodos,
el nodo4, nodo18, nodo44 y nodo57, entonces se ejecuta en este orden en un terminal por nodo así:

Terminal 1:
python nodo4 4

Terminal 2:
python nodo4 18

Terminal 3:
python nodo44 44

Terminal 4:
python nodo4 57

Lo anterior se hace de manera automática, no se debe preocupar por ello.


## Consideraciones

* Este programa lo he probado en ubuntu, ha funcionado completamente. 
* Hay que tener en cuenta que he utilizado python 3 con anaconda y que se debe instalar la librería ZMQ para
poder manejar el tema de comunicación en red. 
* Lo que sigue es en caso de tener varias computadoras:
Se debe cambiar el archivo config.json con las direcciones ip y puertos de cada computadora. El archivo config.json
contine la configuración para probar el trabajo de forma local.
* El programa se puede probar en el SO Windows, pero se debe descargar una terminal
que soporte los comandos de Linux.
* Para que el trabajo funcione con varias computadoras, se ha tenido en cuenta muchos factores, como por ejemplo, particionar los archivos de tal manera que cada parte fuera identificada de forma única y almacenada en una computadora (servidor), el paso de archivos (cada archivo particionado) se hace con un tamaño tal que compense el envío por la red, el tamaño de cada parte fue de 10MB, esto permite que el sistema no colapse, ya que 10MB pueden ser cargados fácilmente en memoria principal y los núcleos de cada computadora los pueden procesar rápidamente.

## Advertencia

Hay que poner bastante atención con el archivo eliminarPartesDeLosArchivosSubidos.sh
porque si se intenta eliminar una carpeta que no exista, se corre el riesgo de que se
eliminen todos los archivos incluidos en la carpeta actual. Solo imaginen que este archivo
se ejecute desde el escritorio y que esté lleno de archivos importantes, se pueden perder
todos. USAR CON MUCHO CUIDADO. 
Por lo anterior, recomiendo que si se desea ejecutar ese archivo, el proyecto que he creado
esté aislado en una carpeta (aunque creo que esto último podría sobrar).

## Para ejecutar el programa

Primero que todo, se debe empezar por abrir un terminal y correr el archivo ejecutar.sh

> ./ejecutar.sh o bash ejecutar.sh

En la carpeta desde donde se ejecute este archivo, se crearan otras 5 carpetas, una carpeta
simulará ser un cliente, las otras 4 serán servidores que guarden las partes de cada archivo
que se suba a este sistema.

Se abrirán 4 ventanas de terminal, cada una simula ser un servidor. Hay que tener en cuenta
que unas ventanas pueden tapar a otras, se debe verificar que sean 4 ventanas de terminal.
Luego, se debe buscar la ventana que indique dar enter para poder continuar y calcular las
finger tables, una vez hecho esto, ya se puede utilizar el sistema para subir o bajar archivos.

Desde el terminal que se corra ejecutar.sh, esa ventana hará de cliente, en este caso solo he
creado un cliente, por lo tanto, dejo esa terminal para que me muestre información del cliente
y también que muestre el menú de opciones de la aplicación.

En la carpeta cliente se deben poner todos los archivos que se deseen subir, en esta carpeta
también se descargarán los archivos que el usuario indique.

Una vez tenga todo lo anterior, en la terminal del cliente o mejor dicho, desde donde se corra
ejecutar.sh ya se puede elegir una opcion del menú de opciones, debe ser un número. Si se desea
subir un archivo, debe ser un archivo que esté en la carpeta cliente1, entonces se debe introducir
el nombre del archivo en el sistema. También, se debe tener en cuenta, que si se intenta descargar
un archivo que no exista en los nodos o servidores, aparecerá como descargandose, pero en realidad,
no se efectúa descarga alguna.
