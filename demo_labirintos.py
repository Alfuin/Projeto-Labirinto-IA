import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os
import time

from algoritmos import bfs, dfs, a_estrela
from gerador_labirintos import gerar_labirinto, GERADORES

os.makedirs("graficos", exist_ok=True)

# Paleta
COR = {
    "parede":    "#060A12",
    "livre":     "#1E293B",
    "visitado":  "#2D4A6B",
    "caminho":   "#3A86FF",
    "inicio":    "#06D6A0",
    "fim":       "#FF006E",
    "bg":        "#080D14",
}

CORES_ALGO = {"BFS": "#3A86FF", "DFS": "#FF006E", "A*": "#06D6A0"}
NOMES_ALGO = {"BFS": "BFS — Largura", "DFS": "DFS — Profundidade", "A*": "A* — A-Estrela"}

def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16)/255 for i in (0, 2, 4))

def renderizar_grade(ax, grade, inicio, fim, resultado=None, titulo=""):
    L, C = grade.linhas, grade.colunas
    img  = np.zeros((L, C, 3))

    cam = set(resultado["caminho"])   if resultado else set()
    vis = set(resultado["visitados"]) if resultado else set()

    for r in range(L):
        for c in range(C):
            pos = (r, c)
            if grade.grade[r][c] == 1:
                cor = hex2rgb(COR["parede"])
            elif pos in cam:
                cor = hex2rgb(COR["caminho"])
            elif pos in vis:
                cor = hex2rgb(COR["visitado"])
            else:
                cor = hex2rgb(COR["livre"])
            img[r][c] = cor

    ax.imshow(img, interpolation='nearest')
    ax.plot(inicio[1], inicio[0], 'o', color=COR["inicio"],
            markersize=6, markeredgecolor='white', markeredgewidth=1, zorder=5)
    ax.plot(fim[1], fim[0], '*', color=COR["fim"],
            markersize=9, markeredgecolor='white', markeredgewidth=1, zorder=5)

    if resultado and resultado["caminho"]:
        xs = [p[1] for p in resultado["caminho"]]
        ys = [p[0] for p in resultado["caminho"]]
        ax.plot(xs, ys, '-', color=COR["caminho"], linewidth=1.5, alpha=0.9, zorder=4)

    ax.set_xticks([]); ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_title(titulo, color="white", fontsize=8, fontweight="bold", pad=5)
    ax.set_facecolor(COR["parede"])


def rodar_cenario(nome_gerador, tamanho, seed):
    """Gera labirinto, roda os 3 algoritmos, plota e imprime resultados."""
    grade, inicio, fim = gerar_labirinto(nome_gerador, tamanho, seed=seed)
    L, C = grade.linhas, grade.colunas

    print(f"\n  Gerador : {nome_gerador}")
    print(f"  Mapa    : {L}×{C}  (células: {tamanho}×{tamanho})")
    print(f"  Início  : {inicio}  →  Fim: {fim}\n")

    resultados = {}
    for nome, fn in [("BFS", bfs), ("DFS", dfs), ("A*", a_estrela)]:
        t0  = time.perf_counter()
        res = fn(grade, inicio, fim)
        ms  = (time.perf_counter() - t0) * 1000
        resultados[nome] = {**res, "tempo_ms": ms}

        status = "✓ Encontrou" if res["encontrou"] else "✗ Não encontrou"
        passos = res["custo"]      if res["encontrou"] else "—"
        expl   = res["explorados"]
        print(f"  [{nome:3s}] {status} | Passos: {str(passos):>5} | "
              f"Explorados: {expl:>5} | {ms:.2f}ms")

    return grade, inicio, fim, resultados


