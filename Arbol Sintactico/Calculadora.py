import sys
import networkx as nx
import matplotlib.pyplot as plt

def cargar_gramatica(ruta):
    gramatica = {}
    with open(ruta, "r") as f:
        for linea in f:
            if "->" in linea:
                izq, der = linea.strip().split("->")
                izq = " ".join(izq.split())
                producciones = [p.strip().split() for p in der.split("|")]
                if izq not in gramatica:
                    gramatica[izq] = []
                gramatica[izq].extend(producciones)
    return gramatica

def tokenizar(expr):
    tokens = []
    numero = ""
    for ch in expr:
        if ch.isdigit():
            numero += ch
        else:
            if numero:
                tokens.append(("num", numero))
                numero = ""
            if ch == "+":
                tokens.append(("opsuma", "+"))
            elif ch == "-":
                tokens.append(("opsuma", "-"))
            elif ch == "*":
                tokens.append(("opmul", "*"))
            elif ch == "/":
                tokens.append(("opmul", "/"))
            elif ch == "(":
                tokens.append(("pari", "("))
            elif ch == ")":
                tokens.append(("pard", ")"))
            elif ch.strip() == "":
                continue
            else:
                print(f"Error: simbolo no reconocido '{ch}'")
                sys.exit(1)
    if numero:
        tokens.append(("num", numero))
    return tokens

class Nodo:
    def __init__(self, etiqueta, hijos=None):
        self.etiqueta = etiqueta
        self.hijos = hijos or []

def analizar(gramatica, tokens, simbolo_inicial="E"):
    pos = [0]  

    def ver():
        if pos[0] < len(tokens):
            return tokens[pos[0]]
        return (None, None)

    def consumir(tipo_esperado=None):
        tok = ver()
        if tipo_esperado and tok[0] != tipo_esperado:
            raise SyntaxError(f"Se esperaba {tipo_esperado}, se encontro {tok}")
        if pos[0] < len(tokens):
            pos[0] += 1
            return tok
        return (None, None)

    def parse_F():
        tok = ver()
        if tok[0] == "num":
            consumir("num")
            return Nodo("F", [Nodo("num", [Nodo(tok[1])])])
        elif tok[0] == "id":
            consumir("id")
            return Nodo("F", [Nodo("id", [Nodo(tok[1])])])
        elif tok[0] == "pari":
            pari_tok = consumir("pari")  
            interno = parse_E()
            if interno is None:
                raise SyntaxError("Expresión invalida después de '('")
            if ver()[0] != "pard":
                raise SyntaxError("Falta ')'")
            pard_tok = consumir("pard")  
            return Nodo("F", [
                Nodo("pari", [Nodo(pari_tok[1])]),
                interno,
                Nodo("pard", [Nodo(pard_tok[1])])
            ])
        else:
            raise SyntaxError(f"Se esperaba F (num/id/(E)), se encontro {tok}")

    def parse_T():
        nodo = parse_F()
        if nodo is None:
            return None
        while ver()[0] == "opmul":
            op = consumir("opmul")
            derecho = parse_F()
            if derecho is None:
                raise SyntaxError("Se esperaba F despues de operador * o /")
            nodo = Nodo("T", [nodo, Nodo("opmul", [Nodo(op[1])]), derecho])
        if nodo.etiqueta != "T":
            return Nodo("T", [nodo])
        return nodo

    def parse_E():
        nodo = parse_T()
        if nodo is None:
            return None
        while ver()[0] == "opsuma":
            op = consumir("opsuma")
            derecho = parse_T()
            if derecho is None:
                raise SyntaxError("Se esperaba T despues de operador + o -")
            nodo = Nodo("E", [nodo, Nodo("opsuma", [Nodo(op[1])]), derecho])
        if nodo.etiqueta != "E":
            return Nodo("E", [nodo])
        return nodo

    try:
        raiz = parse_E()
        if raiz is None:
            return None
        if pos[0] != len(tokens):
            return None
        if isinstance(raiz, Nodo) and raiz.etiqueta == simbolo_inicial:
            return raiz
        return raiz
    except SyntaxError:
        return None

