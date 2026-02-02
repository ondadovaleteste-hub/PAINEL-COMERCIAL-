import pandas as pd
import json
from datetime import datetime, timedelta
import os

CAMINHO_EXCEL = "excel/PEDIDOS ONDA.xlsx"
CAMINHO_DADOS = "dados/"
CAMINHO_SITE = "site/dados/"

# ==========================================================
#  CARREGAR EXCEL
# ==========================================================
def carregar_excel():
    if not os.path.exists(CAMINHO_EXCEL):
        raise Exception("❌ Arquivo PEDIDOS ONDA.xlsx não encontrado!")

    df = pd.read_excel(CAMINHO_EXCEL)

    # Normaliza os nomes das colunas
    df.columns = [str(c).strip().upper() for c in df.columns]

    if "DATA" not in df.columns:
        raise Exception("❌ A coluna 'DATA' não foi encontrada no Excel.")

    # Converte DATA
    df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce")

    # Normaliza coluna de valores com IPI
    col_valor = None
    for nome in df.columns:
        if nome.startswith("VALOR COM IPI"):
            col_valor = nome
            break

    if not col_valor:
        raise Exception("❌ A coluna de Valor Com IPI não foi encontrada!")

    df["VALOR_COM_IPI"] = df[col_valor]

    # Normaliza KG
    if "KG" not in df.columns:
        raise Exception("❌ A coluna 'KG' não existe no Excel.")

    df["KG"] = pd.to_numeric(df["KG"], errors="coerce").fillna(0)

    # Normaliza M2
    col_m2 = None
    for nome in df.columns:
        if nome.startswith("TOTAL M2") or nome.startswith("TOTAL M²") or nome.startswith("TOTAL M2".upper()):
            col_m2 = nome
            break

    if not col_m2:
        raise Exception("❌ A coluna de M² não foi encontrada!")

    df["M2"] = pd.to_numeric(df[col_m2], errors="coerce").fillna(0)

    return df


# ==========================================================
# IDENTIFICAR A ÚLTIMA DATA VÁLIDA DO MÊS
# ==========================================================
def obter_ultima_data(df):
    datas_validas = df["DATA"].dropna().sort_values()

    if datas_validas.empty:
        raise Exception("❌ Nenhuma data válida encontrada no Excel.")

    # Data mais recente no arquivo
    ultima = datas_validas.max()

    return ultima


# ==========================================================
# FUNÇÕES DE FILTRO
# ==========================================================
def filtrar_periodo(df, data_final):
    ano = data_final.year
    mes = data_final.month
    dt_ini = datetime(ano, mes, 1)

    return df[(df["DATA"] >= dt_ini) & (df["DATA"] <= data_final)]


def filtrar_periodo_ano_anterior(df, data_final):
    dt_ini = datetime(data_final.year - 1, data_final.month, 1)
    dt_fim = datetime(data_final.year - 1, data_final.month, data_final.day)
    return df[(df["DATA"] >= dt_ini) & (df["DATA"] <= dt_fim)]


# ==========================================================
# CALCULAR KPIS (PADRÃO)
# ==========================================================
def calcular_kpis_padrao(df, data_ref):
    df_atual = filtrar_periodo(df, data_ref)
    df_ant = filtrar_periodo_ano_anterior(df, data_ref)

    soma_atual = df_atual["VALOR_COM_IPI"].sum()
    soma_ant = df_ant["VALOR_COM_IPI"].sum()

    qtd_atual = df_atual["PEDIDO"].nunique()
    qtd_ant = df_ant["PEDIDO"].nunique()

    variacao = ((soma_atual - soma_ant) / soma_ant * 100) if soma_ant > 0 else 0

    dados = {
        "atual": float(soma_atual),
        "ano_anterior": float(soma_ant),
        "variacao": round(float(variacao), 1),
        "data_atual": data_ref.strftime("%d/%m/%Y"),
        "data_ano_anterior": (data_ref.replace(year=data_ref.year -1)).strftime("%d/%m/%Y"),
        "qtd_atual": int(qtd_atual),
        "qtd_ano_anterior": int(qtd_ant),
    }

    return dados


