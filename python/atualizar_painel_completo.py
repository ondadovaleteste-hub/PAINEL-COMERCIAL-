import pandas as pd
import json
import re
from datetime import datetime


# ======================================================
# 🔥 FUNÇÃO PARA NORMALIZAR NÚMEROS BRASILEIROS
# ======================================================
def limpar_numero(valor):
    if pd.isna(valor):
        return 0.0

    v = str(valor).strip()
    v = re.sub(r"[^0-9,.-]", "", v)

    if v in ["", "-", ",", ".", ",-", ".-"]:
        return 0.0

    # Formato 1.234.567,89
    if "." in v and "," in v:
        return float(v.replace(".", "").replace(",", "."))

    # Formato 123,45
    if "," in v:
        return float(v.replace(",", "."))

    # Formato 1234 ou 1234.56
    return float(v)


# ======================================================
# 🔥 CARREGAR EXCEL E NORMALIZAR
# ======================================================
def carregar_excel():
    df = pd.read_excel("excel/PEDIDOS ONDA.xlsx")
    df.columns = df.columns.str.upper().str.strip()

    obrig = ["DATA", "VALOR COM IPI", "KG", "TOTAL M2"]
    for c in obrig:
        if c not in df.columns:
            raise Exception(f"❌ Coluna obrigatória ausente: {c}")

    df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce")
    df = df[df["DATA"].notna()]

    df["VALOR COM IPI"] = df["VALOR COM IPI"].apply(limpar_numero)
    df["KG"] = df["KG"].apply(limpar_numero)
    df["TOTAL M2"] = df["TOTAL M2"].apply(limpar_numero)

    return df


# ======================================================
# 🔥 DATA DE REFERÊNCIA (ÚLTIMA DATA NO EXCEL)
# ======================================================
def obter_data_ref(df):
    return df["DATA"].max()


# ======================================================
# 🔥 CALCULAR KPIS PADRÃO
# ======================================================
def calcular_kpis_padrao(df, data_ref):
    ano = data_ref.year
    mes = data_ref.month

    # Filtra SOMENTE mesmo mês e mesmo ano
    df_atual_mes = df[(df["DATA"].dt.year == ano) & (df["DATA"].dt.month == mes)]
    primeira_data_valida = df_atual_mes["DATA"].min()

    # Filtra período correto (EXATO COMO DESEJADO)
    df_atual = df[(df["DATA"] >= primeira_data_valida) & (df["DATA"] <= data_ref)]

    # Ano anterior → mesmo período (dias do mês)
    df_anterior_mes = df[(df["DATA"].dt.year == ano - 1) & (df["DATA"].dt.month == mes)]
    df_anterior = df_anterior_mes[
        (df_anterior_mes["DATA"].dt.day >= primeira_data_valida.day) &
        (df_anterior_mes["DATA"].dt.day <= data_ref.day)
    ]

    # Cálculos
    fat_atual = df_atual["VALOR COM IPI"].sum()
    fat_ant = df_anterior["VALOR COM IPI"].sum()

    kg_atual = df_atual["KG"].sum()
    kg_ant = df_anterior["KG"].sum()

    qtd_atual = len(df_atual)
    qtd_ant = len(df_anterior)

    ticket_atual = fat_atual / qtd_atual if qtd_atual else 0
    ticket_ant = fat_ant / qtd_ant if qtd_ant else 0

    return {
        "faturamento": {
            "atual": round(fat_atual, 2),
            "ano_anterior": round(fat_ant, 2),
            "variacao": ((fat_atual / fat_ant - 1) * 100) if fat_ant else 0,
            "data_atual": f"{primeira_data_valida.strftime('%d/%m/%Y')} até {data_ref.strftime('%d/%m/%Y')}",
            "data_ano_anterior": f"{primeira_data_valida.replace(year=ano-1).strftime('%d/%m/%Y')} até {data_ref.replace(year=ano-1).strftime('%d/%m/%Y')}"
        },
        "kg": {
            "atual": round(kg_atual, 2),
            "ano_anterior": round(kg_ant, 2),
            "variacao": ((kg_atual / kg_ant - 1) * 100) if kg_ant else 0
        },
        "qtd": {
            "atual": qtd_atual,
            "ano_anterior": qtd_ant,
            "variacao": ((qtd_atual / qtd_ant - 1) * 100) if qtd_ant else 0
        },
        "ticket": {
            "atual": round(ticket_atual, 2),
            "ano_anterior": round(ticket_ant, 2),
            "variacao": ((ticket_atual / ticket_ant - 1) * 100) if ticket_ant else 0
        },
        "intervalo": {
            "primeira": primeira_data_valida.strftime('%Y-%m-%d'),
            "ultima": data_ref.strftime('%Y-%m-%d')
        }
    }


# ======================================================
# 🔥 PREÇO MÉDIO – MESMO PERÍODO REAL
# ======================================================
def calcular_preco_medio(df, data_ref):
    ano = data_ref.year
    mes = data_ref.month

    df_mes = df[(df["DATA"].dt.year == ano) & (df["DATA"].dt.month == mes)]
    primeira_data_valida = df_mes["DATA"].min()

    df_periodo = df[(df["DATA"] >= primeira_data_valida) & (df["DATA"] <= data_ref)]

    total_valor = df_periodo["VALOR COM IPI"].sum()
    total_kg = df_periodo["KG"].sum()
    total_m2 = df_periodo["TOTAL M2"].sum()

    preco_kg = round(total_valor / total_kg, 2) if total_kg else 0
    preco_m2 = round(total_valor / total_m2, 2) if total_m2 else 0

    return {
        "preco_medio_kg": preco_kg,
        "preco_medio_m2": preco_m2,
        "total_kg": round(total_kg, 2),
        "total_m2": round(total_m2, 2),
        "data": data_ref.strftime("%d/%m/%Y"),
        "primeira_data": primeira_data_valida.strftime("%d/%m/%Y")
    }


# ======================================================
# 🔥 SALVAR JSON
# ======================================================
def salvar(nome, dados):
    with open(f"dados/{nome}", "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    with open(f"site/dados/{nome}", "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


# ======================================================
# 🔥 EXECUÇÃO
# ======================================================
if __name__ == "__main__":
    df = carregar_excel()
    data_ref = obter_data_ref(df)

    kpis = calcular_kpis_padrao(df, data_ref)
    preco = calcular_preco_medio(df, data_ref)

    salvar("kpi_faturamento.json", kpis["faturamento"])
    salvar("kpi_kg_total.json", kpis["kg"])
    salvar("kpi_quantidade_pedidos.json", kpis["qtd"])
    salvar("kpi_ticket_medio.json", kpis["ticket"])
    salvar("kpi_preco_medio.json", preco)

    print("\n✓ JSON GERADOS COM SUCESSO\n")