def gerar_figura_labirinto(nome_gerador, tamanho, seed=42):
    grade, inicio, fim, resultados = rodar_cenario(nome_gerador, tamanho, seed)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.patch.set_facecolor(COR["bg"])

    titulo_fig = (f"Gerador: {nome_gerador}  |  "
                  f"Labirinto {grade.linhas}×{grade.colunas}  |  "
                  f"Seed: {seed}")
    fig.suptitle(titulo_fig, fontsize=11, color="white",
                 fontweight="bold", y=1.01)

    for ax, (nome, res) in zip(axes, resultados.items()):
        passos = res["custo"] if res["encontrou"] else "—"
        titulo = (f"{NOMES_ALGO[nome]}\n"
                  f"Passos: {passos}  |  Explorados: {res['explorados']}  |  {res['tempo_ms']:.1f}ms")
        renderizar_grade(ax, grade, inicio, fim, res, titulo)

    legenda = [
        mpatches.Patch(color=COR["inicio"],   label="Início (S)"),
        mpatches.Patch(color=COR["fim"],      label="Fim (E)"),
        mpatches.Patch(color=COR["caminho"],  label="Caminho encontrado"),
        mpatches.Patch(color=COR["visitado"], label="Células exploradas"),
        mpatches.Patch(color=COR["parede"],   label="Parede"),
    ]
    fig.legend(handles=legenda, loc="lower center", ncol=5,
               framealpha=0.15, facecolor="#1E293B", edgecolor="#334155",
               labelcolor="white", fontsize=8, bbox_to_anchor=(0.5, -0.06))

    plt.tight_layout()
    nome_arq = nome_gerador.lower().replace(" ", "_").replace("(", "").replace(")", "")
    caminho  = f"graficos/labirinto_{nome_arq}_{tamanho}x{tamanho}.png"
    plt.savefig(caminho, dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close()
    print(f"\n  ✓ Salvo: {caminho}")
    return caminho, resultados


def gerar_figura_comparativa_geradores(tamanho=20, seed=42):
    """
    Figura 3×3: cada linha é um gerador, cada coluna é um algoritmo.
    Mostra como o tipo de labirinto afeta cada algoritmo.
    """
    geradores = list(GERADORES.keys())
    algos     = ["BFS", "DFS", "A*"]

    fig, axes = plt.subplots(3, 3, figsize=(15, 15))
    fig.patch.set_facecolor(COR["bg"])
    fig.suptitle(
        f"Comparação: 3 Geradores × 3 Algoritmos  |  "
        f"Labirinto {tamanho*2+1}×{tamanho*2+1}  |  Seed {seed}",
        fontsize=13, color="white", fontweight="bold", y=1.01
    )

    todos = {}
    for i, gen in enumerate(geradores):
        grade, inicio, fim = gerar_labirinto(gen, tamanho, seed=seed)
        resultados = {}
        for algo, fn in [("BFS", bfs), ("DFS", dfs), ("A*", a_estrela)]:
            resultados[algo] = fn(grade, inicio, fim)

        todos[gen] = resultados

        for j, algo in enumerate(algos):
            ax  = axes[i][j]
            res = resultados[algo]
            passos = res["custo"] if res["encontrou"] else "—"
            titulo = (f"{gen}\n{NOMES_ALGO[algo]}\n"
                      f"Passos: {passos} | Explorados: {res['explorados']}")
            renderizar_grade(ax, grade, inicio, fim, res, titulo)

    # Rótulos das colunas
    for j, algo in enumerate(algos):
        axes[0][j].set_title(
            f"{'─'*8} {NOMES_ALGO[algo]} {'─'*8}\n" + axes[0][j].get_title(),
            color=list(CORES_ALGO.values())[j], fontsize=9, fontweight="bold"
        )

    legenda = [
        mpatches.Patch(color=COR["inicio"],   label="Início"),
        mpatches.Patch(color=COR["fim"],      label="Fim"),
        mpatches.Patch(color=COR["caminho"],  label="Caminho"),
        mpatches.Patch(color=COR["visitado"], label="Explorado"),
        mpatches.Patch(color=COR["parede"],   label="Parede"),
    ]
    fig.legend(handles=legenda, loc="lower center", ncol=5,
               framealpha=0.15, facecolor="#1E293B", edgecolor="#334155",
               labelcolor="white", fontsize=9, bbox_to_anchor=(0.5, -0.02))

    plt.tight_layout()
    caminho = f"graficos/comparacao_geradores_{tamanho}x{tamanho}.png"
    plt.savefig(caminho, dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close()
    print(f"  ✓ Salvo: {caminho}")
    return caminho, todos


def gerar_figura_escalabilidade():
    """Testa os algoritmos em labirintos de tamanhos crescentes."""
    tamanhos = [10, 20, 35, 50]
    algos    = ["BFS", "DFS", "A*"]
    fns      = {"BFS": bfs, "DFS": dfs, "A*": a_estrela}

    dados = {a: {"passos": [], "explorados": [], "tempo": []} for a in algos}

    print("\n  Testando escalabilidade...")
    for tam in tamanhos:
        grade, inicio, fim = gerar_labirinto("DFS (Backtracker)", tam, seed=42)
        print(f"    Grade {grade.linhas}×{grade.colunas}", end="")
        for algo in algos:
            t0  = time.perf_counter()
            res = fns[algo](grade, inicio, fim)
            ms  = (time.perf_counter() - t0) * 1000
            dados[algo]["passos"].append(res["custo"] if res["encontrou"] else 0)
            dados[algo]["explorados"].append(res["explorados"])
            dados[algo]["tempo"].append(ms)
            print(f"  {algo}✓", end="")
        print()

    eixo_x = [t * 2 + 1 for t in tamanhos]   # tamanho real do mapa

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.patch.set_facecolor(COR["bg"])
    fig.suptitle("Escalabilidade dos Algoritmos (Gerador DFS, Seed 42)",
                 fontsize=12, color="white", fontweight="bold")

    titulos = ["Passos no Caminho", "Nós Explorados", "Tempo (ms)"]
    chaves  = ["passos", "explorados", "tempo"]

    for ax, titulo, chave in zip(axes, titulos, chaves):
        ax.set_facecolor("#1E293B")
        for algo in algos:
            ax.plot(eixo_x, dados[algo][chave],
                    marker='o', linewidth=2, markersize=6,
                    color=CORES_ALGO[algo], label=algo)
        ax.set_title(titulo, color="white", fontweight="bold", pad=8)
        ax.set_xlabel("Tamanho do Mapa (N×N)", color="#94A3B8")
        ax.tick_params(colors="#94A3B8")
        ax.legend(facecolor="#0F172A", edgecolor="#334155",
                  labelcolor="white", fontsize=9)
        for spine in ax.spines.values():
            spine.set_edgecolor("#334155")
        ax.yaxis.grid(True, color="#334155", linestyle="--", alpha=0.5)
        ax.set_axisbelow(True)
        ax.set_xticks(eixo_x)
        ax.set_xticklabels([f"{x}×{x}" for x in eixo_x], color="#94A3B8", fontsize=8)

    plt.tight_layout()
    caminho = "graficos/escalabilidade.png"
    plt.savefig(caminho, dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close()
    print(f"\n  ✓ Salvo: {caminho}")


#  EXECUÇÃO PRINCIPAL

def main():
    print("=" * 60)
    print("  LABIRINTOS COMPLEXOS — BFS, DFS e A*")
    print("  Inteligência Artificial — UNIP")
    print("=" * 60)

    # 1. Um labirinto por gerador (tamanho médio)
    for gerador in GERADORES:
        print(f"\n{'─'*55}")
        print(f"  GERADOR: {gerador.upper()}")
        print(f"{'─'*55}")
        gerar_figura_labirinto(gerador, tamanho=20, seed=42)

    # 2. Figura 3×3 comparativa (labirinto grande)
    print(f"\n{'─'*55}")
    print("  FIGURA COMPARATIVA 3×3 (tamanho 30)")
    print(f"{'─'*55}\n")
    gerar_figura_comparativa_geradores(tamanho=30, seed=7)

    # 3. Escalabilidade
    print(f"\n{'─'*55}")
    print("  ESCALABILIDADE")
    print(f"{'─'*55}")
    gerar_figura_escalabilidade()

    print(f"\n{'='*60}")
    print("  Todos os gráficos salvos em: graficos/")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
