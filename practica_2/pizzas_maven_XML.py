import pandas as pd
import sys
import signal
from tabulate import tabulate
import datetime as dt
import re
import xml.etree.ElementTree as ET
from xml.dom import minidom


def extract():

    # Extrae los datos de los csv que contiene la información de las pizzas, ingredientes, pedidos y detalles de pedidos ya limpios.
    # Añadimos además los dos dataframes que nos dan sucios: pedidos y detalles_pedidos que son los que usaremos para hacer el informe de los datos
    detalles_pedidos_limpio = pd.read_csv("order_details_limpio.csv", sep = ";", encoding = "UTF-8")
    detalles_pedidos = pd.read_csv("order_details.csv", sep = ";", encoding = "UTF-8")
    pizzas = pd.read_csv("pizzas.csv", sep = ",", encoding = "UTF-8")
    ingredientes = pd.read_csv("pizza_types.csv", sep = ",", encoding = "LATIN-1")
    pedidos_limpio= pd.read_csv("orders_limpio.csv",sep = ';', encoding="LATIN-1")
    pedidos = pd.read_csv("orders.csv",sep = ';', encoding="LATIN-1")
    return detalles_pedidos_limpio, pizzas, ingredientes, pedidos_limpio, detalles_pedidos, pedidos

def transform(detalles_pedidos_limpio, pizzas, ingredientes, pedidos_limpio, detalles_pedidos, pedidos):

    # Recibe como parámetros los 6 dataframes, pedidos, pizzas, ingredientes, detalles de pedidos, pedidos limpios y detalles de pedidos limpios.
    # Devuelve un diccionario con los ingredientes a comprar semanalmente.

    #Ahora, vamos a generar el informe de cada dataframe y lo guardaremos en un csv
    csvs = ["order_details.csv", "pizzas.csv", "pizza_types.csv", "orders.csv"]
    dataframes = [detalles_pedidos, pizzas, ingredientes, pedidos]
    
    for i in range(len(dataframes)):

        print('Informe del csv',csvs[i],':\n')
        informe = dataframes[i].isna().sum().to_frame().rename(columns={0: 'NaNs'})
        informe['Nulls'] = dataframes[i].isnull().sum()
        informe['Porcentaje NaNs'] = informe['NaNs'] / dataframes[i].shape[0] * 100
        informe['Porcentaje Nulls'] = informe['Nulls'] / dataframes[i].shape[0] * 100
        informe['Data Type'] = dataframes[i].dtypes
        print(tabulate(informe, headers='keys', tablefmt='psql'))
        print('\n')
        nombre_fout = 'informe_'+csvs[i][:-4]+'.csv'
        informe.to_csv(nombre_fout) 

    # Cogemos el número de veces que se ha pedido cada pizza en un año.
    # Ahora lo dividimos por 365 (tomamos parte entera) y multiplicamos por 7 para obtener el número de pizzas que se pide cada semana
    # A eso le sumamos 1 porque mejor que sobren pizzas que que falten

    n_sem_pizzas=dict()
    d_ingr = dict()

    for p in pizzas['pizza_id']:
        n_sem_pizzas[p] = int(detalles_pedidos_limpio[detalles_pedidos_limpio['pizza_id'] == p].shape[0] / 365 * 7) + 1

    # Cogemos los ingredientes de cada pizza y los pasamos a una lista
    # A continuación, cogemos cada ingrediente de la lista y lo añadimos al diccionario de ingredientes
    # Inicializamos el valor de cada ingrediente a 0.
    
    for ingrediente_bruto in ingredientes['ingredients']:
        lista = ingrediente_bruto.split(', ')
        for ingrediente in lista:
            d_ingr[ingrediente] = 0
    
    # Ahora, para cada pizza, cogemos los ingredientes que tiene y los multiplicamos por el número de veces que se pide esa pizza en una semana

    for pizza_bruto in n_sem_pizzas.keys():
        # Ahora procesamos el nombre de cada pizza para sacar por separado el nombre y el tamaño.
        # El nombre de la pizza está entre los dos primeros guiones bajos
        # El tamaño de la pizza está entre el segundo y el tercer guión bajo
        # Cogemos el tamaño de la pizza y lo convertimos a un número según la lista Multiplicador
        pizza = pizza_bruto.split('_')
        tam = pizza.pop(-1)
        pizza = '_'.join(pizza)
        multi = Multiplicador[Tamaño.index(tam)]
        # Para cada pizza saco sus ingredientes y los paso a una lista.
        # Busco cada ingrediente en el diccionario de ingredientes y le sumo el resultado de multiplicar el número de pizzas de 
        # ese tipo que se han pedido en una semana
        # por el multiplicador que le corresponde según su tamaño

        # Usamos map para convertir los ingredientes en una lista
        ingredientes_pizza = ingredientes[ingredientes['pizza_type_id'] == pizza]['ingredients'].item()
        lista = ingredientes_pizza.split(', ')
        list(map(lambda x: d_ingr.update({x: d_ingr[x] + n_sem_pizzas[pizza_bruto]*multi}), lista))
    
    return d_ingr

