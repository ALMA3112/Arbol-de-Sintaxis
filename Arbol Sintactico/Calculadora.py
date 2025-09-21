import re

TOK_NUM = "NUM"        
TOK_ID  = "ID"         
TOK_MAS = "MAS"        
TOK_MENOS = "MENOS"    
TOK_POR = "POR"        
TOK_DIV = "DIV"        
TOK_PAR_IZQ = "PAR_IZQ" 
TOK_PAR_DER = "PAR_DER" 
TOK_EOF = "EOF"        # fin de la entrada

patrones = [
    (TOK_NUM,      r'\d+(\.\d+)?'),         
    (TOK_ID,       r'[A-Za-z_][A-Za-z0-9_]*'), 
    (TOK_MAS,      r'\+'),
    (TOK_MENOS,    r'-'),
    (TOK_POR,      r'\*'),
    (TOK_DIV,      r'/'),
    (TOK_PAR_IZQ,  r'\('),
    (TOK_PAR_DER,  r'\)'),
    ('ESPACIO',    r'[ \t]+'),             
    ('OTRO',       r'.'),                  
]

regex_tokens = '|'.join('(?P<%s>%s)' % p for p in patrones)
matcher = re.compile(regex_tokens).match

# guarda el tipo y valor
class Token:
    def __init__(self, tipo, valor=None):
        self.tipo = tipo
        self.valor = valor
    def __repr__(self):
        return f"Token({self.tipo}, {self.valor})"

# Separa en tokens
def lexear(texto):
    pos = 0
    m = matcher(texto, pos)
    while m:
        nombre = m.lastgroup
        val = m.group(nombre)
        if nombre == TOK_NUM:
            yield Token(TOK_NUM, float(val))
        elif nombre == TOK_ID:
            yield Token(TOK_ID, val)
        elif nombre == TOK_MAS:
            yield Token(TOK_MAS, val)
        elif nombre == TOK_MENOS:
            yield Token(TOK_MENOS, val)
        elif nombre == TOK_POR:
            yield Token(TOK_POR, val)
        elif nombre == TOK_DIV:
            yield Token(TOK_DIV, val)
        elif nombre == TOK_PAR_IZQ:
            yield Token(TOK_PAR_IZQ, val)
        elif nombre == TOK_PAR_DER:
            yield Token(TOK_PAR_DER, val)
        elif nombre == 'ESPACIO':
            pass
        else:
            raise SyntaxError(f"Caracter invalido: {val!r}")
        pos = m.end()
        m = matcher(texto, pos) 
    yield Token(TOK_EOF, None)

class Nodo:
    def __init__(self, etiqueta, hijos=None, valor=None, prod=None):
        # etiqueta: E, T, F, num, id, opsuma, opmul, etc.
        self.etiqueta = etiqueta
        self.hijos = hijos if hijos is not None else []
        self.valor = valor  
        self.prod = prod    
    def __repr__(self):
        if self.valor is not None:
            return f"{self.etiqueta}({self.valor})"
        return f"{self.etiqueta}"