# ==========================================================
# CALCULAR KG, M2, PREÇO MÉDIO
# ==========================================================
def calcular_preco_medio(df, data_ref):
    df_mes = filtrar_periodo(df, data_ref)

    total_kg = df_mes["KG"].sum()
    total_m2 = df_mes["M2"].sum()
    total_valor = df_mes["VALOR_COM_IPI"].sum()

    preco_kg = (total_valor / total_kg) if total_kg > 0 else 0
    preco_m2 = (total_valor / total_m2) if total_m2 > 0 else 0

    dados = {
        "preco_medio_kg": round(float(preco_kg), 2),
        "preco_medio_m2": round(float(preco_m2), 2),
        "total_kg": float(total_kg),
        "total_m2": float(total_m2),
        "data": data_ref.strftime("%d/%m/%Y")
    }

    return dados


# ==========================================================
# SALVAR JSON
# ==========================================================
def salvar_json(nome, conteudo):
    caminho1 = os.path.join(CAMINHO_DADOS, nome)
    caminho2 = os.path.join(CAMINHO_SITE, nome)

    with open(caminho1, "w", encoding="utf-8") as f:
        json.dump(conteudo, f, indent=2, ensure_ascii=False)

    with open(caminho2, "w", encoding="utf-8") as f:
        json.dump(conteudo, f, indent=2, ensure_ascii=False)

    print(f"✔ JSON gerado: {nome}")


# ==========================================================
# EXECUTAR
# ==========================================================
def calcular_kpis():
    df = carregar_excel()

    data_ref = obter_ultima_data(df)

    print(f"📅 Última data encontrada no Excel: {data_ref.date()}")

    # FATURAMENTO
    kpis = calcular_kpis_padrao(df, data_ref)
    salvar_json("kpi_faturamento.json", kpis)

    # KG TOTAL
    df_atual = filtrar_periodo(df, data_ref)
    kg_atual = df_atual["KG"].sum()

    df_ant = filtrar_periodo_ano_anterior(df, data_ref)
    kg_ant = df_ant["KG"].sum()

    variacao_kg = ((kg_atual - kg_ant) / kg_ant * 100) if kg_ant > 0 else 0

    dados_kg = {
        "atual": round(float(kg_atual), 2),
        "ano_anterior": round(float(kg_ant), 2),
        "variacao": round(float(variacao_kg), 1)
    }
    salvar_json("kpi_kg_total.json", dados_kg)

    # QUANTIDADE DE PEDIDOS
    dados_pedidos = {
        "atual": int(df_atual["PEDIDO"].nunique()),
        "ano_anterior": int(df_ant["PEDIDO"].nunique()),
        "variacao": round(
            ((df_atual["PEDIDO"].nunique() - df_ant["PEDIDO"].nunique())
             / df_ant["PEDIDO"].nunique() * 100)
            if df_ant["PEDIDO"].nunique() > 0 else 0, 1)
    }
    salvar_json("kpi_quantidade_pedidos.json", dados_pedidos)

    # TICKET MÉDIO
    ticket_atual = kpis["atual"] / dados_pedidos["atual"] if dados_pedidos["atual"] > 0 else 0
    ticket_ant = kpis["ano_anterior"] / dados_pedidos["ano_anterior"] if dados_pedidos["ano_anterior"] > 0 else 0
    ticket_var = ((ticket_atual - ticket_ant) / ticket_ant * 100) if ticket_ant > 0 else 0

    dados_ticket = {
        "atual": round(float(ticket_atual), 2),
        "ano_anterior": round(float(ticket_ant), 2),
        "variacao": round(float(ticket_var), 1)
    }
    salvar_json("kpi_ticket_medio.json", dados_ticket)

    # PREÇO MÉDIO
    salvar_json("kpi_preco_medio.json", calcular_preco_medio(df, data_ref))


if __name__ == "__main__":
    calcular_kpis()
