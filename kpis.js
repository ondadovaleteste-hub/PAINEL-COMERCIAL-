function carregarJSON(nome) {
  return fetch("site/dados/" + nome)
    .then(r => r.json())
    .catch(() => null);
}

function moeda(v) {
  return v.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function numero(v) {
  return v.toLocaleString("pt-BR", { maximumFractionDigits: 2 });
}

function percentual(v) {
  return Math.abs(v).toFixed(1).replace(".", ",") + "%";
}

function aplicarCor(el, v) {
  el.classList.remove("positivo", "negativo");
  if (v > 0) el.classList.add("positivo");
  if (v < 0) el.classList.add("negativo");
}

Promise.all([
  carregarJSON("kpi_faturamento.json"),
  carregarJSON("kpi_quantidade_pedidos.json"),
  carregarJSON("kpi_ticket_medio.json"),
  carregarJSON("kpi_kg_total.json"),
  carregarJSON("kpi_preco_medio.json")
]).then(([fat, qtd, ticket, kg, preco]) => {

  /* ================= FATURAMENTO ================= */
  document.getElementById("fatQtdAtual").innerText =
    qtd.atual + " pedidos";

  document.getElementById("fatValorAtual").innerText =
    moeda(fat.atual);

  document.getElementById("fatDataAtual").innerText =
    `de ${fat.inicio_mes} até ${fat.data}`;

  document.getElementById("fatQtdAnterior").innerText =
    qtd.ano_anterior + " pedidos";

  document.getElementById("fatValorAnterior").innerText =
    moeda(fat.ano_anterior);

  document.getElementById("fatDataAnterior").innerText =
    `de ${fat.inicio_mes_anterior} até ${fat.data_ano_anterior}`;

  const elFatVar = document.getElementById("fatVariacao");
  elFatVar.innerText =
    `${fat.variacao >= 0 ? "▲" : "▼"} ${percentual(fat.variacao)} vs ano anterior`;
  aplicarCor(elFatVar, fat.variacao);

  /* ================= KG TOTAL ================= */
  document.getElementById("kgQtdAtual").innerText =
    qtd.atual + " pedidos";

  document.getElementById("kgValorAtual").innerText =
    numero(kg.atual) + " kg";

  document.getElementById("kgDataAtual").innerText =
    `de ${fat.inicio_mes} até ${fat.data}`;

  document.getElementById("kgQtdAnterior").innerText =
    qtd.ano_anterior + " pedidos";

  document.getElementById("kgValorAnterior").innerText =
    numero(kg.ano_anterior) + " kg";

  document.getElementById("kgDataAnterior").innerText =
    `de ${fat.inicio_mes_anterior} até ${fat.data_ano_anterior}`;

  const elKgVar = document.getElementById("kgVariacao");
  elKgVar.innerText =
    `${kg.variacao >= 0 ? "▲" : "▼"} ${percentual(kg.variacao)} vs ano anterior`;
  aplicarCor(elKgVar, kg.variacao);

  /* ================= TICKET MÉDIO ================= */
  document.getElementById("ticketAtual").innerText =
    moeda(ticket.atual);

  document.getElementById("ticketAnterior").innerText =
    moeda(ticket.ano_anterior);

  document.getElementById("ticketQtdAtual").innerText =
    qtd.atual + " pedidos no período";

  document.getElementById("ticketQtdAnterior").innerText =
    qtd.ano_anterior + " pedidos no período";

  const elTicketVar = document.getElementById("ticketVariacao");
  elTicketVar.innerText =
    `${ticket.variacao >= 0 ? "▲" : "▼"} ${percentual(ticket.variacao)} vs ano anterior`;
  aplicarCor(elTicketVar, ticket.variacao);

  /* ================= PREÇO MÉDIO ================= */
  if (preco) {
    document.getElementById("precoMedioKG").innerText =
      moeda(preco.preco_medio_kg);

    document.getElementById("precoMedioM2").innerText =
      moeda(preco.preco_medio_m2);

    document.getElementById("precoDataKG").innerText =
      "Atualizado até " + preco.data;

    document.getElementById("precoDataM2").innerText =
      "Atualizado até " + preco.data;
  }
});