class Parser:
    def __init__(self, lista_tokens):
        self.iterator = iter(lista_tokens) 
        self.actual = None                 
        self._avanzar()                   

    def _avanzar(self):
        self.actual = next(self.iterator)

    def _comer(self, tipo_esperado):
        if self.actual.tipo == tipo_esperado:
            t = self.actual
            self._avanzar()
            return t
        raise SyntaxError(f"Se esperaba {tipo_esperado} pero vino {self.actual.tipo}")

    # E -> E opsuma T | T
    def parse_E(self):
        izquierda = self.parse_T()
        if self.actual.tipo in (TOK_MAS, TOK_MENOS):
            while self.actual.tipo in (TOK_MAS, TOK_MENOS):
                if izquierda.etiqueta != 'E':
                    izquierda = Nodo('E', hijos=[izquierda], prod="E -> T")
                if self.actual.tipo == TOK_MAS:
                    self._comer(TOK_MAS)
                    operador = Nodo('opsuma', valor='+', prod="opsuma -> +")
                else:
                    self._comer(TOK_MENOS)
                    operador = Nodo('opsuma', valor='-', prod="opsuma -> -")
                derecha = self.parse_T()
                izquierda = Nodo('E', hijos=[izquierda, operador, derecha], prod="E -> E opsuma T")
            return izquierda
        else:
            return Nodo('E', hijos=[izquierda], prod="E -> T")

    # T -> T opmul F | F
    def parse_T(self):
        izquierda = self.parse_F()
        if self.actual.tipo in (TOK_POR, TOK_DIV):
            while self.actual.tipo in (TOK_POR, TOK_DIV):
                if izquierda.etiqueta != 'T':
                    izquierda = Nodo('T', hijos=[izquierda], prod="T -> F")
                if self.actual.tipo == TOK_POR:
                    self._comer(TOK_POR)
                    operador = Nodo('opmul', valor='*', prod="opmul -> *")
                else:
                    self._comer(TOK_DIV)
                    operador = Nodo('opmul', valor='/', prod="opmul -> /")
                derecha = self.parse_F()
                izquierda = Nodo('T', hijos=[izquierda, operador, derecha], prod="T -> T opmul F")
            return izquierda
        else:
            return Nodo('T', hijos=[izquierda], prod="T -> F")

    # F -> id | num | ( E )
    def parse_F(self):
        if self.actual.tipo == TOK_ID:
            t = self._comer(TOK_ID)
            nodo_id = Nodo('id', valor=t.valor)
            return Nodo('F', hijos=[nodo_id])
        elif self.actual.tipo == TOK_NUM:
            t = self._comer(TOK_NUM)
            nodo_num = Nodo('num', valor=t.valor)
            return Nodo('F', hijos=[nodo_num])
        elif self.actual.tipo == TOK_PAR_IZQ:
            self._comer(TOK_PAR_IZQ)
            nodo_pari = Nodo('pari', valor='(')
            inner = self.parse_E()
            self._comer(TOK_PAR_DER)
            nodo_pard = Nodo('pard', valor=')')
            return Nodo('F', hijos=[nodo_pari, inner, nodo_pard])
        else:
            raise SyntaxError(f"Token inesperado en F: {self.actual}")

    def parse(self):
        raiz = self.parse_E()
        if self.actual.tipo != TOK_EOF:
            raise SyntaxError("Quedó texto sin parsear")
        return raiz

def evaluar(nodo, valores_id):
    if nodo.etiqueta == 'E':
        if len(nodo.hijos) == 1:
            return evaluar(nodo.hijos[0], valores_id)
        a = evaluar(nodo.hijos[0], valores_id)
        op = nodo.hijos[1]
        b = evaluar(nodo.hijos[2], valores_id)
        if op.valor == '+':
            return a + b
        else:
            return a - b
    if nodo.etiqueta == 'T':
        if len(nodo.hijos) == 1:
            return evaluar(nodo.hijos[0], valores_id)
        a = evaluar(nodo.hijos[0], valores_id)
        op = nodo.hijos[1]
        b = evaluar(nodo.hijos[2], valores_id)
        if op.valor == '*':
            return a * b
        else:
            if b == 0:
                raise ZeroDivisionError("División por cero")
            return a / b
    if nodo.etiqueta == 'F':
        if len(nodo.hijos) == 1:
            hijo = nodo.hijos[0]
            if hijo.etiqueta == 'num':
                return float(hijo.valor)
            if hijo.etiqueta == 'id':
                nombre = hijo.valor
                if nombre not in valores_id:
                    entrada = input(f"Ingresa valor para {nombre}: ")
                    valores_id[nombre] = float(entrada)
                return float(valores_id[nombre])
            return evaluar(hijo, valores_id)
        else:
            return evaluar(nodo.hijos[1], valores_id)
    if nodo.etiqueta == 'num':
        return float(nodo.valor)
    if nodo.etiqueta == 'id':
        nombre = nodo.valor
        if nombre not in valores_id:
            entrada = input(f"Ingresa valor para {nombre}: ")
            valores_id[nombre] = float(entrada)
        return float(valores_id[nombre])
    raise RuntimeError(f"Etiqueta desconocida: {nodo.etiqueta}")

class NodoVista:
    def __init__(self, etiqueta, hijos=None):
        self.etiqueta = etiqueta
        self.hijos = hijos if hijos is not None else []

def ast_a_vista(nodo):
    if nodo is None:
        return None
    etiqueta = nodo.etiqueta
    if etiqueta in ('E','T','F'):
        lista_hijos = []
        for c in nodo.hijos:
            if c.etiqueta in ('opsuma','opmul'):
                lista_hijos.append(NodoVista(c.etiqueta)) # sin el signo debajo
            elif c.etiqueta in ('num','id','pari','pard'):
                if c.valor is not None:
                    lista_hijos.append(NodoVista(c.etiqueta, [NodoVista(str(c.valor))]))
                else:
                    lista_hijos.append(NodoVista(c.etiqueta))
            else:
                lista_hijos.append(ast_a_vista(c))
        return NodoVista(etiqueta, lista_hijos)
    if etiqueta in ('opsuma','opmul'):
        return NodoVista(etiqueta)
    if etiqueta in ('num','id','pari','pard'):
        if nodo.valor is not None:
            return NodoVista(etiqueta, [NodoVista(str(nodo.valor))])
        return NodoVista(etiqueta)
    return NodoVista(etiqueta, [ast_a_vista(h) for h in nodo.hijos])

