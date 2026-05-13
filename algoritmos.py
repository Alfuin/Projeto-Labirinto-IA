import heapq
from collections import deque
import math

#  HEURÍSTICAS (usadas pelo A*)
def heuristica_manhattan(a, b):
    """Distância de Manhattan — apenas movimentos ortogonais."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def heuristica_euclidiana(a, b):
    """Distância Euclidiana — movimentos em qualquer direção."""
    return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

#  CLASSE: GRAFO / GRADE (Grid)
class Grade:
    """
    Representa o mapa como uma grade 2D.

    Células:
      0 = livre (caminho possível)
      1 = obstáculo (parede)

    Movimentos: 4 direções (cima, baixo, esquerda, direita)
    """

    def __init__(self, linhas, colunas, obstaculos=None):
        self.linhas   = linhas
        self.colunas  = colunas
        self.grade    = [[0] * colunas for _ in range(linhas)]

        if obstaculos:
            for (r, c) in obstaculos:
                self.grade[r][c] = 1

    def eh_valido(self, linha, coluna):
        "Verifica se a célula está dentro dos limites e não é obstáculo."
        return (
            0 <= linha < self.linhas and
            0 <= coluna < self.colunas and
            self.grade[linha][coluna] == 0
        )

    def vizinhos(self, pos):
        "Retorna os vizinhos válidos de uma posição (4 direções)."
        r, c = pos
        direcoes = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # cima, baixo, esq, dir
        return [
            (r + dr, c + dc)
            for dr, dc in direcoes
            if self.eh_valido(r + dr, c + dc)
        ]

    def definir_obstaculo(self, linha, coluna, valor=1):
        "Define ou remove um obstáculo na célula."
        self.grade[linha][coluna] = valor

    def exibir(self, inicio=None, fim=None, caminho=None, visitados=None):
        "Exibe o mapa no terminal com símbolos visuais."
        caminho_set   = set(caminho)   if caminho   else set()
        visitados_set = set(visitados) if visitados else set()

        simbolos = {
            'inicio':    ' S ',
            'fim':       ' E ',
            'caminho':   ' ● ',
            'visitado':  ' · ',
            'obstaculo': '███',
            'livre':     '   ',
        }

        print("+" + "---+" * self.colunas)
        for r in range(self.linhas):
            linha_str = "|"
            for c in range(self.colunas):
                pos = (r, c)
                if pos == inicio:
                    cel = simbolos['inicio']
                elif pos == fim:
                    cel = simbolos['fim']
                elif pos in caminho_set:
                    cel = simbolos['caminho']
                elif pos in visitados_set:
                    cel = simbolos['visitado']
                elif self.grade[r][c] == 1:
                    cel = simbolos['obstaculo']
                else:
                    cel = simbolos['livre']
                linha_str += cel + "|"
            print(linha_str)
            print("+" + "---+" * self.colunas)



#  ALGORITMO 1: BFS — Busca em Largura
def bfs(grade, inicio, fim):
    """
    BFS — Breadth-First Search (Busca em Largura)

    Estratégia:
      Explora os nós em camadas, nível por nível.
      Usa uma FILA (FIFO). Garante o caminho com MENOR NÚMERO DE PASSOS.

    Complexidade:
      Tempo : O(V + E)  — V = vértices, E = arestas
      Espaço: O(V)

    Returns:
      caminho   : lista de posições do início ao fim
      visitados : ordem de exploração
      custo     : número de passos
      explorados: total de nós visitados
    """
    fila      = deque([(inicio, [inicio])])   # (posição_atual, caminho_até_aqui)
    visitados = []
    visto     = {inicio}

    while fila:
        atual, caminho = fila.popleft()
        visitados.append(atual)

        if atual == fim:
            return {
                "caminho":    caminho,
                "visitados":  visitados,
                "custo":      len(caminho) - 1,
                "explorados": len(visitados),
                "encontrou":  True,
            }

        for vizinho in grade.vizinhos(atual):
            if vizinho not in visto:
                visto.add(vizinho)
                fila.append((vizinho, caminho + [vizinho]))

    return {"caminho": [], "visitados": visitados,
            "custo": -1, "explorados": len(visitados), "encontrou": False}



#  ALGORITMO 2: DFS — Busca em Profundidade
def dfs(grade, inicio, fim):
    """
    DFS — Depth-First Search (Busca em Profundidade)

    Estratégia:
      Explora o máximo possível em uma direção antes de voltar.
      Usa uma PILHA (LIFO). NÃO garante o caminho mais curto.

    Complexidade:
      Tempo : O(V + E)
      Espaço: O(V)

    Returns: mesmo formato do BFS
    """
    pilha     = [(inicio, [inicio])]  # (posição_atual, caminho_até_aqui)
    visitados = []
    visto     = {inicio}

    while pilha:
        atual, caminho = pilha.pop()   # LIFO — diferença fundamental do BFS
        visitados.append(atual)

        if atual == fim:
            return {
                "caminho":    caminho,
                "visitados":  visitados,
                "custo":      len(caminho) - 1,
                "explorados": len(visitados),
                "encontrou":  True,
            }

        for vizinho in reversed(grade.vizinhos(atual)):
            if vizinho not in visto:
                visto.add(vizinho)
                pilha.append((vizinho, caminho + [vizinho]))

    return {"caminho": [], "visitados": visitados,
            "custo": -1, "explorados": len(visitados), "encontrou": False}


#  ALGORITMO 3: A* — A-Estrela
def a_estrela(grade, inicio, fim, heuristica=heuristica_manhattan):
    """
    A* — A-Star

    Estratégia:
      Combina o custo real g(n) com uma estimativa h(n) até o destino.
      f(n) = g(n) + h(n)
      Usa uma FILA DE PRIORIDADE (heap). Garante o caminho ÓTIMO
      desde que a heurística seja admissível (nunca superestima o custo real).

    Complexidade:
      Tempo : O(E log V)  — depende da heurística
      Espaço: O(V)

    Returns: mesmo formato do BFS
    """
    # heap: (f, g, posição, caminho)
    heap      = [(0 + heuristica(inicio, fim), 0, inicio, [inicio])]
    visitados = []
    custo_g   = {inicio: 0}   # menor custo real encontrado até cada nó

    while heap:
        f, g, atual, caminho = heapq.heappop(heap)
        visitados.append(atual)

        if atual == fim:
            return {
                "caminho":    caminho,
                "visitados":  visitados,
                "custo":      g,
                "explorados": len(visitados),
                "encontrou":  True,
            }

        for vizinho in grade.vizinhos(atual):
            novo_g = g + 1   # custo de mover para um vizinho = 1

            if vizinho not in custo_g or novo_g < custo_g[vizinho]:
                custo_g[vizinho] = novo_g
                h = heuristica(vizinho, fim)
                f = novo_g + h
                heapq.heappush(heap, (f, novo_g, vizinho, caminho + [vizinho]))

    return {"caminho": [], "visitados": visitados,
            "custo": -1, "explorados": len(visitados), "encontrou": False}

#  COMPARADOR — executa os 3 e retorna relatório

def comparar_algoritmos(grade, inicio, fim):
    """Roda BFS, DFS e A* e retorna um dicionário com os resultados."""
    print(f"\n  Início: {inicio}  →  Fim: {fim}")
    print(f"  Grade: {grade.linhas}×{grade.colunas}\n")

    algoritmos = {
        "BFS": bfs,
        "DFS": dfs,
        "A*" : a_estrela,
    }

    resultados = {}
    for nome, func in algoritmos.items():
        res = func(grade, inicio, fim)
        resultados[nome] = res

        status = "✓ Encontrou" if res["encontrou"] else "✗ Não encontrou"
        passos = res["custo"]      if res["encontrou"] else "—"
        expl   = res["explorados"]
        print(f"  [{nome:3s}] {status} | Passos: {str(passos):>4} | Explorados: {expl:>4} nós")

    return resultados
