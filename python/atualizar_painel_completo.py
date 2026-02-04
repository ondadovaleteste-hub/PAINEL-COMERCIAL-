import pandas as pd
import json
import re
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
EXCEL = BASE_DIR / "excel" / "PEDIDOS ONDA.xlsx"
DADOS = BASE_DIR / "dados"
SITE_DADOS = BASE_DIR / "site" / "dados"

DADOS.mkdir(exist_ok=True)
SITE_DADOS.mkdir(exist_ok=True)

# ======================================================
# LIMPA NÚMEROS BR
# ======================================================
def limpar_numero(valor):
    if pd.isna(valor):
        return 0.0
    v = re.sub(r"[^0-9,.-]", "", str(valor))
    if v in ["", "-", ",", "."]:
        return 0.0
    if "." in v and "," in v:
        return float(v.replace(".", "").replace(",", "."))
    if "," in v:
        return float(v.replace(",", "."))
    return float(v)

# ======================================================
# CARREGAR EXCEL
# ======================================================
df = pd.read_excel(EXCEL)
df.columns = df.columns.str.strip().str.upper()

COLS = ["DATA", "PEDIDO", "VALOR COM IPI", "KG", "TOTAL M2"]
for c in COLS:
    if c not in df.columns:
        raise Exception(f"❌ Coluna ausente: {c}")

df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce")
df = df[df["DATA"].notna()]

df["VALOR COM IPI"] = df["VALOR COM IPI"].apply(limpar_numero)
df["KG"] = df["KG"].apply(limpar_numero)
df["TOTAL M2"] = df["TOTAL M2"].apply(limpar_numero)

# ======================================================
# DEFINIR PERÍODO CORRETO
# ======================================================
ultima_data = df["DATA"].max()
ano = ultima_data.year
mes = ultima_data.month

df_mes = df[(df["DATA"].dt.year == ano) & (df["DATA"].dt.month == mes)]
primeira_data = df_mes["DATA"].min()

print("=====================================")
print(f"Pedidos atuais: {df_mes['PEDIDO'].nunique()}")
print(f"Período: {primeira_data.strftime('%d/%m/%Y')} → {ultima_data.strftime('%d/%m/%Y')}")
print("=====================================")

# ======================================================
# FUNÇÃO KPI
# ======================================================
def calcular(df_base, inicio, fim):
    d = df_base[(df_base["DATA"] >= inicio) & (df_base["DATA"] <= fim)]
    return {
        "valor": d["VALOR COM IPI"].sum(),
        "kg": d["KG"].sum(),
        "m2": d["TOTAL M2"].sum(),
        "qtd": d["PEDIDO"].nunique()
    }

# Atual
atual = calcular(df, primeira_data, ultima_data)

# Ano anterior
inicio_ant = primeira_data.replace(year=ano - 1)
fim_ant = ultima_data.replace(year=ano - 1)
anterior = calcular(df, inicio_ant, fim_ant)

# ======================================================
# KPIs
# ======================================================
fat = {
    "atual": round(atual["valor"], 2),
    "ano_anterior": round(anterior["valor"], 2),
    "variacao": ((atual["valor"] / anterior["valor"] - 1) * 100) if anterior["valor"] else 0,
    "data": ultima_data.strftime("%d/%m/%Y"),
    "inicio_mes": primeira_data.strftime("%d/%m/%Y"),
    "data_ano_anterior": fim_ant.strftime("%d/%m/%Y"),
    "inicio_mes_anterior": inicio_ant.strftime("%d/%m/%Y")
}

qtd = {
    "atual": atual["qtd"],
    "ano_anterior": anterior["qtd"],
    "variacao": ((atual["qtd"] / anterior["qtd"] - 1) * 100) if anterior["qtd"] else 0
}

kg = {
    "atual": round(atual["kg"], 2),
    "ano_anterior": round(anterior["kg"], 2),
    "variacao": ((atual["kg"] / anterior["kg"] - 1) * 100) if anterior["kg"] else 0
}

ticket = {
    "atual": round(atual["valor"] / atual["qtd"], 2) if atual["qtd"] else 0,
    "ano_anterior": round(anterior["valor"] / anterior["qtd"], 2) if anterior["qtd"] else 0,
    "variacao": 0
}

preco = {
    "preco_medio_kg": round(atual["valor"] / atual["kg"], 2) if atual["kg"] else 0,
    "preco_medio_m2": round(atual["valor"] / atual["m2"], 2) if atual["m2"] else 0,
    "total_kg": round(atual["kg"], 2),
    "total_m2": round(atual["m2"], 2),
    "data": ultima_data.strftime("%d/%m/%Y")
}

# ======================================================
# SALVAR JSON
# ======================================================
def salvar(nome, dados):
    for pasta in [DADOS, SITE_DADOS]:
        with open(pasta / nome, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)

salvar("kpi_faturamento.json", fat)
salvar("kpi_quantidade_pedidos.json", qtd)
salvar("kpi_kg_total.json", kg)
salvar("kpi_ticket_medio.json", ticket)
salvar("kpi_preco_medio.json", preco)

print("✓ JSON gerados corretamente")
print("📅 Última data encontrada:", ultima_data)