def dibujar_caja(nodo_vista):
    etiqueta = nodo_vista.etiqueta
    ancho_interno = len(etiqueta)
    ancho = ancho_interno + 2
    linea_sup = "┌" + "─"*ancho + "┐"
    linea_mid = "│" + etiqueta.center(ancho) + "│"
    linea_inf = "└" + "─"*ancho + "┘"
    bloque = [linea_sup, linea_mid, linea_inf]
    ancho_bloque = len(linea_sup)
    if not nodo_vista.hijos:
        return bloque, ancho_bloque, ancho_bloque//2

    render_hijos = [dibujar_caja(h) for h in nodo_vista.hijos]
    lineas_hijos = [r[0] for r in render_hijos]
    anchos_hijos = [r[1] for r in render_hijos]
    centros_hijos = [r[2] for r in render_hijos]

    separacion = 2
    total_hijos = sum(anchos_hijos) + separacion*(len(anchos_hijos)-1)
    ancho_total = max(total_hijos, ancho_bloque)
    extra = ancho_total - total_hijos
    cur = extra//2
    comienzos = []
    for w in anchos_hijos:
        comienzos.append(cur)
        cur += w + separacion

    padre_start = (ancho_total - ancho_bloque)//2
    padre_centro = padre_start + ancho_bloque//2

    canvas = []
    for l in bloque:
        linea = [' ']*ancho_total
        for i,ch in enumerate(l):
            p = padre_start + i
            if 0 <= p < ancho_total:
                linea[p] = ch
        canvas.append(''.join(linea).rstrip())

    linea_v = [' ']*ancho_total
    linea_v[padre_centro] = '│'
    canvas.append(''.join(linea_v).rstrip())

    linea_r = [' ']*ancho_total
    linea_r[padre_centro] = '┴'
    for s,w,m in zip(comienzos, anchos_hijos, centros_hijos):
        centro_hijo = s + m
        if centro_hijo == padre_centro:
            linea_r[centro_hijo] = '│'
        else:
            lo = min(centro_hijo, padre_centro)
            hi = max(centro_hijo, padre_centro)
            for k in range(lo+1, hi):
                linea_r[k] = '─'
            linea_r[centro_hijo] = '┴'
            linea_r[padre_centro] = '┴'
    canvas.append(''.join(linea_r).rstrip())

    altura_max = max(len(lines) for lines in lineas_hijos)
    hijos_padded = []
    for lines,w in zip(lineas_hijos, anchos_hijos):
        padded = lines + [' '*w]*(altura_max - len(lines))
        hijos_padded.append(padded)

    for fila in range(altura_max):
        linea = [' ']*ancho_total
        for inicio, block, w in zip(comienzos, hijos_padded, anchos_hijos):
            seg = block[fila]
            for i,ch in enumerate(seg):
                p = inicio + i
                if 0 <= p < ancho_total:
                    linea[p] = ch
        canvas.append(''.join(linea).rstrip())

    return canvas, ancho_total, padre_centro

def imprimir_arbol(nodo_vista):
    lineas, _, _ = dibujar_caja(nodo_vista)
    for l in lineas:
        print(l)

def main():
    try:
        expr = input("Ingresa una operación: ").strip()
        if not expr:
            print("No ingresaste nada.")
            return
        tok = list(lexear(expr)) 
        p = Parser(tok)          
        arbol = p.parse()        
        valores = {}             
        try:
            resultado = evaluar(arbol, valores) 
            if abs(resultado - int(resultado)) < 1e-12:
                resultado = int(resultado)
            print("Resultado:", resultado)
        except ZeroDivisionError:
            print("Error: división por cero.")
            return
        vista = ast_a_vista(arbol)   
        print("\nÁrbol sintáctico:")
        imprimir_arbol(vista)        
    except SyntaxError as e:
        print("Error de sintaxis:", e)
    except Exception as e:
        print("Ocurrió un error:", e)

if __name__ == "__main__":
    main()
