async function carregarJSON(caminho) {
    const resposta = await fetch(caminho + '?v=' + new Date().getTime());
    if (!resposta.ok) {
        throw new Error(`Erro ao carregar ${caminho}`);
    }
    return resposta.json();
}

async function atualizarKPIs() {
    try {
        const faturamento = await carregarJSON('dados/kpi_faturamento.json');
        const pedidos = await carregarJSON('dados/kpi_quantidade_pedidos.json');
        const ticket = await carregarJSON('dados/kpi_ticket_medio.json');

        document.getElementById('fat_atual').innerText =
            faturamento.atual.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });

        document.getElementById('fat_variacao').innerText =
            faturamento.variacao !== null ? `${faturamento.variacao}%` : '-';

        document.getElementById('qtd_pedidos').innerText = pedidos.atual;

        document.getElementById('ticket_medio').innerText =
            ticket.valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });

    } catch (erro) {
        console.error('Erro ao atualizar KPIs:', erro);
    }
}

atualizarKPIs();
setInterval(atualizarKPIs, 60000); // atualiza a cada 1 minuto
