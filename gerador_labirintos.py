import random
from algoritmos import Grade

#  UTILITÁRIOS COMUNS

def _grade_cheia(linhas, colunas):
    """Cria uma grade onde TUDO é parede. Base para os geradores."""
    g = Grade(linhas, colunas)
    for r in range(linhas):
        for c in range(colunas):
            g.grade[r][c] = 1   # tudo bloqueado
    return g


def _celulas_internas(linhas, colunas):

    return [(r, c) for r in range(linhas) for c in range(colunas)]


def _pos_mapa(r, c):
    """Converte coordenada de célula para coordenada no mapa expandido."""
    return (r * 2 + 1, c * 2 + 1)


def _parede_entre(r1, c1, r2, c2):
    """Retorna a célula-parede entre duas células adjacentes."""
    return ((r1 + r2 + 1), (c1 + c2 + 1))   # média * 2 + 1... simplificado:
    # Nota: as células diferem em exatamente 1 unidade, então a parede
    # está na posição intermediária no mapa expandido.


def _remover_parede(grade, r1, c1, r2, c2):
    """Abre a parede entre duas células no mapa expandido."""
    pr = r1 + r2 + 1   # = (pos_mapa(r1)[0] + pos_mapa(r2)[0]) // 2
    pc = c1 + c2 + 1
    grade.grade[pr][pc] = 0   # abre a parede
    grade.grade[r1 * 2 + 1][c1 * 2 + 1] = 0   # abre célula 1
    grade.grade[r2 * 2 + 1][c2 * 2 + 1] = 0   # abre célula 2

#  ALGORITMO 1: RECURSIVE BACKTRACKER (DFS)
#  Produz: corredores longos e sinuosos, poucos becos-sem-saída

def gerar_labirinto_dfs(celulas_l, celulas_c, seed=None):

    if seed is not None:
        random.seed(seed)

    L = celulas_l * 2 + 1
    C = celulas_c * 2 + 1
    grade = _grade_cheia(L, C)

    visitado = [[False] * celulas_c for _ in range(celulas_l)]
    pilha    = [(0, 0)]
    visitado[0][0] = True
    grade.grade[1][1] = 0   # abre célula inicial

    direcoes = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while pilha:
        r, c = pilha[-1]

        # Vizinhos não visitados
        vizinhos = []
        for dr, dc in direcoes:
            nr, nc = r + dr, c + dc
            if 0 <= nr < celulas_l and 0 <= nc < celulas_c and not visitado[nr][nc]:
                vizinhos.append((nr, nc))

        if vizinhos:
            nr, nc = random.choice(vizinhos)
            visitado[nr][nc] = True
            _remover_parede(grade, r, c, nr, nc)
            pilha.append((nr, nc))
        else:
            pilha.pop()   # backtrack

    return grade

#  ALGORITMO 2: KRUSKAL ALEATÓRIO
#  Produz: labirintos uniformemente aleatórios, muito ramificados

class _UnionFind:
    """Union-Find (Disjoint Set) para o algoritmo de Kruskal."""
    def __init__(self, n):
        self.pai = list(range(n))
        self.rank = [0] * n

    def encontrar(self, x):
        while self.pai[x] != x:
            self.pai[x] = self.pai[self.pai[x]]
            x = self.pai[x]
        return x

    def unir(self, x, y):
        px, py = self.encontrar(x), self.encontrar(y)
        if px == py:
            return False
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        self.pai[py] = px
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1
        return True


def gerar_labirinto_kruskal(celulas_l, celulas_c, seed=None):

    if seed is not None:
        random.seed(seed)

    L = celulas_l * 2 + 1
    C = celulas_c * 2 + 1
    grade = _grade_cheia(L, C)

    # Abre todas as células (não as paredes)
    for r in range(celulas_l):
        for c in range(celulas_c):
            grade.grade[r * 2 + 1][c * 2 + 1] = 0

    uf = _UnionFind(celulas_l * celulas_c)

    def idx(r, c):
        return r * celulas_c + c

    # Lista todas as paredes horizontais e verticais
    paredes = []
    for r in range(celulas_l):
        for c in range(celulas_c):
            if c + 1 < celulas_c:
                paredes.append((r, c, r, c + 1))   # parede à direita
            if r + 1 < celulas_l:
                paredes.append((r, c, r + 1, c))   # parede abaixo

    random.shuffle(paredes)

    for r1, c1, r2, c2 in paredes:
        if uf.unir(idx(r1, c1), idx(r2, c2)):
            _remover_parede(grade, r1, c1, r2, c2)

    return grade

#  ALGORITMO 3: PRIM ALEATÓRIO
#  Produz: labirintos com árvore mais "arbustiva", muitos becos curtos

def gerar_labirinto_prim(celulas_l, celulas_c, seed=None):

    if seed is not None:
        random.seed(seed)

    L = celulas_l * 2 + 1
    C = celulas_c * 2 + 1
    grade = _grade_cheia(L, C)

    visitado = [[False] * celulas_c for _ in range(celulas_l)]
    direcoes = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def adicionar_vizinhos(r, c, lista_paredes):
        for dr, dc in direcoes:
            nr, nc = r + dr, c + dc
            if 0 <= nr < celulas_l and 0 <= nc < celulas_c and not visitado[nr][nc]:
                lista_paredes.append((r, c, nr, nc))

    # Célula inicial aleatória
    r0, c0 = random.randint(0, celulas_l-1), random.randint(0, celulas_c-1)
    visitado[r0][c0] = True
    grade.grade[r0 * 2 + 1][c0 * 2 + 1] = 0

    paredes = []
    adicionar_vizinhos(r0, c0, paredes)

    while paredes:
        idx = random.randrange(len(paredes))
        r1, c1, r2, c2 = paredes.pop(idx)

        if visitado[r2][c2]:
            continue

        visitado[r2][c2] = True
        _remover_parede(grade, r1, c1, r2, c2)
        adicionar_vizinhos(r2, c2, paredes)

    return grade

#  FÁBRICA: facilita criação por nome

GERADORES = {
    "DFS (Backtracker)": gerar_labirinto_dfs,
    "Kruskal":           gerar_labirinto_kruskal,
    "Prim":              gerar_labirinto_prim,
}

def gerar_labirinto(metodo="DFS (Backtracker)", tamanho=15, seed=None):
    fn    = GERADORES[metodo]
    grade = fn(tamanho, tamanho, seed=seed)

    L, C = grade.linhas, grade.colunas
    # Início no canto superior esquerdo, Fim no canto inferior direito
    inicio = (1, 1)
    fim    = (L - 2, C - 2)

    # Garante que início e fim estejam abertos
    grade.grade[inicio[0]][inicio[1]] = 0
    grade.grade[fim[0]][fim[1]]       = 0

    return grade, inicio, fim