def load(d_ingr):
    
        # Recibe como parámetro el diccionario de ingredientes a comprar semanalmente.
        # Crea un dataframe con los ingredientes y sus cantidades y lo guarda en un csv.
        # Muestra por pantalla el dataframe.
   
        compra_semana = pd.DataFrame(d_ingr.items(), columns=['Ingrediente', 'Unidades'])
        compra_semana.to_csv('compra_semana.csv', index=False)
        print('El dataframe con la cantidad de ingredientes a comprar semanalmente es:\n')
        # Imprimimos el dataframe de forma más bonita
        print(tabulate(compra_semana, headers='keys', tablefmt='psql'))



def handler_signal(signal, frame):
    print("\n [!] Se ha recibido la señal de interrupción. Finalizando ejecución...")
    sys.exit(1)

# Ctrl + C
signal.signal(signal.SIGINT, handler_signal)


Multiplicador = [1, 2, 3, 4, 5] # Esta lista da un peso a cada pizza según su tamaño
Tamaño = ['s','m','l','xl', 'xxl'] # Esta lista contiene los tamaños de las pizzas


def limpiar_archivos(archivo):
    #Tenemos 4 casos:
    #1. Línea vacía (la eliminamos).
    #2. Línea con espacios en blanco en vez de ";".
    #3. Línea con espacios en blanco en vez de "_".
    #4. Línea en la que el nombre de la pizza está mal escrito.
    #Para diferenciar el caso 2 del 3, comprobamos si detrás de ese espacio en blanco hay un número o una letra.
    #Si hay un número, es el caso 2, si hay una letra, es el caso 3.
    
    nombre_archivo_limpio = archivo[:-4] + '_limpio.csv'
    with open(archivo, 'r') as fin:
        lineas = fin.readlines()
        with open(nombre_archivo_limpio, 'w') as fout:

            # Si la línea tiene un espacio en blanco y detrás hay un número, es el caso 2 y lo cambiamos por ";"
            lineas = [linea.replace(' ', ';') if ' ' in linea and linea[linea.index(' ')+1].isdigit() else linea for linea in lineas]
             # Si la línea tiene un espacio en blanco y detrás hay una letra, es el caso 3 y lo cambiamos por "_"
            lineas = [linea.replace(' ', '_') if ' ' in linea and linea[linea.index(' ')+1].isalpha() else linea for linea in lineas]
            # Si la línea tiene "-" lo cambiamos por "_"
            lineas = [linea.replace('-', '_') if '-' in linea else linea for linea in lineas]
            # Si dicha línea no tiene 2 ";" seguidos ni hay un salto de línea después de l ";" la escribimos en el archivo.
            lineas = [linea for linea in lineas if ';;' not in linea and ';\n' not in linea]
            fout.writelines(lineas)

    dataframe=pd.read_csv(nombre_archivo_limpio,sep=";")

    #En la columna quantity, cambio los numeros escritos en letra por números
    num_letra = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
    dataframe['quantity'] = dataframe['quantity'].replace(num_letra, regex=True)

    #En la columna pizza_id, cambio los caracteres como @ por a, 3 por e, etc.
    caracteres = {"@": "a", "3": "e", "4": "f", "5": "s", "6": "g", "7": "t", "8": "b", "9": "g", "0": "o"}
    dataframe['pizza_id'] = dataframe['pizza_id'].replace(caracteres, regex=True)

    #guardo el archivo
    dataframe.to_csv(nombre_archivo_limpio, sep=';', index=False)

    return nombre_archivo_limpio

