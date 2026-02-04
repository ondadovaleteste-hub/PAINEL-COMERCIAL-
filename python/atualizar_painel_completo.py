import pandas as pd
import json
import re
from datetime import datetime

CAMINHO_EXCEL = "excel/PEDIDOS ONDA.xlsx"

# ===============================
# LIMPA NÚMEROS BR
# ===============================
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

# ===============================
# CARREGAR EXCEL
# ===============================
def carregar_excel():
    df = pd.read_excel(CAMINHO_EXCEL)
    df.columns = df.columns.str.upper().str.strip()

    obrig = ["DATA", "PEDIDO", "TIPO DE PEDIDO", "VALOR COM IPI", "KG", "TOTAL M2"]
    for c in obrig:
        if c not in df.columns:
            raise Exception(f"❌ Coluna ausente: {c}")

    df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce")
    df = df[df["DATA"].notna()]

    df["VALOR COM IPI"] = df["VALOR COM IPI"].apply(limpar_numero)
    df["KG"] = df["KG"].apply(limpar_numero)
    df["TOTAL M2"] = df["TOTAL M2"].apply(limpar_numero)

    return df

# ===============================
# CÁLCULO PRINCIPAL
# ===============================
def calcular(df):
    # 🔒 APENAS PEDIDOS NORMAIS
    df = df[df["TIPO DE PEDIDO"].str.upper() == "NORMAL"]

    ultima = df["DATA"].max()
    ano = ultima.year
    mes = ultima.month

    df_mes = df[(df["DATA"].dt.year == ano) & (df["DATA"].dt.month == mes)]

    inicio_real = df_mes["DATA"].min()
    inicio_exibicao = datetime(ano, mes, 1)

    df_periodo = df[(df["DATA"] >= inicio_real) & (df["DATA"] <= ultima)]

    # 🔥 CONTAGEM CORRETA
    qtd = df_periodo["PEDIDO"].nunique()

    total_valor = df_periodo["VALOR COM IPI"].sum()
    total_kg = df_periodo["KG"].sum()
    total_m2 = df_periodo["TOTAL M2"].sum()

    preco_kg = round(total_valor / total_kg, 2) if total_kg else 0
    preco_m2 = round(total_valor / total_m2, 2) if total_m2 else 0

    # ===== ANO ANTERIOR =====
    df_ant = df.copy()
    df_ant["DATA"] = df_ant["DATA"] - pd.DateOffset(years=1)

    df_ant_mes = df_ant[
        (df_ant["DATA"] >= inicio_real.replace(year=ano - 1)) &
        (df_ant["DATA"] <= ultima.replace(year=ano - 1))
    ]

    qtd_ant = df_ant_mes["PEDIDO"].nunique()
    total_valor_ant = df_ant_mes["VALOR COM IPI"].sum()
    total_kg_ant = df_ant_mes["KG"].sum()

    ticket_atual = total_valor / qtd if qtd else 0
    ticket_ant = total_valor_ant / qtd_ant if qtd_ant else 0

    return {
        "faturamento": {
            "atual": round(total_valor, 2),
            "ano_anterior": round(total_valor_ant, 2),
            "variacao": ((total_valor / total_valor_ant) - 1) * 100 if total_valor_ant else 0,
            "data": ultima.strftime("%d/%m/%Y"),
            "inicio_mes": inicio_exibicao.strftime("%d/%m/%Y"),
            "data_ano_anterior": ultima.replace(year=ano - 1).strftime("%d/%m/%Y"),
            "inicio_mes_anterior": inicio_exibicao.replace(year=ano - 1).strftime("%d/%m/%Y")
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
        "ticket": {
            "atual": round(ticket_atual, 2),
            "ano_anterior": round(ticket_ant, 2),
            "variacao": ((ticket_atual / ticket_ant) - 1) * 100 if ticket_ant else 0
        },
        "preco": {
            "preco_medio_kg": preco_kg,
            "preco_medio_m2": preco_m2,
            "total_kg": round(total_kg, 2),
            "total_m2": round(total_m2, 2),
            "data": ultima.strftime("%d/%m/%Y")
        }
    }

# ===============================
# SALVAR JSON
# ===============================
def salvar(nome, dados):
    for path in [f"dados/{nome}", f"site/dados/{nome}"]:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)

# ===============================
# EXECUÇÃO
# ===============================
if __name__ == "__main__":
    df = carregar_excel()
    res = calcular(df)

    salvar("kpi_faturamento.json", res["faturamento"])
    salvar("kpi_quantidade_pedidos.json", res["quantidade"])
    salvar("kpi_kg_total.json", res["kg"])
    salvar("kpi_ticket_medio.json", res["ticket"])
    salvar("kpi_preco_medio.json", res["preco"])

    print("=====================================")
    print("Pedidos atuais:", res["quantidade"]["atual"])
    print("Período:", res["faturamento"]["inicio_mes"], "→", res["faturamento"]["data"])
    print("=====================================")
