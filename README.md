# Arbol-de-Sintaxis
Carlos Alberto Cardona pulido 

# Descripción.
En este repositorio se encuentra el código en Python de una calculadora que permite realizar operaciones de suma, resta, multiplicación y división. Además, genera el árbol sintáctico de la operación que se ingrese, basado en la siguiente gramática:

- `E -> E opsuma T`
- `E -> T`
- `T -> T opmul F`
- `T -> F`
- `F -> id` 
- `F -> num`
- `F -> ( E )`

El código está compuesto por dos archivos principales:

- [Gramatica.txt](https://github.com/ALMA3112/Arbol-de-Sintaxis/blob/main/Arbol%20Sintactico/gramatica.txt): Contiene las reglas gramaticales para el analizador.
- [Calculadora.py](https://github.com/ALMA3112/Arbol-de-Sintaxis/blob/main/Arbol%20Sintactico/Calculadora.py): Implementa la calculadora y utiliza la gramatica para poder hacer el arbol sintáctico.

# Explicacion Funciones del Codigo. 
En el archivo Calculadora.py se utilizan diferentes funciones, las cuales serán explicadas individualmente de la siguiente manera:

- `class Token:` Guarda la información de cada pedazo de texto (número, variable, símbolo, etc.). Tiene un tipo y un valor. 
- `def lexear:` Toma la espresión que escribe el usuario (como "2+3") y la corta en tokens. Así en lugar de trabajar con texto suelto, trabaja con objetos más claros.
- `Nodo:` Sirve para construir el árbol sintáctico. Cada nodo tiene una etiqueta (como E, T, F, num), puede tener hijos ( son otros nodos) y a veces valor.
- `Parser:` ESte es el que sigue la gramática. La función va leyendo tokens y construye el árbol con nodos. Tine funciones para cada regla de la gramática.

- `parse:` Es el inicio del parser. Llama a parse_E y al final comprueba que no queden tokens sin usar.
- `evaluar:` Recorre el árbol y calcula el resultado.
- `NodoVista:`Es como Nodo, pero simplificado para dibujar. Solo guarda la etiqueta y los hijos.
- `ast_a_vista:` Muestra el árbol vista (NodoVista).
- `dibujar_caja:`Dinuja la caja con al etiqueta del nodo y si tiene hijos los coloca debajo contectandolos con una línea. Es recursiva, se llama a si misma para diujar todo el árbol.
- `imprimir_arbol:`Usa dibujar_caja y muestra el árbol en la pantalla línea por línea.
- `main:`Es la función principal. Pide una expresión al usuario, la convierte en tokens, la parsea, la evalúa y muestra el resultado junto con el árbol sintáctico.

# 
