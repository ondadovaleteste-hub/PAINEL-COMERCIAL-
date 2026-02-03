import pandas as pd
import json
import re
from datetime import datetime


# ======================================================
# 🔥 LIMPA NÚMEROS BRASILEIROS (DEFINITIVO)
# ======================================================
def limpar_numero(valor):
    if pd.isna(valor):
        return 0.0

    v = str(valor).strip()
    v = re.sub(r"[^0-9,.-]", "", v)

    if v in ["", "-", ",", ".", ",-", ".-"]:
        return 0.0

    if "." in v and "," in v:
        v = v.replace(".", "")
        v = v.replace(",", ".")
        try:
            return float(v)
        except:
            return 0.0

    if "," in v:
        v = v.replace(",", ".")
        try:
            return float(v)
        except:
            return 0.0

    if "." in v:
        partes = v.split(".")
        if len(partes[-1]) == 3:
            v = v.replace(".", "")
        try:
            return float(v)
        except:
            return 0.0

    try:
        return float(v)
    except:
        return 0.0


# ======================================================
# 📌 CARREGA PLANILHA
# ======================================================
def carregar_excel():
    df = pd.read_excel("excel/PEDIDOS ONDA.xlsx")

    df.columns = df.columns.str.strip().str.upper()

    obrig = ["DATA", "VALOR COM IPI", "KG", "TOTAL M2"]
    for c in obrig:
        if c not in df.columns:
            raise Exception(f"❌ Coluna obrigatória não encontrada: {c}")

    df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce")

    df["VALOR COM IPI"] = df["VALOR COM IPI"].apply(limpar_numero)
    df["KG"] = df["KG"].apply(limpar_numero)
    df["TOTAL M2"] = df["TOTAL M2"].apply(limpar_numero)

    return df


# ======================================================
# 📌 PEGA PRIMEIRO DIA EXISTENTE DO MÊS
# ======================================================
def obter_primeiro_dia_mes(df, ano, mes):
    df_mes = df[(df["DATA"].dt.year == ano) & (df["DATA"].dt.month == mes)]
    if df_mes.empty:
        return None
    return df_mes["DATA"].min()


# ======================================================
# 📌 KPIs OFICIAIS
# ======================================================
def calcular_kpis(df, data_ref):
    ano = data_ref.year
    mes = data_ref.month

    # Primeiro dia REAL existente no mês
    primeiro_dia = obter_primeiro_dia_mes(df, ano, mes)
    if primeiro_dia is None:
        raise Exception("❌ Nenhum dia válido encontrado para o mês.")

    # Usa esse mesmo dia para filtrar ano anterior
    dia = primeiro_dia.day

    atual = df[
        (df["DATA"].dt.year == ano) &
        (df["DATA"].dt.month == mes) &
        (df["DATA"].dt.day <= dia)
    ]

    anterior = df[
        (df["DATA"].dt.year == ano - 1) &
        (df["DATA"].dt.month == mes) &
        (df["DATA"].dt.day <= dia)
    ]

    fat_atual = atual["VALOR COM IPI"].sum()
    fat_ant = anterior["VALOR COM IPI"].sum()
    kg_atual = atual["KG"].sum()
    kg_ant = anterior["KG"].sum()
    m2_atual = atual["TOTAL M2"].sum()
    m2_ant = anterior["TOTAL M2"].sum()

    qtd_atual = len(atual)
    qtd_ant = len(anterior)

    return {
        "faturamento": {
            "atual": round(fat_atual, 2),
            "ano_anterior": round(fat_ant, 2)
        },
        "kg": {
            "atual": round(kg_atual, 2),
            "ano_anterior": round(kg_ant, 2)
        },
        "m2": {
            "atual": round(m2_atual, 2),
            "ano_anterior": round(m2_ant, 2)
        },
        "qtd": {
            "atual": qtd_atual,
            "ano_anterior": qtd_ant
        },
        "dia_filtrado": dia
    }


# ======================================================
# 📌 PREÇO MÉDIO (USANDO O MESMO DIA DE CORTE)
# ======================================================
def calcular_preco_medio(df, ano, mes, dia):
    df_mes = df[
        (df["DATA"].dt.year == ano) &
        (df["DATA"].dt.month == mes) &
        (df["DATA"].dt.day <= dia)
    ]

    total_valor = df_mes["VALOR COM IPI"].sum()
    total_kg = df_mes["KG"].sum()
    total_m2 = df_mes["TOTAL M2"].sum()

    preco_kg = round(total_valor / total_kg, 2) if total_kg else 0
    preco_m2 = round(total_valor / total_m2, 2) if total_m2 else 0

    return {
        "preco_medio_kg": preco_kg,
        "preco_medio_m2": preco_m2,
        "total_kg": round(total_kg, 2),
        "total_m2": round(total_m2, 2)
    }


# ======================================================
# SALVAR JSON
# ======================================================
def salvar(nome, dados):
    with open(f"dados/{nome}", "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    with open(f"site/dados/{nome}", "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


# ======================================================
# EXECUÇÃO
# ======================================================
if __name__ == "__main__":
    df = carregar_excel()
    data_ref = df["DATA"].max()
    print("📅 Última data encontrada:", data_ref)

    kpis = calcular_kpis(df, data_ref)
    dia = kpis["dia_filtrado"]
    ano = data_ref.year
    mes = data_ref.month

    preco = calcular_preco_medio(df, ano, mes, dia)

    salvar("kpi_faturamento.json", kpis["faturamento"])
    salvar("kpi_kg_total.json", kpis["kg"])
    salvar("kpi_quantidade_pedidos.json", kpis["qtd"])
    salvar("kpi_preco_medio.json", preco)

    print("\n✓ JSON gerados com sucesso.")
