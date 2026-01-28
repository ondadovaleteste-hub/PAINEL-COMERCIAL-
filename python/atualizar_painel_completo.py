import pandas as pd
import json
from datetime import datetime
from pathlib import Path
import numpy as np

print("=====================================")
print("Atualizando painel a partir do Excel")
print("=====================================\n")

# ======================================================
# CAMINHOS
# ======================================================
BASE_DIR = Path(__file__).resolve().parents[1]
ARQ_EXCEL = BASE_DIR / "excel" / "PEDIDOS ONDA.xlsx"
PASTA_DADOS = BASE_DIR / "dados"   # <<< AQUI É A CHAVE
PASTA_DADOS.mkdir(parents=True, exist_ok=True)

# ======================================================
# DATA / PERÍODO
# ======================================================
HOJE = datetime.now()
DATA_INICIO = HOJE.replace(day=1)
ANO_ANTERIOR = HOJE.year - 1

# ======================================================
# LEITURA
# ======================================================
df = pd.read_excel(ARQ_EXCEL)
print(f"📄 Linhas lidas: {len(df)}")

COL_TIPO = "Tipo de pedido"
COL_DATA = "Data"
COL_VALOR = "Valor Com IPI"

print(f"🧩 Coluna TIPO: {COL_TIPO}")
print(f"🧩 Coluna DATA: {COL_DATA}")
print(f"🧩 Coluna VALOR: {COL_VALOR}")

# ======================================================
# FILTRO NORMAL
# ======================================================
df[COL_TIPO] = (
    df[COL_TIPO].astype(str).str.strip().str.lower()
)
df = df[df[COL_TIPO] == "normal"]
print(f"✅ Pedidos NORMAL: {len(df)}")

# ======================================================
# DATA
# ======================================================
df["DATA_OK"] = pd.to_datetime(df[COL_DATA], errors="coerce", dayfirst=True)
df = df.dropna(subset=["DATA_OK"])

# ======================================================
# VALOR COM IPI
# ======================================================
def conv(v):
    if pd.isna(v): return 0.0
    if isinstance(v, (int, float)): return float(v)
    return float(str(v).replace(".", "").replace(",", "."))

df["VALOR_OK"] = df[COL_VALOR].apply(conv)

# ======================================================
# PERÍODO
# ======================================================
df_atual = df[(df["DATA_OK"] >= DATA_INICIO) & (df["DATA_OK"] <= HOJE)]
df_ant = df[
    (df["DATA_OK"] >= DATA_INICIO.replace(year=ANO_ANTERIOR)) &
    (df["DATA_OK"] <= HOJE.replace(year=ANO_ANTERIOR))
]

# ======================================================
# KPIs
# ======================================================
fat_atual = round(df_atual["VALOR_OK"].sum(), 2)
fat_ant = round(df_ant["VALOR_OK"].sum(), 2)

qtd_atual = len(df_atual)
qtd_ant = len(df_ant)

ticket = round(fat_atual / qtd_atual, 2) if qtd_atual else 0
variacao = round(((fat_atual - fat_ant) / fat_ant) * 100, 1) if fat_ant else None

# ======================================================
# JSONs (RAIZ /dados)
# ======================================================
json.dump(
    {
        "atual": fat_atual,
        "ano_anterior": fat_ant,
        "variacao": variacao,
        "data_fim": HOJE.strftime("%d/%m/%Y")
    },
    open(PASTA_DADOS / "kpi_faturamento.json", "w", encoding="utf-8"),
    ensure_ascii=False, indent=2
)

json.dump(
    {
        "atual": qtd_atual,
        "ano_anterior": qtd_ant
    },
    open(PASTA_DADOS / "kpi_quantidade_pedidos.json", "w", encoding="utf-8"),
    ensure_ascii=False, indent=2
)

json.dump(
    {
        "valor": ticket
    },
    open(PASTA_DADOS / "kpi_ticket_medio.json", "w", encoding="utf-8"),
    ensure_ascii=False, indent=2
)

print("✅ Atualização concluída com sucesso")
print(f"📦 Pedidos: {qtd_atual}")
print(f"💰 Faturamento com IPI: {fat_atual:,.2f}")