def limpiar_orders(archivo):
    #Hago una función separada para limpiar el archivo orders.csv
    # Hay 3 cosas que hay que arreglar:
    #1. Línea con datos incompletos (la eliminamos).
    #2. La hora de la orden está mal escrita (la corregimos) y luego la eliminamos.
    #3. La fecha de la orden está mal formateada (la corregimos).

    
    nombre_archivo_limpio = archivo[:-4] + '_limpio.csv'
    with open(archivo, 'r') as fin:
        lineas = fin.readlines()
        with open(nombre_archivo_limpio, 'w') as fout:
            #Si dicha línea no tiene 2 ";" seguidos ni hay un salto de línea después de l ";" la escribimos en el archivo.
            [fout.write(linea.strip() + '\n') for linea in lineas if ';;' not in linea and ';\n' not in linea]
            #Comprueba si hay algo de la forma XX:XX:XX y lo cambia por ;
            #Como no necesitamos la hora, la eliminamos quitando lo que hay después del ultimo ;
            #Y después comprueba si no hay 2 ";" seguidos ni hay un salto de línea después de l ";" la escribimos en el archivo
            [fout.write(linea[:linea.rindex(';')] + '\n') for linea in lineas if re.search(r'\d{2}:\d{2}:\d{2}', linea) and ';;' not in linea and ';\n' not in linea]

    dataframe=pd.read_csv(nombre_archivo_limpio,sep=";")

    # Como la fecha está mal formateada, vamos a cambiarla.
    # Si hay un valor decimal en dataframe['date'] lo vamos a cambiar al formato YYYY-MM-DD
    # Lo hacemos con una función lambda que recibe un valor y si es un valor decimal lo cambia al formato YYYY-MM-DD
    dataframe['date'] = dataframe['date'].apply(lambda x: dt.datetime.fromtimestamp(x).strftime('%Y-%m-%d') if isinstance(x, float) else x)
    dataframe.to_csv(nombre_archivo_limpio,sep =";", index=False)

    return nombre_archivo_limpio


                
def crear_xml(informes, recomendacion):
    """
    Crear un archivo XML, donde se guarde el informe generado para cada archivo de entrada ("informe_order_details.csv", "informe_orders.csv", "informe_pizzas.csv" y "informe_pizza_types").
    Y que también se guarde la recomendación de compra semanal ("compra_semana.csv").
    """
    """
    Todos los argumentos de entrada son csv que queremos guardar en un único xml.
    informes: lista de los nombres de los archivos csv que queremos guardar en el xml.
    recomendacion: nombre del archivo csv que queremos guardar en el xml.

    """
    fout="informe.xml"
    root = ET.Element("root")

    for informe in informes:
        ET.SubElement(root, "informe", name=informe).text = open(informe, 'r').read()

    ET.SubElement(root, "recomendacion", name=recomendacion).text = open(recomendacion, 'r').read()

    tree = ET.ElementTree(root)
    tree.write(fout, encoding="utf-8", xml_declaration=True)

def prettify(elem):
    """
    Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

if __name__ == "__main__":
    limpiar_archivos('order_details.csv')
    limpiar_orders('orders.csv')
    detalles_pedidos_limpio, pizzas, ingredientes, pedidos_limpio, detalles_pedidos, pedidos= extract()
    d_ingr = transform(detalles_pedidos_limpio, pizzas, ingredientes, pedidos_limpio, detalles_pedidos, pedidos)
    load(d_ingr)
    informes = ["informe_order_details.csv", "informe_orders.csv", "informe_pizzas.csv", "informe_pizza_types.csv"]
    recomendacion = "compra_semana.csv"
    crear_xml(informes, recomendacion)




    

    
