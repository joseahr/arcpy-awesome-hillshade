# Índice
***

- [Introducción y objetivos](#introducción-y-objetivos)
    - [Herramientas utilizadas](#herramientas-utilizadas)
    - [Desarrollo del formulario en ArcMap](#desarrollo-del-formulario-en-arcmap)
- [Desarrollo de la práctica](#desarrollo-de-la-práctica)
- [Resultados](#resultados)
- [Conclusiones](#conclusiones)

# Introducción y Objetivos
***

El objetivo del presente documento es mostrar el trabajo realizado en la elaboración de una herramienta para **ArcMap** que realiza una ```combinación múltiple``` de sombreados sobre una imagen en formato ráster.

> El problema reside en que en muchas ocasiones y debido a la variabilidad del terreno, un único tipo de sombreado no es óptimo para todas las zonas, por lo que sería útil disponer de una herramienta más flexible que permitiese combinar diversos focos de luz para mejorar el resultado final. ```(Inmhof, 1982; Keates, 1989)```

La herramienta diseñada permite la combinación de múltiples focos de luz simultaneamente, esto se consigue mediante la suma de los diferentes mapas de sombra generados independientemente para cada par de valores ```[acimut, elevación]``` y reescalando el resultado a un único rango de valores de gris ```[0, 255]```

### Herramientas utilizadas

 - ArcMap 10.1 
 - Python 2.7 (arcpy - junto con la extensión 'Spatial')

 
### Desarrollo del formulario en ArcMap

El desarrollo para el formulario es bastante sencillo y se adapta más o menos a las necesidades requeridas por la herramienta. Cuenta con:
 - Ráster de entrada (Input)
 - Ráster de salida (Output)
 - Acimutes (MultiValue)
 - Elevaciones (MultiValue)

Dentro de las posibilidades que ArcMap nos da es el mejor diseño posible. El formulario esperado podría ser una combinación del formulario generado cuando el tipo de dato es ```Cell Size XY``` y ```MultiValue```. Es decir, un formulario multivalor que almacene pares de valores ```[acimut, elevación]```. Si intentamos reproducir esto, el formulario que genera *ArcMap* no funciona correctamente.

Algunas posibles alternativas para la creación del formulario:
 - Crear nuestro propio GUI utilizando *PyQt4*
 - Crear una pequeña aplicación de escritorio (*PyQt4*, Aplicaciones híbridas, ...)

La primera alternativa funcionaría tanto como dentro del entorno de *ArcMap* (Como una herramienta de las ```toolboxes```) como una aplicación de escritorio.
> La segunda alternativa, si hablamos de ```aplicaciones híbridas``` (las cuales están creciendo a pasos agigantados en la actualidad), solo serviría fuera del entorno de *ArcMap* (Aunque por supuesto habría que tener instalado *ArcMap* y configurada la ```variable de entorno``` hacia el path de python de *ArcGIS*) pero nos da mucha flexibilidad para crear el formulario e interactuar con arcpy.

Una combinación de herramientas/tecnologías para crear la aplicación podría ser:
 - *Electron* (Framework para crear aplicaciones de escritorio multiplataforma, basado en NodeJS)
 - *Angular 4* y *Angular Material* (Lógica y diseño de nuestra aplicación) [Opcional]
 - *Python 2.7* (*arcpy*) para ejecutar el script.

# Desarrollo de la práctica
***
 
 El primer elemento de la herramienta llevado a cabo ha sido el formulario donde se introducirán los datos. 
![Ráster de entrada](https://raw.githubusercontent.com/joseahr/arcpy-awesome-hillshade/master/images/gui.png) 
 
 Como se ha comentado antes consta de ```4 parámetros```:
  - Ráster de entrada (Input)

![Ráster de entrada](https://raw.githubusercontent.com/joseahr/arcpy-awesome-hillshade/master/images/raster_entrada.png)

 - Ráster de salida (Output)

![Ráster de salida](https://raw.githubusercontent.com/joseahr/arcpy-awesome-hillshade/master/images/raster_salida.png)

 - Acimutes (MultiValue)

![Acimutes](https://raw.githubusercontent.com/joseahr/arcpy-awesome-hillshade/master/images/acimutes.png)

 - Elevaciones (MultiValue)

![Elevaciones](https://raw.githubusercontent.com/joseahr/arcpy-awesome-hillshade/master/images/elevaciones.png)

Al ser los acimutes y las elevaciones parámetros ```Long``` y ```Multivalue```, es decir una lista de acimutes y una lista de elevaciones, el usuario deberá introducir en orden los pares de valores, es decir el primer elemento de la lista de acimutes se corresponde con el primer elemento de las lista de elevaciones.
Sobreescribiendo el método ```updateMessages``` de la clase ```ToolValidator```, podemos modificar el comportamiento de validación de la herramienta y así adaptarlo para mostrar errores:
 - ```Cuando el usuario introduzca valores erróneos de acimut y elevación```

![Error Validación 1](https://raw.githubusercontent.com/joseahr/arcpy-awesome-hillshade/master/images/ejemplo_error1.png)

 - ```Para poder avisar al usuario que debe introducir el mismo número de acimutes y elevaciones```.

 ![Error Validación 2](https://raw.githubusercontent.com/joseahr/arcpy-awesome-hillshade/master/images/ejemplo_error.png)

Si hay el mismo número de elevaciones y acimutes, todos los acimutes introducidos están en el rango ```[0, 360]``` y todas las elevaciones introducidas están en el rango ```[0, 90]``` el formulario no mostrará ningún error de validación para los campos acimutes y elevaciones:

 ![GUI sin errores](https://raw.githubusercontent.com/joseahr/arcpy-awesome-hillshade/master/images/sin_errores.png)

A continuación se muestra el código **comentado** empleado para la validación, sobrescribiendo el método ```updateMessages``` de la clase ```ToolValidator```:

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

Y finalmente el código **comentado** del script que ejecuta el proceso:

```python
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
    do() ## EJECUTAMOS LA FUNCIÃ“N QUE HACE TODO EL PROCESO
    #Devolución de la licencia
    arcpy.CheckInExtension('Spatial')
else:
    print ('Licencia no disponible')
```

# Resultados 
***

Se han realizado varias pruebas con distintos focos de luz:
- Prueba 1 : (3 focos de luz)

| acimut | elevacion |
| :--------: | :--------: |
| 90   | 90   |
| 180  | 45   |
| 270  | 50   |

 ![Resultado 1](https://raw.githubusercontent.com/joseahr/arcpy-awesome-hillshade/master/images/prueba_1_res.png)

- Prueba 2 : (2 focos de luz)

| acimut | elevacion |
| :--------: | :--------: |
| 90   | 50   |
| 270  | 90   |

 ![Resultado 2](https://raw.githubusercontent.com/joseahr/arcpy-awesome-hillshade/master/images/prueba_2_res.png)

# Conclusiones
***

Como se observa en los reusltados se ha intentado combinar focos de luz oblicuos, para obtener una buena representación de la topografía del terreno con focos de luz cenitales, para remarcar zonas de fuertes variaciones en el terreno y diminuir las posibles sombras generadas por el foco de luz oblicuo.

Vemos que al quitar un foco de luz oblicuo se distingue peor las zonas de poco cambio en esa dirección (180º)