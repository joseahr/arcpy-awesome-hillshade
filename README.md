# Introducción y Objetivos
***
[![N|Solid](https://geoinnova.org/blog-territorio/wp-content/uploads/2016/10/7.jpg)](https://nodesource.com/products/nsolid)

El objetivo del presente documento es mostrar el trabajo realizado en la elaboración de una herramienta para ArcMap que realiza una combinación múltiple de sombreados sobre una imagen en formato ráster.

### Herramientas utilizadas

 - ArcMap 10.1 
 - Python 2.7

 
### Desarrollo del formulario (GUI) en ArcMap

El desarrollo para el formulario es bastante sencillo y se adapta más o menos a las necesidades requeridas por la herramienta. Cuenta con:
 - Ráster de entrada (Input)
 - Ráster de salida (Output)
 - Acimutes (MultiValue)
 - Elevaciones (MultiValue)

Dentro de las posibilidades que ArcMap nos da es el mejor diseño posible. El formulario esperado podría ser una combinación del formulario generado cuando el tipo de dato es "Cell Size XY" y "MultiValue". Es decir, un formulario multivalor que almacene pares de valores [acimut, elevación]. Si intentamos reproducir esto, el formulario que genera ArcMap no funciona correctamente.

Algunas posibles alternativas para la creación del formulario:
 - Crear nuestro propio GUI utilizando PyQt4
 - Crear una pequeña aplicación de escritorio (PyQt4, Aplicaciones híbridas, ...)

La primera alternativa funcionaría tanto como dentro del entorno de ArcMap (Como una herramienta de las toolboxes) como una aplicación de escritorio.
> La segunda alternativa, si hablamos de aplicaciones híbridas (las cuales están creciendo a pasos agigantados en la actualidad), solo serviría fuera del entorno de ArcMap (Aunque por supuesto habría que tener instalado ArcMap y configurada la variable de entorno hacia el path de python de ArcGIS) pero nos da mucha flexibilidad para crear el formulario e interactuar con arcpy.

Una combinación de herramientas/tecnologías para crear la aplicación podría ser:
 - Electron (Framework para crear aplicaciones de escritorio multiplataforma, basado en NodeJS)
 - Angular 4 y Angular Material (Lógica y diseño de nuestra aplicación) [Opcional]
 - Python 2.7 (arcpy) para ejecutar el script.

# Desarrollo de la práctica
***
 
 El primer elemento de la herramienta llevado a cabo ha sido el formulario donde se introducirán los datos. Como se ha comentado antes consta de 4 parámetros:
  - Ráster de entrada (Input)
 - Ráster de salida (Output)
 - Acimutes (MultiValue)
 - Elevaciones (MultiValue)
 
Al ser los acimutes y las elevaciones parámetros Long Multivalue, es decir una lista de acimutes y una lista de elevaciones, el usuario deberá introducir en orden los pares de valores, es decir el primer elemento de la lista de acimutes se corresponde con el primer elemento de las lista de elevaciones.
Sobreescribiendo el método updateMessages de la clase ToolValidator, podemos modificar el comportamiento de validación de la herramienta y así adaptarlo para mostrar errores cuando el usuario introduzca valores erroneos de acimut y elevación y poder avisar al usuario de que debe introducir el mismo número de acimutes y elevaciones.
 
```python
import arcpy
class ToolValidator(object):
  """Class for validating a tool's parameter values and controlling
  the behavior of the tool's dialog."""

  def __init__(self):
    """Setup arcpy and the list of tool parameters."""
    self.params = arcpy.GetParameterInfo()

  def initializeParameters(self):
    """Refine the properties of a tool's parameters.  This method is
    called when the tool is opened."""
    return

  def updateParameters(self):
    """Modify the values and properties of parameters before internal
    validation is performed.  This method is called whenever a parmater
    has been changed."""
    return

  def updateMessages(self):
    """Modify the messages created by internal validation for each tool
    parameter.  This method is called after internal validation."""
    # Obtenemos los parámetros (acimutes y elevaciones hasta el momento)
    acimutes    = self.params[2].values
    elevaciones = self.params[3].values
    # Si todavía no se ha introducido algun valor en los parámetros devolverá None, pero queremos una lista vacía para poder comparar
    acimutes    = acimutes if acimutes else []
    elevaciones = elevaciones if elevaciones else []
    # Mensajes de error para los campos acimutes y elevaciones
    errorsAcimutField = []
    errorsElevacionField = []
    # Si alguno de los dos parámetros se ha modificado
    if self.params[2].altered or self.params[3].altered :
        # Y el tamaño de las listas no coincide
        if not len(acimutes) == len(elevaciones):
            # Añadimos error a las listas de los dos parámetros
            errorsAcimutField.append('Debe haber el mismo número de acimutes y elevaciones.')
            errorsElevacionField.append('Debe haber el mismo número de acimutes y elevaciones.')
    # Si algún acimut está fuera del rango [0, 360] añadimos error
    if any(acimut > 360 or acimut < 0 for acimut in acimutes):
        errorsAcimutField.append('Rango de valores de acimutes [0, 360].')
    # Si alguna elevación está fuera del rango [0, 90] añadimos error
    if any(elevacion > 90 or elevacion < 0 for elevacion in elevaciones): 
        errorsElevacionField.append('Rango de valores de elevaciones [0, 90].')
    # Si alguna lista contiene mensajes de error -> Añadimos error al parámetro (GUI)
    if len(errorsAcimutField) : self.params[2].setErrorMessage('\n'.join(errorsAcimutField))
    if len(errorsElevacionField) : self.params[3].setErrorMessage('\n'.join(errorsElevacionField))
    return
```
















```python
import arcpy

'''
@ FunciÃ³n que ejecutarÃ¡ todo el proceso
'''
def do():
    # Obtenemos los parÃ¡metros
    mde, salida, acimuts, elevaciones = [ arcpy.GetParameter(i) for i in range(0, 4) ]
    # Deben tener el mismo tamaÃ±o ambas listas
    if not len(acimuts) == len(elevaciones) : arcpy.AddError('Debe seleccionar el mismo nÃºmero de elevaciones que acimuts')
    # Juntamos las dos listas por pares
    values = zip(acimuts, elevaciones)
    #values = map(lambda x : dict( zip(['acimut', 'elevacion'], x) ), zip(acimuts, elevaciones) )

    hillshades = [] # AlmacenarÃ¡ todos los hillshades
    # Recorremos las opciones [[acimut, elevacion], ...]
    for options in values :
        acimut, elevacion = options # Cogemos los valores de la lista
        # Creamos el hillshade con los parÃ¡metros
        hillshade = arcpy.sa.Hillshade(mde, acimut, elevacion)
        # AÃ±adimos el hillshade creado
        hillshades.append(hillshade)
    # Cuando ha acabado el bucle ...
    # Sumamos todos los raster (sombreados)
    suma = reduce(lambda a, b : a + b, hillshades)
    # Obtenemos el mÃ¡ximo y el mÃ­nimo de la suma de los rasters
    maximum, minimum = suma.maximum, suma.minimum
    # Estandarizamos los valores entre [0, 255]
    estandarizado = (suma - minimum) * 255 / (maximum - minimum)
    # Guardamos la suma generada en la salida
    estandarizado.save(str(salida))

# Entrada del programa -- Comprobamos la extensiÃ³n 'Spatial'
if arcpy.CheckExtension('Spatial') == 'Available':
    #PeticiÃ³n de la licencia
    arcpy.CheckOutExtension('Spatial')
    do() ## EJECUTAMOS LA FUNCIÃ“N QUE HACE TODO EL PROCESO
    #DevoluciÃ³n de la licencia
    arcpy.CheckInExtension('Spatial')
else:
    print ('Licencia no disponible')

```
