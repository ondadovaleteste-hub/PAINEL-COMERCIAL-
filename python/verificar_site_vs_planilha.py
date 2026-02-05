import pandas as pd
import re
from datetime import datetime

CAMINHO = "excel/PEDIDOS ONDA.xlsx"

# ================================================================
# LIMPA NÚMEROS BRASILEIROS
# ================================================================
def limpar_numero(v):
    if pd.isna(v):
        return 0.0
    v = str(v).strip()
    v = re.sub(r"[^0-9,.-]", "", v)

    if v in ["", "-", ".", ","]:
        return 0.0

    # 1.234.567,89
    if "." in v and "," in v:
        return float(v.replace(".", "").replace(",", "."))

    # 123,45
    if "," in v:
        return float(v.replace(",", "."))

    try:
        return float(v)
    except:
        return 0.0


# ================================================================
# CARREGAR PLANILHA
# ================================================================
def carregar_excel():
    df = pd.read_excel(CAMINHO)
    df.columns = df.columns.str.upper().str.strip()

    obrig = ["PEDIDO", "DATA", "VALOR COM IPI", "KG", "TOTAL M2"]
    for c in obrig:
        if c not in df.columns:
            raise Exception(f"❌ Coluna ausente: {c}")

    df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce")
    df = df[df["DATA"].notna()]

    df["VALOR COM IPI"] = df["VALOR COM IPI"].apply(limpar_numero)
    df["KG"] = df["KG"].apply(limpar_numero)
    df["TOTAL M2"] = df["TOTAL M2"].apply(limpar_numero)

    df["PEDIDO"] = df["PEDIDO"].astype(str)
    return df


# ================================================================
# REGRA DEFINITIVA DO PERÍODO PARA AMBOS OS ANOS
# ================================================================
def obter_periodo(df):
    hoje = datetime.now()
    ano = hoje.year
    mes = hoje.month

    # ==== Ano Atual ====
    df_atual_mes = df[(df["DATA"].dt.year == ano) & (df["DATA"].dt.month == mes)]

    primeira_real_atual = df_atual_mes["DATA"].min()
    ultima_real_atual = df_atual_mes["DATA"].max()

    # ==== Ano Anterior ====
    df_ant_mes = df[(df["DATA"].dt.year == ano - 1) & (df["DATA"].dt.month == mes)]

    # primeiro dia real igual ao atual, apenas troca ano
    primeira_ant = primeira_real_atual.replace(year=ano - 1)

    # último dia real: só usa se existir pedido nesse dia no ano anterior
    ultima_alvo_ant = ultima_real_atual.replace(year=ano - 1)

    if ultima_alvo_ant in df_ant_mes["DATA"].values:
        ultima_ant = ultima_alvo_ant
    else:
        ultima_ant = df_ant_mes["DATA"].max()

    return {
        "primeira_atual": primeira_real_atual,
        "ultima_atual": ultima_real_atual,
        "primeira_ant": primeira_ant,
        "ultima_ant": ultima_ant
    }


# ================================================================
# CALCULAR OS KPIs
# ================================================================
def calcular(df):
    periodo = obter_periodo(df)

    p_atual_ini = periodo["primeira_atual"]
    p_atual_fim = periodo["ultima_atual"]

    p_ant_ini = periodo["primeira_ant"]
    p_ant_fim = periodo["ultima_ant"]

    # ---------------- ATUAL ----------------
    df_atual = df[(df["DATA"] >= p_atual_ini) & (df["DATA"] <= p_atual_fim)]

    total_atual = df_atual["VALOR COM IPI"].sum()
    kg_atual = df_atual["KG"].sum()
    m2_atual = df_atual["TOTAL M2"].sum()
    qtd_atual = df_atual["PEDIDO"].nunique()

    # ---------------- ANO ANTERIOR ----------------
    df_ant = df[(df["DATA"] >= p_ant_ini) & (df["DATA"] <= p_ant_fim)]

    total_ant = df_ant["VALOR COM IPI"].sum()
    kg_ant = df_ant["KG"].sum()
    m2_ant = df_ant["TOTAL M2"].sum()
    qtd_ant = df_ant["PEDIDO"].nunique()

    # ---------------- TICKET ----------------
    ticket_atual = total_atual / qtd_atual if qtd_atual else 0
    ticket_ant = total_ant / qtd_ant if qtd_ant else 0

    # ---------------- PREÇO MÉDIO ----------------
    preco_kg = total_atual / kg_atual if kg_atual else 0
    preco_m2 = total_atual / m2_atual if m2_atual else 0

    return {
        "periodo": {
            "atual_inicio": p_atual_ini.strftime("%d/%m/%Y"),
            "atual_fim": p_atual_fim.strftime("%d/%m/%Y"),
            "ant_inicio": p_ant_ini.strftime("%d/%m/%Y"),
            "ant_fim": p_ant_fim.strftime("%d/%m/%Y"),
        },
        "atual": {
            "pedidos": qtd_atual,
            "fat": round(total_atual, 2),
            "kg": round(kg_atual, 2),
            "m2": round(m2_atual, 2),
            "ticket": round(ticket_atual, 2),
            "preco_kg": round(preco_kg, 2),
            "preco_m2": round(preco_m2, 2)
        },
        "anterior": {
            "pedidos": qtd_ant,
            "fat": round(total_ant, 2),
            "kg": round(kg_ant, 2),
            "m2": round(m2_ant, 2),
            "ticket": round(ticket_ant, 2)
        }
    }


# ================================================================
# EXECUÇÃO
# ================================================================
if __name__ == "__main__":
    df = carregar_excel()
    r = calcular(df)

    print("\n================== RESULTADOS ==================\n")

    print("📅 ATUAL :", r["periodo"]["atual_inicio"], "→", r["periodo"]["atual_fim"])
    print("📅 ANTERIOR :", r["periodo"]["ant_inicio"], "→", r["periodo"]["ant_fim"])

    print("\n--- ATUAL ---")
    print(r["atual"])

    print("\n--- ANTERIOR ---")
    print(r["anterior"])

    print("\n================================================\n")
