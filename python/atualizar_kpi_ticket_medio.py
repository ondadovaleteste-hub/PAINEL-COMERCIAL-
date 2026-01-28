import pandas as pd
import json
from datetime import datetime
from pathlib import Path
import numpy as np

print("🔄 Atualizando KPI de ticket médio (PEDIDOS ÚNICOS)...")

# ======================================================
# CAMINHOS
# ======================================================
BASE_DIR = Path(__file__).resolve().parents[1]
ARQ_EXCEL = BASE_DIR / "excel" / "PEDIDOS ONDA.xlsx"
PASTA_DADOS = BASE_DIR / "site" / "dados"
PASTA_DADOS.mkdir(exist_ok=True)

# ======================================================
# COLUNAS (AJUSTADAS AO SEU EXCEL)
# ======================================================
COL_PEDIDO = 1   # Coluna B
COL_TIPO = 3     # Tipo
COL_DATA = 4     # Data
COL_VALOR = 7    # Valor total

# ======================================================
# DATA DE REFERÊNCIA
# ======================================================
HOJE = datetime(2026, 1, 28)
ANO_ANTERIOR = HOJE.year - 1

# ======================================================
# LEITURA
# ======================================================
df = pd.read_excel(ARQ_EXCEL)
print(f"📄 Linhas lidas: {len(df)}")

# ======================================================
# FILTRAR NORMAL
# ======================================================
df = df[df.iloc[:, COL_TIPO].astype(str).str.upper().str.strip() == "NORMAL"]
print(f"✅ NORMAL: {len(df)} linhas")

# ======================================================
# DATA
# ======================================================
df["DATA_OK"] = pd.to_datetime(
    df.iloc[:, COL_DATA],
    errors="coerce",
    dayfirst=True
)
df = df.dropna(subset=["DATA_OK"])

# ======================================================
# VALOR
# ======================================================
def converter_valor(v):
    if pd.isna(v):
        return 0.0
    if isinstance(v, (int, float, np.integer, np.floating)):
        return float(v)
    v = str(v).replace(".", "").replace(",", ".")
    try:
        return float(v)
    except:
        return 0.0

df["VALOR_OK"] = df.iloc[:, COL_VALOR].apply(converter_valor)

# ======================================================
# PERÍODOS
# ======================================================
df_atual = df[
    (df["DATA_OK"].dt.year == HOJE.year) &
    (df["DATA_OK"] <= HOJE)
]

df_anterior = df[
    (df["DATA_OK"].dt.year == ANO_ANTERIOR) &
    (df["DATA_OK"] <= HOJE.replace(year=ANO_ANTERIOR))
]

# ======================================================
# DEDUPLICAR POR PEDIDO (CHAVE!)
# ======================================================
df_atual = df_atual.drop_duplicates(subset=df.columns[COL_PEDIDO])
df_anterior = df_anterior.drop_duplicates(subset=df.columns[COL_PEDIDO])

# ======================================================
# CÁLCULOS CORRETOS
# ======================================================
faturamento_atual = df_atual["VALOR_OK"].sum()
qtd_atual = len(df_atual)

faturamento_anterior = df_anterior["VALOR_OK"].sum()
qtd_anterior = len(df_anterior)

ticket_atual = faturamento_atual / qtd_atual if qtd_atual > 0 else 0
ticket_anterior = faturamento_anterior / qtd_anterior if qtd_anterior > 0 else 0

variacao = (
    ((ticket_atual - ticket_anterior) / ticket_anterior) * 100
    if ticket_anterior > 0 else None
)

# ======================================================
# JSON
# ======================================================
dados = {
    "atual": round(ticket_atual, 2),
    "ano_anterior": round(ticket_anterior, 2),
    "variacao": round(variacao, 1) if variacao is not None else None
}

with open(PASTA_DADOS / "kpi_ticket_medio.json", "w", encoding="utf-8") as f:
    json.dump(dados, f, ensure_ascii=False, indent=2)

# ======================================================
# LOG
# ======================================================
print("✅ KPI ticket médio gerado com sucesso")
print(f"🎟️ Ticket médio atual: {ticket_atual:,.2f}")
print(f"🎟️ Ticket médio ano anterior: {ticket_anterior:,.2f}")
print(f"📈 Variação: {dados['variacao'] if dados['variacao'] else '--'}%")
