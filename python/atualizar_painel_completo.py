import pandas as pd
import json
import re
from datetime import datetime

CAMINHO_EXCEL = "excel/PEDIDOS ONDA.xlsx"

# ==============================
# LIMPAR NÚMEROS BR
# ==============================
def limpar_numero(valor):
    if pd.isna(valor):
        return 0.0
    v = str(valor).strip()
    v = re.sub(r"[^0-9,.-]", "", v)
    if v in ["", "-", ",", ".", ",-", ".-"]:
        return 0.0
    if "." in v and "," in v:
        return float(v.replace(".", "").replace(",", "."))
    if "," in v:
        return float(v.replace(",", "."))
    return float(v)

# ==============================
# CARREGAR EXCEL
# ==============================
def carregar_excel():
    df = pd.read_excel(CAMINHO_EXCEL)
    df.columns = df.columns.str.strip().str.upper()

    obrig = ["DATA", "PEDIDO", "VALOR COM IPI", "KG", "TOTAL M2"]
    for c in obrig:
        if c not in df.columns:
            raise Exception(f"❌ Coluna ausente: {c}")

    df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce")
    df = df[df["DATA"].notna()]

    df["VALOR COM IPI"] = df["VALOR COM IPI"].apply(limpar_numero)
    df["KG"] = df["KG"].apply(limpar_numero)
    df["TOTAL M2"] = df["TOTAL M2"].apply(limpar_numero)

    return df

# ==============================
# PERÍODO
# ==============================
def obter_periodo(df):
    ultima = df["DATA"].max()
    df_mes = df[(df["DATA"].dt.year == ultima.year) & (df["DATA"].dt.month == ultima.month)]
    primeira_real = df_mes["DATA"].min()
    inicio_mes_exibicao = primeira_real.replace(day=1)
    return primeira_real, ultima, inicio_mes_exibicao

# ==============================
# CALCULAR KPIs
# ==============================
def calcular(df):
    primeira, ultima, inicio_mes = obter_periodo(df)

    df_periodo = df[(df["DATA"] >= primeira) & (df["DATA"] <= ultima)]

    # 🔴 CORREÇÃO PRINCIPAL AQUI
    qtd = df_periodo["PEDIDO"].nunique()

    total_valor = df_periodo["VALOR COM IPI"].sum()
    total_kg = df_periodo["KG"].sum()
    total_m2 = df_periodo["TOTAL M2"].sum()

    preco_kg = round(total_valor / total_kg, 2) if total_kg else 0
    preco_m2 = round(total_valor / total_m2, 2) if total_m2 else 0

    # Ano anterior
    ano_ant = primeira.year - 1
    df_ant = df[
        (df["DATA"] >= primeira.replace(year=ano_ant)) &
        (df["DATA"] <= ultima.replace(year=ano_ant))
    ]

    qtd_ant = df_ant["PEDIDO"].nunique()
    total_valor_ant = df_ant["VALOR COM IPI"].sum()
    total_kg_ant = df_ant["KG"].sum()

    return {
        "faturamento": {
            "atual": round(total_valor, 2),
            "ano_anterior": round(total_valor_ant, 2),
            "variacao": ((total_valor / total_valor_ant) - 1) * 100 if total_valor_ant else 0,
            "inicio_mes": inicio_mes.strftime("%d/%m/%Y"),
            "data": ultima.strftime("%d/%m/%Y"),
            "inicio_mes_anterior": inicio_mes.replace(year=ano_ant).strftime("%d/%m/%Y"),
            "data_ano_anterior": ultima.replace(year=ano_ant).strftime("%d/%m/%Y")
        },
        "quantidade": {
            "atual": qtd,
            "ano_anterior": qtd_ant,
            "variacao": ((qtd / qtd_ant) - 1) * 100 if qtd_ant else 0
        },
        "kg": {
            "atual": round(total_kg, 2),
            "ano_anterior": round(total_kg_ant, 2),
            "variacao": ((total_kg / total_kg_ant) - 1) * 100 if total_kg_ant else 0
        },
        "preco": {
            "preco_medio_kg": preco_kg,
            "preco_medio_m2": preco_m2,
            "total_kg": round(total_kg, 2),
            "total_m2": round(total_m2, 2),
            "data": ultima.strftime("%d/%m/%Y")
        }
    }

# ==============================
# SALVAR JSON
# ==============================
def salvar(nome, dados):
    with open(f"dados/{nome}", "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    with open(f"site/dados/{nome}", "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

# ==============================
# EXECUÇÃO
# ==============================
if __name__ == "__main__":
    df = carregar_excel()
    res = calcular(df)

    salvar("kpi_faturamento.json", res["faturamento"])
    salvar("kpi_quantidade_pedidos.json", res["quantidade"])
    salvar("kpi_kg_total.json", res["kg"])
    salvar("kpi_preco_medio.json", res["preco"])

    print("=====================================")
    print(f"Pedidos atuais: {res['quantidade']['atual']}")
    print(f"Período: {res['faturamento']['inicio_mes']} → {res['faturamento']['data']}")
    print("=====================================")
