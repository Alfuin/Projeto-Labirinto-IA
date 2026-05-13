import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import time, random

from algoritmos import Grade, bfs, dfs, a_estrela
from gerador_labirintos import gerar_labirinto, GERADORES

st.set_page_config(page_title="Busca de Caminhos", page_icon="🗺️", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@300;400;600&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;background-color:#080D14;color:#E2E8F0}
.main{background-color:#080D14} h1{font-family:'Space Mono',monospace;color:#3A86FF}
h2,h3{color:#94A3B8;font-weight:300}
.stButton>button{background:linear-gradient(135deg,#3A86FF,#2563EB);color:white;border:none;border-radius:8px;font-family:'Space Mono',monospace;font-weight:700;padding:0.5rem 1.5rem;width:100%}
.mc{background:#1E293B;border:1px solid #334155;border-radius:12px;padding:16px;text-align:center}
.mv{font-size:1.8rem;font-weight:700;font-family:'Space Mono',monospace}
.ml{font-size:.7rem;color:#64748B;text-transform:uppercase;letter-spacing:1px;margin-top:2px}
</style>""", unsafe_allow_html=True)

st.title("🗺️ Busca de Caminhos em Mapas")
st.markdown("**BFS · DFS · A\*** com Labirintos Gerados Algoritmicamente | IA — UNIP")
st.divider()

COR={"parede":"#060A12","livre":"#1E293B","visitado":"#2D4A6B","caminho":"#3A86FF","inicio":"#06D6A0","fim":"#FF006E","bg":"#080D14"}
CORES_ALGO={"BFS":"#3A86FF","DFS":"#FF006E","A*":"#06D6A0"}
NOMES_ALGO={"BFS":"BFS — Largura","DFS":"DFS — Profundidade","A*":"A* — A-Estrela"}

def hex2rgb(h):
    h=h.lstrip("#"); return tuple(int(h[i:i+2],16)/255 for i in(0,2,4))

def render_grade(ax,grade,inicio,fim,resultado=None,titulo=""):
    L,C=grade.linhas,grade.colunas; img=np.zeros((L,C,3))
    cam=set(resultado["caminho"]) if resultado else set()
    vis=set(resultado["visitados"]) if resultado else set()
    for r in range(L):
        for c in range(C):
            p=(r,c)
            if grade.grade[r][c]==1: cor=hex2rgb(COR["parede"])
            elif p in cam: cor=hex2rgb(COR["caminho"])
            elif p in vis: cor=hex2rgb(COR["visitado"])
            else: cor=hex2rgb(COR["livre"])
            img[r][c]=cor
    ax.imshow(img,interpolation='nearest')
    ms=max(3,8-L//20)
    ax.plot(inicio[1],inicio[0],'o',color=COR["inicio"],markersize=ms,markeredgecolor='white',markeredgewidth=1,zorder=5)
    ax.plot(fim[1],fim[0],'*',color=COR["fim"],markersize=ms+3,markeredgecolor='white',markeredgewidth=1,zorder=5)
    if resultado and resultado["caminho"]:
        xs=[p[1] for p in resultado["caminho"]]; ys=[p[0] for p in resultado["caminho"]]
        ax.plot(xs,ys,'-',color=COR["caminho"],linewidth=1.5,alpha=0.9,zorder=4)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_visible(False)
    ax.set_title(titulo,color="white",fontsize=8,fontweight="bold",pad=5)
    ax.set_facecolor(COR["parede"])

with st.sidebar:
    st.header("⚙️ Configurações")
    modo=st.radio("Modo de Mapa",["🏛️ Labirinto Gerado","🎲 Grade Aleatória"])
    st.divider()
    if "Labirinto" in modo:
        gerador=st.selectbox("Algoritmo de Geração",list(GERADORES.keys()))
        tamanho=st.slider("Complexidade (células)",5,50,20)
        st.caption(f"Mapa resultante: {tamanho*2+1}×{tamanho*2+1}")
    else:
        tamanho=st.slider("Tamanho da Grade (N×N)",8,40,15)
        densidade=st.slider("Obstáculos (%)",5,45,28)
    seed=st.number_input("Seed aleatória",0,9999,42)
    st.divider()
    gerar=st.button("🎲 Gerar Mapa",use_container_width=True)
    buscar=st.button("🚀 Executar Busca",use_container_width=True)
    st.divider()
    st.markdown("**Geradores:**\n- **DFS** → corredores longos\n- **Kruskal** → uniforme, denso\n- **Prim** → ramificado, radial")

if "grade_obj" not in st.session_state or gerar:
    if "Labirinto" in modo:
        grade,inicio,fim=gerar_labirinto(gerador,tamanho,seed=int(seed))
    else:
        random.seed(int(seed)); grade=Grade(tamanho,tamanho)
        inicio,fim=(0,0),(tamanho-1,tamanho-1)
        for r in range(tamanho):
            for c in range(tamanho):
                if (r,c) not in [inicio,fim] and random.random()<densidade/100:
                    grade.grade[r][c]=1
    st.session_state.update({"grade_obj":grade,"inicio":inicio,"fim":fim,"resultados":None})

grade=st.session_state["grade_obj"]; inicio=st.session_state["inicio"]; fim=st.session_state["fim"]

if buscar:
    res={}
    for nome,fn in [("BFS",bfs),("DFS",dfs),("A*",a_estrela)]:
        t0=time.perf_counter(); r=fn(grade,inicio,fim); ms=(time.perf_counter()-t0)*1000
        res[nome]={**r,"tempo_ms":ms}
    st.session_state["resultados"]=res

resultados=st.session_state.get("resultados")

if resultados:
    st.subheader("📊 Métricas Comparativas")
    cols=st.columns(3)
    for col,(algo,res) in zip(cols,resultados.items()):
        passos=res["custo"] if res["encontrou"] else "—"; cor=CORES_ALGO[algo]; status="✅" if res["encontrou"] else "❌"
        with col:
            st.markdown(f"""<div class="mc" style="border-color:{cor}55">
              <div style="color:{cor};font-family:'Space Mono',monospace;font-size:.9rem;font-weight:700;margin-bottom:10px">{status} {NOMES_ALGO[algo]}</div>
              <div style="display:flex;justify-content:space-around">
                <div><div class="mv" style="color:{cor}">{passos}</div><div class="ml">Passos</div></div>
                <div><div class="mv" style="color:{cor}">{res['explorados']}</div><div class="ml">Explorados</div></div>
                <div><div class="mv" style="color:{cor}">{res['tempo_ms']:.1f}</div><div class="ml">ms</div></div>
              </div></div>""",unsafe_allow_html=True)
    st.divider()

st.subheader("🗺️ Visualização")
fig,axes=plt.subplots(1,3,figsize=(16,6)); fig.patch.set_facecolor(COR["bg"])
if resultados:
    for ax,(algo,res) in zip(axes,resultados.items()):
        passos=res["custo"] if res["encontrou"] else "—"
        render_grade(ax,grade,inicio,fim,res,f"{NOMES_ALGO[algo]}\n{passos} passos | {res['explorados']} explorados | {res['tempo_ms']:.1f}ms")
else:
    render_grade(axes[0],grade,inicio,fim,titulo=f"Mapa {grade.linhas}×{grade.colunas} — Clique em 'Executar Busca'")
    for ax in axes[1:]: ax.axis('off')

legenda=[mpatches.Patch(color=COR[k],label=v) for k,v in [("inicio","Início"),("fim","Fim"),("caminho","Caminho"),("visitado","Explorado"),("parede","Parede")]]
fig.legend(handles=legenda,loc="lower center",ncol=5,framealpha=0.15,facecolor="#1E293B",edgecolor="#334155",labelcolor="white",fontsize=9,bbox_to_anchor=(0.5,-0.05))
plt.tight_layout(); st.pyplot(fig,use_container_width=True); plt.close()

st.divider()
st.caption("UNIP — IA | BFS · DFS · A* | Geradores: DFS Backtracker · Kruskal · Prim")
