function carregarJSON(nome) {
  return fetch("site/dados/" + nome)
    .then(r => r.json())
    .catch(() => null);
}

function formatarMoeda(v) {
  return (v ?? 0).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function formatarNumero(v, casas = 2) {
  return (v ?? 0).toLocaleString("pt-BR", { maximumFractionDigits: casas });
}

function formatarPercentual(v) {
  const n = Number(v ?? 0);
  return n.toFixed(1).replace(".", ",") + "%";
}

function aplicarCorPosNeg(el, valor) {
  el.classList.remove("positivo", "negativo");
  if (valor > 0) el.classList.add("positivo");
  if (valor < 0) el.classList.add("negativo");
}

function obterMesDeDataBR(dataBR) {
  // "05/02/2026" -> 2
  if (!dataBR || typeof dataBR !== "string" || dataBR.length < 10) return null;
  const mes = Number(dataBR.substring(3, 5));
  return Number.isFinite(mes) ? mes : null;
}

Promise.all([
  carregarJSON("kpi_faturamento.json"),
  carregarJSON("kpi_quantidade_pedidos.json"),
  carregarJSON("kpi_ticket_medio.json"),
  carregarJSON("kpi_kg_total.json"),
  carregarJSON("kpi_preco_medio.json")
]).then(([fat, qtd, ticket, kg, precoRaw]) => {
  if (!fat || !qtd || !ticket || !kg || !precoRaw) {
    console.error("❌ Falha ao carregar algum JSON:", { fat, qtd, ticket, kg, precoRaw });
    return;
  }

  // ======================================================
  // NORMALIZAÇÃO DO PREÇO MÉDIO (ACEITA FORMATO NOVO E ANTIGO)
  // - Novo: { atual: {...}, ano_anterior: {...} }
  // - Antigo: { preco_medio_kg, preco_medio_m2, ... }
  // ======================================================
  const preco = {
    atual: precoRaw.atual ? precoRaw.atual : precoRaw,
    ano_anterior: precoRaw.ano_anterior ? precoRaw.ano_anterior : null
  };

  /* ================= SLIDE 1 – FATURAMENTO ================= */
  document.getElementById("fatQtdAtual").innerText = (qtd.atual ?? "--") + " pedidos";
  document.getElementById("fatValorAtual").innerText = formatarMoeda(fat.atual);
  document.getElementById("fatDataAtual").innerText =
    "de " + (fat.inicio_mes ?? "--") + " até " + (fat.data_atual ?? "--");

  document.getElementById("fatQtdAnterior").innerText = (qtd.ano_anterior ?? "--") + " pedidos";
  document.getElementById("fatValorAnterior").innerText = formatarMoeda(fat.ano_anterior);
  document.getElementById("fatDataAnterior").innerText =
    "de " + (fat.inicio_mes_anterior ?? "--") + " até " + (fat.data_ano_anterior ?? "--");

  const elFatVar = document.getElementById("fatVariacao");
  const pfFat = (fat.variacao ?? 0) >= 0 ? "▲" : "▼";
  elFatVar.innerText = `${pfFat} ${formatarPercentual(Math.abs(fat.variacao ?? 0))} vs ano anterior`;
  aplicarCorPosNeg(elFatVar, fat.variacao ?? 0);

  /* ===== META FATURAMENTO ===== */
  const METAS = {
    1: { kg: 100000, fat: 1324746.56 },
    2: { kg: 100000, fat: 1324746.56 },
    3: { kg: 120000, fat: 1598757.69 },
    4: { kg: 130000, fat: 1910459.23 },
    5: { kg: 130000, fat: 1892998.21 },
    6: { kg: 130000, fat: 1892995.74 },
    7: { kg: 150000, fat: 2199365.46 },
    8: { kg: 150000, fat: 2199350.47 },
    9: { kg: 150000, fat: 2199340.46 },
    10: { kg: 150000, fat: 2199335.81 },
    11: { kg: 150000, fat: 2199360.62 },
    12: { kg: 98000, fat: 1409516.02 }
  };

  const mes = obterMesDeDataBR(fat.data_atual);
  if (mes && METAS[mes]) {
    const metaFat = METAS[mes].fat;
    const metaFatPerc = (fat.atual / metaFat) * 100;

    document.getElementById("fatMetaValor").innerText = "Meta mês: " + formatarMoeda(metaFat);

    const elFatMetaPerc = document.getElementById("fatMetaPerc");
    elFatMetaPerc.innerText = "🎯 " + metaFatPerc.toFixed(1).replace(".", ",") + "% da meta";

    elFatMetaPerc.classList.remove("meta-ok", "meta-atencao", "meta-ruim");
    if (metaFatPerc >= 100) elFatMetaPerc.classList.add("meta-ok");
    else if (metaFatPerc >= 80) elFatMetaPerc.classList.add("meta-atencao");
    else elFatMetaPerc.classList.add("meta-ruim");
  } else {
    document.getElementById("fatMetaValor").innerText = "Meta mês: --";
    document.getElementById("fatMetaPerc").innerText = "🎯 -- % da meta";
  }

  /* ================= SLIDE 2 – KG TOTAL ================= */
  document.getElementById("kgQtdAtual").innerText = (qtd.atual ?? "--") + " pedidos";
  document.getElementById("kgValorAtual").innerText = formatarNumero(kg.atual, 0) + " kg";
  document.getElementById("kgDataAtual").innerText =
    "de " + (fat.inicio_mes ?? "--") + " até " + (fat.data_atual ?? "--");

  document.getElementById("kgQtdAnterior").innerText = (qtd.ano_anterior ?? "--") + " pedidos";
  document.getElementById("kgValorAnterior").innerText = formatarNumero(kg.ano_anterior, 0) + " kg";
  document.getElementById("kgDataAnterior").innerText =
    "de " + (fat.inicio_mes_anterior ?? "--") + " até " + (fat.data_ano_anterior ?? "--");

  const elKgVar = document.getElementById("kgVariacao");
  const pfKG = (kg.variacao ?? 0) >= 0 ? "▲" : "▼";
  elKgVar.innerText = `${pfKG} ${formatarPercentual(Math.abs(kg.variacao ?? 0))} vs ano anterior`;
  aplicarCorPosNeg(elKgVar, kg.variacao ?? 0);

  /* ===== META KG (AGORA SEMPRE APARECE) ===== */
  if (mes && METAS[mes]) {
    const metaKG = METAS[mes].kg;
    const metaKGperc = (kg.atual / metaKG) * 100;

    document.getElementById("kgMetaValor").innerText = "Meta mês: " + formatarNumero(metaKG, 0) + " kg";
    document.getElementById("kgMetaPerc").innerText = "🎯 " + metaKGperc.toFixed(1).replace(".", ",") + "% da meta";

    const elKgMetaPerc = document.getElementById("kgMetaPerc");
    elKgMetaPerc.classList.remove("meta-ok", "meta-atencao", "meta-ruim");
    if (metaKGperc >= 100) elKgMetaPerc.classList.add("meta-ok");
    else if (metaKGperc >= 80) elKgMetaPerc.classList.add("meta-atencao");
    else elKgMetaPerc.classList.add("meta-ruim");
  } else {
    document.getElementById("kgMetaValor").innerText = "Meta mês: --";
    document.getElementById("kgMetaPerc").innerText = "🎯 -- % da meta";
  }

  /* ================= SLIDE 3 – TICKET MÉDIO ================= */
  document.getElementById("ticketAtual").innerText = formatarMoeda(ticket.atual);
  document.getElementById("ticketAnterior").innerText = formatarMoeda(ticket.ano_anterior);

  document.getElementById("ticketQtdAtual").innerText = (qtd.atual ?? "--") + " pedidos no período";
  document.getElementById("ticketQtdAnterior").innerText = (qtd.ano_anterior ?? "--") + " pedidos no período";

  const elTicketVar = document.getElementById("ticketVariacao");
  const pfT = (ticket.variacao ?? 0) >= 0 ? "▲" : "▼";
  elTicketVar.innerText = `${pfT} ${formatarPercentual(Math.abs(ticket.variacao ?? 0))} vs ano anterior`;
  aplicarCorPosNeg(elTicketVar, ticket.variacao ?? 0);

  /* ================= SLIDE 4 – PREÇO MÉDIO (ATUAL + ANO ANTERIOR) ================= */
  // ATUAL
  if (preco.atual) {
    document.getElementById("precoMedioKG").innerText =
      "R$ " + (preco.atual.preco_medio_kg ?? 0).toLocaleString("pt-BR");

    document.getElementById("precoMedioM2").innerText =
      "R$ " + (preco.atual.preco_medio_m2 ?? 0).toLocaleString("pt-BR");

    document.getElementById("precoDataKG").innerText =
      "Atualizado até " + (preco.atual.data ?? "--");

    document.getElementById("precoDataM2").innerText =
      "Atualizado até " + (preco.atual.data ?? "--");
  }

  // ANO ANTERIOR (SE EXISTIR NO JSON)
  const elKgAnt = document.getElementById("precoMedioKGant");
  const elM2Ant = document.getElementById("precoMedioM2ant");
  const elDataKgAnt = document.getElementById("precoDataKGant");
  const elDataM2Ant = document.getElementById("precoDataM2ant");

  if (preco.ano_anterior && elKgAnt && elM2Ant && elDataKgAnt && elDataM2Ant) {
    elKgAnt.innerText =
      "R$ " + (preco.ano_anterior.preco_medio_kg ?? 0).toLocaleString("pt-BR");

    elM2Ant.innerText =
      "R$ " + (preco.ano_anterior.preco_medio_m2 ?? 0).toLocaleString("pt-BR");

    elDataKgAnt.innerText =
      "Atualizado até " + (preco.ano_anterior.data ?? "--");

    elDataM2Ant.innerText =
      "Atualizado até " + (preco.ano_anterior.data ?? "--");
  }
});
