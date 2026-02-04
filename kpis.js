function carregarJSON(nome) {
  return fetch("site/dados/" + nome).then(r => r.json());
}

function formatarMoeda(v) {
  return v.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function formatarNumero(v) {
  return v.toLocaleString("pt-BR", { maximumFractionDigits: 2 });
}

function formatarPercentual(v) {
  return v.toFixed(1).replace(".", ",") + "%";
}

function aplicarCorPosNeg(el, valor) {
  el.classList.remove("positivo", "negativo");
  if (valor > 0) el.classList.add("positivo");
  if (valor < 0) el.classList.add("negativo");
}

Promise.all([
  carregarJSON("kpi_faturamento.json"),
  carregarJSON("kpi_quantidade_pedidos.json"),
  carregarJSON("kpi_ticket_medio.json"),
  carregarJSON("kpi_kg_total.json"),
  carregarJSON("kpi_preco_medio.json")
]).then(([fat, qtd, ticket, kg, preco]) => {

  document.getElementById("fatQtdAtual").innerText = qtd.atual + " pedidos";
  document.getElementById("fatValorAtual").innerText = formatarMoeda(fat.atual);
  document.getElementById("fatDataAtual").innerText =
    `de ${fat.inicio_mes} até ${fat.data}`;

  document.getElementById("fatQtdAnterior").innerText =
    qtd.ano_anterior + " pedidos";
  document.getElementById("fatValorAnterior").innerText =
    formatarMoeda(fat.ano_anterior);
  document.getElementById("fatDataAnterior").innerText =
    `de ${fat.inicio_mes_anterior} até ${fat.data_ano_anterior}`;

  const elFatVar = document.getElementById("fatVariacao");
  const pf = fat.variacao >= 0 ? "▲" : "▼";
  elFatVar.innerText =
    `${pf} ${formatarPercentual(Math.abs(fat.variacao))} vs ano anterior`;
  aplicarCorPosNeg(elFatVar, fat.variacao);

  document.getElementById("precoMedioKG").innerText =
    "R$ " + preco.preco_medio_kg.toLocaleString("pt-BR");
  document.getElementById("precoMedioM2").innerText =
    "R$ " + preco.preco_medio_m2.toLocaleString("pt-BR");

  document.getElementById("precoDataKG").innerText =
    "Atualizado até " + preco.data;
  document.getElementById("precoDataM2").innerText =
    "Atualizado até " + preco.data;
});