def construir_grafo(G, nodo, padre=None, contador=None, mapping=None):
    if contador is None:
        contador = {"v": 0}
    if mapping is None:
        mapping = {}
    idx = contador["v"]
    contador["v"] += 1
    nombre = f"{nodo.etiqueta}_{idx}"
    G.add_node(nombre, label=nodo.etiqueta)
    mapping[id(nodo)] = nombre
    if padre:
        G.add_edge(padre, nombre)
    for hijo in nodo.hijos:
        construir_grafo(G, hijo, nombre, contador, mapping)
    return G, mapping

def posiciones_arbol(raiz, mapping, espacio_x=1.0, espacio_y=1.5):
    posiciones = {}
    def asignar(nodo, profundidad, x_actual):
        nombre_nodo = mapping[id(nodo)]
        if not nodo.hijos:
            x = x_actual[0]
            posiciones[nombre_nodo] = (x, -profundidad * espacio_y)
            x_actual[0] += espacio_x
            return posiciones[nombre_nodo][0]
        primero = None
        ultimo = None
        for c in nodo.hijos:
            x_hijo = asignar(c, profundidad + 1, x_actual)
            if primero is None:
                primero = x_hijo
            ultimo = x_hijo
        centro_x = (primero + ultimo) / 2.0
        posiciones[nombre_nodo] = (centro_x, -profundidad * espacio_y)
        return centro_x
    asignar(raiz, 0, [0.0])
    return posiciones

def normalizar_arbol(nodo):
    if not nodo.hijos:
        return Nodo(nodo.etiqueta, [Nodo(h.etiqueta) for h in nodo.hijos]) if nodo.hijos else Nodo(nodo.etiqueta, list(nodo.hijos))

    hijos_norm = [normalizar_arbol(c) for c in nodo.hijos]

    nuevo_nodo = Nodo(nodo.etiqueta, hijos_norm)

    if nuevo_nodo.etiqueta == "E":
        while len(nuevo_nodo.hijos) >= 3 and nuevo_nodo.hijos[1].etiqueta == "opsuma" and nuevo_nodo.hijos[0].etiqueta != "E":
            izq = nuevo_nodo.hijos[0]
            izq_envuelto = Nodo("E", [izq])
            nuevos_hijos = [izq_envuelto] + nuevo_nodo.hijos[1:]
            nuevo_nodo = Nodo("E", nuevos_hijos)
        return nuevo_nodo

    if nuevo_nodo.etiqueta == "T":
        while len(nuevo_nodo.hijos) >= 3 and nuevo_nodo.hijos[1].etiqueta == "opmul" and nuevo_nodo.hijos[0].etiqueta != "T":
            izq = nuevo_nodo.hijos[0]
            izq_envuelto = Nodo("T", [izq])
            nuevos_hijos = [izq_envuelto] + nuevo_nodo.hijos[1:]
            nuevo_nodo = Nodo("T", nuevos_hijos)
        return nuevo_nodo
    return nuevo_nodo

def dibujar_arbol(nodo):
    G = nx.DiGraph()
    nodo_norm = normalizar_arbol(nodo)
    G, mapping = construir_grafo(G, nodo_norm)
    pos = posiciones_arbol(nodo_norm, mapping)
    etiquetas = nx.get_node_attributes(G, 'label')
    plt.figure(figsize=(12, 6))
    nx.draw(G, pos, with_labels=True, labels=etiquetas,
            node_size=1200, node_color="lightblue",
            font_size=9, font_weight="bold", arrows=False)
    plt.axis('off')
    plt.savefig("arbol_sintactico.png", dpi=300)
    print(" El arbol sintáctico se guardo como 'arbol_sintactico.png'")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python3 Calculadora.py gramatica.txt \"2+3-4\"")
        sys.exit(1)

    archivo_gram = sys.argv[1]
    expresion = sys.argv[2]

    gramatica = cargar_gramatica(archivo_gram)
    tokens = tokenizar(expresion)

    arbol = analizar(gramatica, tokens, "E")

    if arbol:
        print("Cadena valida. arbol de sintaxis generado.")
        dibujar_arbol(arbol)
    else:
        print("Cadena invalida.")
