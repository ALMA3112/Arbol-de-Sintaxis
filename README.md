# Arbol Sintactico

Este repositorio contiene un pequeño analizador sintáctico (parser) para expresiones aritméticas y una gramática en formato texto utilizada por el programa. El objetivo es validar expresiones como `2+3*4` y generar un árbol sintáctico en formato de imagen . El proyecto fue pensado para ejecutarse desde la terminal en un entorno Ubuntu y utiliza Python junto con las librerías `networkx` y `matplotlib` para construir y dibujar el árbol.

## Requisitos y dependencias

El programa está escrito en Python y no se necesita una instalación demasiado compleja. Para ejecutar el código se necesitara tener Python3 y `pip` disponibles. El resto de dependencias se instalan con `pip`. Se recomienda usar un entorno virtual (`venv`) para aislar las dependencias del sistema y que el que el ejecutable no genere algun problema. 

A continuación se explica cómo preparar un entorno limpio en Ubuntu y las dependencias exactas que se usan.

## Instalación en Ubuntu 

Primero, se debe de actualizar la lista de paquetes e instalar Python3 y `pip` si no se tienen. Despues debe de crear y activar un entorno virtual.Finalmente se debe de instalar las librerias necesarias con `pip`.

```
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install networkx matplotlib
```
Con estos comandos debe de ser suficiente para instalar todo para ejecutar el codigo y guardar en formato PNG el arbol sintactico. 

## Archivos principales

El programa principal se llama [Calculadora.py](https://github.com/ALMA3112/Arbol-de-Sintaxis/blob/main/Arbol%20Sintactico/Calculadora.py) y la gramática usada por defecto se guarda en [gramatica.txt](https://github.com/ALMA3112/Arbol-de-Sintaxis/blob/main/Arbol%20Sintactico/gramatica.txt). El script carga la gramática, tokeniza la expresión que se le pase por línea de comandos, construye un árbol sintáctico (si la expresión es válida) y guarda una imagen llamada `arbol_sintactico.png` en el directorio desde donde se ejecutó. Asegurarse de que el archivo de gramática esté en el mismo directorio que el script. 

## Formato de la gramática

La gramática se almacena en texto plano con producciones del tipo `A -> B C | D`. Cada línea que contenga `->` es interpretada como una regla. Los símbolos terminales que el analizador reconoce por token son `num` para números, operadores `+ - * /` (en tokens aparece como: `opsuma` y `opmul`) y paréntesis `(` `)` (como `pari` y `pard`). 

## Uso desde terminal (ejemplos)

Para ejecutar el programa, ubique el directorio que contiene `Calculadora.py` y `gramatica.txt` y ejecute el comando con Python3. A continuación hay ejemplos concretos que puede copiar y pegar. El primer ejemplo usa una expresión válida; el segundo muestra el comportamiento con una cadena inválida.

```
python3 Calculadora.py gramatica.txt "2+3*4"
```

Al ejecutarlo con una expresión válida se vera en la salida: `Cadena valida. arbol de sintaxis generado.` y se guardará un archivo `arbol_sintactico.png` con la representación del árbol.

[Imagen1](https://github.com/ALMA3112/Arbol-de-Sintaxis/blob/main/Imagenes/1.png)

Si la expresión no respeta la gramática, la salida será `Cadena invalida.`. Por ejemplo:

```
python3 Calculadora.py gramatica.txt "2++3"
```

Este último comando normalmente imprimirá `Cadena invalida.` porque la tokenización y el análisis detectan el error sintáctico. Como se muestra a continuacion: 



## Detalles de ejecución y comportamiento

El script realiza los siguientes pasos cuando lo invocas: carga la gramática desde el archivo de texto, convierte la cadena de entrada en tokens (`num`, `opsuma`, `opmul`, `pari`, `pard`), intenta analizarla aplicando las reglas recursivas para `E`, `T` y `F`, y si el análisis termina correctamente genera y normaliza un árbol sintáctico. La imagen final del árbol se genera con NetworkX y Matplotlib y se guarda como `arbol_sintactico.png`.

Si trabajas en un entorno en el que Matplotlib no puede abrir una ventana gráfica, esto no impide que se guarde la imagen; sin embargo, en algunos entornos puede ser necesario forzar un backend no interactivo (ver la sección de instalación).

## Ejemplos de prueba adicionales

Puedes probar expresiones con paréntesis y con combinaciones de operadores para verificar la precedencia y la construcción del árbol. Por ejemplo, `"(1+2)*3"`, `"4/2+6"` y `"7-(3+1)"` son buenos candidatos para validar distintos caminos de parseo y ver cómo el árbol refleja la estructura sintáctica.

## Solución de problemas comunes

Si obtienes un mensaje de error relacionado con símbolos no reconocidos, revisa que la expresión de entrada contenga únicamente dígitos, espacios, operadores `+ - * /` y paréntesis. Si Matplotlib falla al intentar dibujar, verifica que has instalado la dependencia correctamente y, si es un servidor sin entorno gráfico, exporta `MPLBACKEND=Agg` antes de ejecutar el script.

Si necesitas que el script acepte identificadores (tokens `id`) u otros terminales distintos, puedes ampliar la función de tokenización en `Calculadora.py` y actualizar la gramática en `gramatica.txt` acorde a las nuevas reglas.

## Licencia y notas finales

Este proyecto es un ejemplo didáctico para mostrar un análisis sintáctico básico y la generación de un árbol. Si quieres que lo adapte para soportar más tokens, salida en formatos distintos (SVG, DOT) o integración con Graphviz, dímelo y lo preparo.
