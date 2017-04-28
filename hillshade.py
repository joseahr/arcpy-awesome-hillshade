import arcpy

'''
@ Función que ejecutará todo el proceso
'''
def do():
    # Obtenemos los parámetros
    mde, salida, acimuts, elevaciones = [ arcpy.GetParameter(i) for i in range(0, 4) ]
    # Deben tener el mismo tamaño ambas listas
    if not len(acimuts) == len(elevaciones) : arcpy.AddError('Debe seleccionar el mismo número de elevaciones que acimuts')
    # Juntamos las dos listas por pares
    values = zip(acimuts, elevaciones)
    #values = map(lambda x : dict( zip(['acimut', 'elevacion'], x) ), zip(acimuts, elevaciones) )

    hillshades = [] # Almacenará todos los hillshades
    # Recorremos las opciones [[acimut, elevacion], ...]
    for options in values :
        acimut, elevacion = options # Cogemos los valores de la lista
        # Creamos el hillshade con los parámetros
        hillshade = arcpy.sa.Hillshade(mde, acimut, elevacion)
        # Añadimos el hillshade creado
        hillshades.append(hillshade)
    # Cuando ha acabado el bucle ...
    # Sumamos todos los raster (sombreados)
    suma = reduce(lambda a, b : a + b, hillshades)
    # Obtenemos el máximo y el mínimo de la suma de los rasters
    maximum, minimum = suma.maximum, suma.minimum
    # Estandarizamos los valores entre [0, 255]
    estandarizado = (suma - minimum) * 255 / (maximum - minimum)
    # Guardamos la suma generada en la salida
    estandarizado.save(str(salida))

# Entrada del programa -- Comprobamos la extensión 'Spatial'
if arcpy.CheckExtension('Spatial') == 'Available':
    #Petición de la licencia
    arcpy.CheckOutExtension('Spatial')
    do() ## EJECUTAMOS LA FUNCIÓN QUE HACE TODO EL PROCESO
    #Devolución de la licencia
    arcpy.CheckInExtension('Spatial')
else:
    print ('Licencia no disponible')



