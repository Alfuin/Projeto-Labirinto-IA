# Busca de Caminhos em Mapas — BFS, DFS e A*

Trabalho de ponto extra — Disciplina de Inteligência Artificial
**UNIP — Universidade Paulista**

---

## Descrição

Implementação e comparação de três algoritmos clássicos de busca em IA aplicados à
navegação em grades 2D com obstáculos:

| Algoritmo | Estratégia | Garante ótimo? |
|-----------|-----------|---------------|
| **BFS** (Busca em Largura) | Fila — explora nível a nível | ✅ Sim |
| **DFS** (Busca em Profundidade) | Pilha — explora até o fundo | ❌ Não |
| **A\*** (A-Estrela) | Heap + heurística Manhattan | ✅ Sim |

---

## Como Executar

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Rodar o demo de labirintos principal (gera gráficos)
```bash
python demo_labirintos.py
```

### 3. Rodar o app interativo
```bash
python -m streamlit run app.py
```

---

## Estrutura

```
busca-caminhos/
├── algoritmos.py                # BFS, DFS, A* + classe Grade
├── demo_labirintos.py           # Demo com 3 cenários + gráficos
├── app.py                       # Interface interativa (Streamlit)
├── requirements.txt
├── README.md
└── graficos/                    # Gerado automaticamente
```

---

## Conceitos Aplicados

- **BFS**: usa `collections.deque` como fila FIFO
- **DFS**: usa lista Python como pilha LIFO
- **A\***: usa `heapq` como fila de prioridade; f(n) = g(n) + h(n)
- **Heurística**: distância de Manhattan |Δrow| + |Δcol|

---

## Grupo

> Mateus da Silva Lopes - R0497H2
> Felipe Martins Frateschi - R108EG6
> Eduardo Ferreira Silva dos Santos - R024FI0
> Eduardo Okabe Sato Scarparo - G9934B5
