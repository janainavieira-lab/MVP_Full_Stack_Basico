/* ═══════════════════════════════════════════════════════
   MarmitApp — Lógica da SPA
   
   Conceitos aplicados:
   - Fetch API com async/await (chamadas à API REST)
   - Hash routing (navegação SPA sem recarregar)
   - Manipulação do DOM (renderização dinâmica de cards)
   - Modularização: funções com responsabilidade única
   
   Todas as 12 rotas da API são chamadas neste arquivo.
═══════════════════════════════════════════════════════ */

'use strict';

/* ─── CONFIGURAÇÃO ──────────────────────────────────── */

// Endereço base da API. Altere a porta se necessário.
// Esta constante centraliza a URL — se a porta mudar,
// basta alterar aqui, sem buscar em todo o arquivo.
const API_URL = 'http://localhost:5000';

// Mapa de cores por nome de categoria.
// Usado para definir as bordas coloridas dos cards (assinatura visual).
const CORES_CATEGORIA = {
    'carboidrato': '#F6B93B',
    'proteína':    '#E55039',
    'proteina':    '#E55039',
    'vegetal':     '#00C9A7',
    'prato pronto':'#A29BFE',
    '_default':    '#74B9FF'
};


/* ─── UTILITÁRIOS ──────────────────────────────────── */

/**
 * Exibe uma notificação toast no canto da tela.
 * @param {string} mensagem - Texto a exibir
 * @param {string} tipo - 'sucesso' | 'erro'
 */
function mostrarToast(mensagem, tipo = 'sucesso') {
    const toast = document.getElementById('toast');
    toast.textContent = mensagem;
    toast.className = `toast ${tipo}`;
    // Remove a classe 'hidden' para exibir
    setTimeout(() => toast.classList.add('hidden'), 3000);
}

/**
 * Retorna a cor associada a uma categoria pelo nome.
 * Normaliza o texto para comparação (minúsculas, sem acento parcial).
 */
function getCorCategoria(nomeCategoria) {
    if (!nomeCategoria) return CORES_CATEGORIA['_default'];
    const chave = nomeCategoria.toLowerCase();
    // Verifica se alguma chave do mapa está contida no nome
    for (const [k, cor] of Object.entries(CORES_CATEGORIA)) {
        if (k !== '_default' && chave.includes(k)) return cor;
    }
    return CORES_CATEGORIA['_default'];
}

/**
 * Formata uma string de data ISO ('2026-06-30') para 'dd/mm/aaaa'.
 * Trata o fuso horário convertendo para local antes de formatar.
 */
function formatarData(isoStr) {
    if (!isoStr) return '—';
    // Adiciona 'T12:00' para evitar problema de fuso que pode
    // fazer a data aparecer como o dia anterior em UTC-3
    const d = new Date(isoStr + 'T12:00');
    return d.toLocaleDateString('pt-BR');
}

/**
 * Calcula a diferença em dias entre hoje e uma data futura.
 * Retorna null se a data não foi informada.
 */
function diasAteVencer(isoStr) {
    if (!isoStr) return null;
    const hoje = new Date();
    const vencimento = new Date(isoStr + 'T12:00');
    const diff = Math.ceil((vencimento - hoje) / (1000 * 60 * 60 * 24));
    return diff;
}

/**
 * Mostra ou esconde um painel de formulário pelo seu id.
 * Princípio: o botão não precisa saber o estado atual do painel —
 * o toggle decide automaticamente.
 */
function toggleForm(idFormulario) {
    const form = document.getElementById(idFormulario);
    form.classList.toggle('hidden');
}


/* ─── HASH ROUTING (navegação SPA) ──────────────────── */

/**
 * Conceito: Hash Routing
 * 
 * A URL '#categorias' diz ao JS qual seção mostrar,
 * sem enviar nenhuma requisição ao servidor.
 * O navegador emite o evento 'hashchange' toda vez
 * que o hash muda — o JS escuta e reage.
 */
function mostrarSecao(hash) {
    // Remove o '#' se presente
    const secao = hash.replace('#', '') || 'categorias';

    // Oculta todas as seções
    document.querySelectorAll('.app-section').forEach(s => s.classList.add('hidden'));

    // Exibe apenas a seção correspondente ao hash
    const alvo = document.getElementById(`section-${secao}`);
    if (alvo) alvo.classList.remove('hidden');

    // Atualiza estado visual dos links da sidebar
    document.querySelectorAll('.sidebar-nav .nav-link').forEach(link => {
        link.classList.toggle('active', link.dataset.section === secao);
    });

    // Carrega dados da seção que acabou de aparecer
    switch (secao) {
        case 'categorias': carregarCategorias();  break;
        case 'porcoes':    carregarPorcoes();     break;
        case 'refeicoes':  carregarRefeicoes();   break;
        case 'sugestao':   /* aguarda clique */   break;
    }
}

// Escuta toda troca de hash na URL
window.addEventListener('hashchange', () => mostrarSecao(window.location.hash));


/* ─── STATUS DA API ─────────────────────────────────── */

/**
 * Verifica se a API está respondendo ao fazer um GET /categorias.
 * Atualiza o indicador visual na sidebar.
 * 
 * Conceito: GET /categorias — Rota 2 da API.
 */
async function verificarStatusAPI() {
    const dot  = document.getElementById('status-dot');
    const text = document.getElementById('status-text');
    try {
        const resp = await fetch(`${API_URL}/categorias`);
        if (resp.ok) {
            dot.className  = 'status-dot online';
            text.textContent = 'API conectada';
        } else {
            throw new Error();
        }
    } catch {
        dot.className  = 'status-dot offline';
        text.textContent = 'API offline';
    }
}


/* ═══════════════════════════════════════════════════════
   SEÇÃO: CATEGORIAS
═══════════════════════════════════════════════════════ */

/**
 * GET /categorias — Rota 2
 * Busca todas as categorias e renderiza os cards.
 */
async function carregarCategorias() {
    try {
        const resp = await fetch(`${API_URL}/categorias`);
        const categorias = await resp.json();
        renderizarCategorias(categorias);
        atualizarFiltrosCategoria(categorias);   // sincroniza filtros na seção de porções
        atualizarSelectCategorias(categorias);   // sincroniza dropdown no form de porções
    } catch {
        mostrarToast('Erro ao carregar categorias. Verifique se a API está rodando.', 'erro');
    }
}

/**
 * POST /categorias — Rota 1
 * Lê o campo de texto, envia para a API e recarrega a lista.
 * 
 * Conceito: fetch com método POST requer:
 * - method: 'POST'
 * - headers: informa ao servidor que o corpo é JSON
 * - body: o dado serializado como string JSON
 */
async function cadastrarCategoria() {
    const input = document.getElementById('input-categoria-nome');
    const nome  = input.value.trim();
    if (!nome) { mostrarToast('Digite um nome para a categoria', 'erro'); return; }

    try {
        const resp = await fetch(`${API_URL}/categorias`, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ nome })
        });

        if (resp.status === 409) {
            mostrarToast('Categoria já existe', 'erro'); return;
        }
        if (!resp.ok) throw new Error();

        input.value = '';
        toggleForm('form-categoria');
        mostrarToast(`Categoria "${nome}" criada!`);
        carregarCategorias();
    } catch {
        mostrarToast('Erro ao criar categoria', 'erro');
    }
}

/** Renderiza os cards de categoria no DOM */
function renderizarCategorias(categorias) {
    const container = document.getElementById('lista-categorias');

    if (!categorias.length) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">🏷️</div>
                <p>Nenhuma categoria cadastrada ainda.<br>Crie a primeira para começar!</p>
            </div>`;
        return;
    }

    // Constrói o HTML de cada card concatenando strings.
    // Em frameworks como React isso seria JSX, mas em JS puro
    // usamos template literals (crase + ${}) para HTML dinâmico.
    container.innerHTML = categorias.map(cat => {
        const cor = getCorCategoria(cat.nome);
        return `
            <div class="categoria-card" style="border-left-color: ${cor}">
                <span class="categoria-card-nome">${cat.nome}</span>
                <span class="badge-categoria" style="background:${cor}">${cat.nome}</span>
            </div>`;
    }).join('');
}

/** Atualiza os chips de filtro na seção de porções */
function atualizarFiltrosCategoria(categorias) {
    const container = document.getElementById('filtros-categoria');
    const chipTodas = `<button class="chip active" onclick="filtrarPorcoes(null, this)">Todas</button>`;
    const chips = categorias.map(cat => {
        const cor = getCorCategoria(cat.nome);
        return `<button class="chip"
                    style="border-color:${cor}; color:${cor}"
                    onclick="filtrarPorcoes(${cat.id}, this)">${cat.nome}</button>`;
    }).join('');
    container.innerHTML = chipTodas + chips;
}

/** Atualiza o <select> de categorias no formulário de porções */
function atualizarSelectCategorias(categorias) {
    const select = document.getElementById('porcao-categoria');
    select.innerHTML = '<option value="">Selecione...</option>' +
        categorias.map(c => `<option value="${c.id}">${c.nome}</option>`).join('');
}


/* ═══════════════════════════════════════════════════════
   SEÇÃO: PORÇÕES
═══════════════════════════════════════════════════════ */

/** Variável de estado: guarda o filtro de categoria ativo */
let filtroCategoriaSelecionada = null;

/**
 * GET /porcoes e GET /porcoes?categoria_id=N — Rota 4
 * Carrega porções com filtro opcional por categoria.
 */
async function carregarPorcoes(categoriaId = null) {
    const url = categoriaId
        ? `${API_URL}/porcoes?categoria_id=${categoriaId}`
        : `${API_URL}/porcoes`;
    try {
        const resp   = await fetch(url);
        const porcoes = await resp.json();
        renderizarPorcoes(porcoes);
    } catch {
        mostrarToast('Erro ao carregar porções', 'erro');
    }
}

/**
 * Aplica o chip de filtro clicado.
 * @param {number|null} categoriaId - null = mostrar todas
 * @param {HTMLElement} chip - botão clicado (para marcar como active)
 */
function filtrarPorcoes(categoriaId, chip) {
    filtroCategoriaSelecionada = categoriaId;
    // Atualiza visual dos chips
    document.querySelectorAll('.filter-chips .chip').forEach(c => c.classList.remove('active'));
    chip.classList.add('active');
    carregarPorcoes(categoriaId);
}

/**
 * POST /porcoes — Rota 3
 * Coleta os dados do formulário e envia para a API.
 */
async function cadastrarPorcao() {
    const nome       = document.getElementById('porcao-nome').value.trim();
    const catId      = document.getElementById('porcao-categoria').value;
    const preparo    = document.getElementById('porcao-preparo').value.trim();
    const quantidade = document.getElementById('porcao-quantidade').value;
    const dataPreparo = document.getElementById('porcao-data-preparo').value;
    const validade   = document.getElementById('porcao-validade').value;

    if (!nome || !catId) {
        mostrarToast('Nome e categoria são obrigatórios', 'erro'); return;
    }

    // Monta o objeto JSON apenas com campos preenchidos
    const payload = {
        nome,
        categoria_id: parseInt(catId),
        quantidade_disponivel: parseInt(quantidade) || 1
    };
    if (preparo)     payload.tipo_preparo      = preparo;
    if (dataPreparo) payload.data_preparo      = dataPreparo;
    if (validade)    payload.validade_estimada = validade;

    try {
        const resp = await fetch(`${API_URL}/porcoes`, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify(payload)
        });
        if (!resp.ok) throw new Error();

        // Limpa o formulário
        ['porcao-nome','porcao-preparo','porcao-data-preparo','porcao-validade'].forEach(id => {
            document.getElementById(id).value = '';
        });
        document.getElementById('porcao-quantidade').value = '1';
        document.getElementById('porcao-categoria').value  = '';

        toggleForm('form-porcao');
        mostrarToast(`Porção "${nome}" cadastrada!`);
        carregarPorcoes(filtroCategoriaSelecionada);
    } catch {
        mostrarToast('Erro ao cadastrar porção', 'erro');
    }
}

/**
 * DELETE /porcoes/<id> — Rota 7
 * Solicita confirmação antes de deletar.
 */
async function deletarPorcao(id, nome) {
    if (!confirm(`Remover a porção "${nome}"?`)) return;

    try {
        const resp = await fetch(`${API_URL}/porcoes/${id}`, { method: 'DELETE' });
        if (!resp.ok) throw new Error();
        mostrarToast(`"${nome}" removida com sucesso`);
        carregarPorcoes(filtroCategoriaSelecionada);
    } catch {
        mostrarToast('Erro ao remover porção', 'erro');
    }
}

/**
 * GET /porcoes/<id> — Rota 5
 * Busca os dados atuais de uma porção e preenche o modal de edição.
 */
async function abrirModalEdicao(id) {
    try {
        const resp   = await fetch(`${API_URL}/porcoes/${id}`);
        const porcao = await resp.json();

        // Preenche os campos do modal com os dados vindos da API
        document.getElementById('edit-id').value        = porcao.id;
        document.getElementById('edit-nome').value      = porcao.nome;
        document.getElementById('edit-preparo').value   = porcao.tipo_preparo || '';
        document.getElementById('edit-quantidade').value = porcao.quantidade_disponivel;
        document.getElementById('edit-validade').value  = porcao.validade_estimada || '';

        document.getElementById('modal-overlay').classList.remove('hidden');
    } catch {
        mostrarToast('Erro ao buscar dados da porção', 'erro');
    }
}

function fecharModal() {
    document.getElementById('modal-overlay').classList.add('hidden');
}

/**
 * PUT /porcoes/<id> — Rota 6
 * Envia as alterações do modal de edição para a API.
 */
async function salvarEdicao() {
    const id       = document.getElementById('edit-id').value;
    const nome     = document.getElementById('edit-nome').value.trim();
    const preparo  = document.getElementById('edit-preparo').value.trim();
    const qtd      = document.getElementById('edit-quantidade').value;
    const validade = document.getElementById('edit-validade').value;

    if (!nome) { mostrarToast('O nome não pode ficar vazio', 'erro'); return; }

    const payload = {
        nome,
        tipo_preparo:          preparo     || null,
        quantidade_disponivel: parseInt(qtd),
        validade_estimada:     validade     || null
    };

    try {
        const resp = await fetch(`${API_URL}/porcoes/${id}`, {
            method:  'PUT',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify(payload)
        });
        if (!resp.ok) throw new Error();

        fecharModal();
        mostrarToast('Porção atualizada com sucesso!');
        carregarPorcoes(filtroCategoriaSelecionada);
    } catch {
        mostrarToast('Erro ao atualizar porção', 'erro');
    }
}

/** Renderiza os cards de porção no DOM */
function renderizarPorcoes(porcoes) {
    const container = document.getElementById('lista-porcoes');

    if (!porcoes.length) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">🍱</div>
                <p>Nenhuma porção encontrada.<br>Cadastre a primeira!</p>
            </div>`;
        return;
    }

    container.innerHTML = porcoes.map(p => {
        const cor   = getCorCategoria(p.categoria_nome);
        const dias  = diasAteVencer(p.validade_estimada);

        // Define o badge de validade baseado nos dias restantes
        let badgeValidade = '';
        if (dias !== null) {
            if (dias < 0) {
                badgeValidade = `<span class="badge-quantidade badge-vencida">⚠️ Vencida</span>`;
            } else if (dias <= 7) {
                badgeValidade = `<span class="badge-quantidade badge-alerta">⏰ ${dias}d restantes</span>`;
            } else {
                badgeValidade = `<span class="badge-quantidade">📅 Válida até ${formatarData(p.validade_estimada)}</span>`;
            }
        }

        return `
            <div class="porcao-card" style="border-left-color:${cor}">
                <div class="porcao-card-header">
                    <div class="porcao-card-nome">${p.nome}</div>
                    <span class="badge-categoria" style="background:${cor}">${p.categoria_nome}</span>
                </div>
                <div class="porcao-card-body">
                    <div class="porcao-info">
                        🍽️ <span><strong>${p.tipo_preparo || '—'}</strong></span>
                    </div>
                    <div class="porcao-info">
                        📦 <strong>${p.quantidade_disponivel}</strong> porção(ões) disponíveis
                    </div>
                    <div class="porcao-info">
                        📅 Preparado em: <strong>${formatarData(p.data_preparo)}</strong>
                    </div>
                    ${badgeValidade}
                </div>
                <div class="porcao-card-footer">
                    <button class="btn-edit"   onclick="abrirModalEdicao(${p.id})">✏️ Editar</button>
                    <button class="btn-danger" onclick="deletarPorcao(${p.id}, '${p.nome.replace(/'/g,"\\'")}')">🗑️ Remover</button>
                </div>
            </div>`;
    }).join('');
}


/* ═══════════════════════════════════════════════════════
   SEÇÃO: REFEIÇÕES
═══════════════════════════════════════════════════════ */

/**
 * GET /refeicoes — Rota 10
 * Carrega e renderiza todas as refeições montadas.
 */
async function carregarRefeicoes() {
    try {
        const resp      = await fetch(`${API_URL}/refeicoes`);
        const refeicoes = await resp.json();
        renderizarRefeicoes(refeicoes);
    } catch {
        mostrarToast('Erro ao carregar refeições', 'erro');
    }
}

/**
 * Abre o formulário de composição de refeição.
 * Antes de abrir, carrega as porções disponíveis
 * para preencher as checkboxes de seleção.
 * 
 * GET /porcoes — Rota 4 (segunda chamada, com propósito diferente)
 */
async function abrirFormRefeicao() {
    toggleForm('form-refeicao');
    if (document.getElementById('form-refeicao').classList.contains('hidden')) return;

    try {
        const resp    = await fetch(`${API_URL}/porcoes`);
        const porcoes = await resp.json();
        renderizarPorcoesSelecionaveis(porcoes);
    } catch {
        mostrarToast('Erro ao carregar porções', 'erro');
    }
}

/** Renderiza as checkboxes de seleção de porções para compor a refeição */
function renderizarPorcoesSelecionaveis(porcoes) {
    const container = document.getElementById('porcoes-selecionaveis');

    if (!porcoes.length) {
        container.innerHTML = '<p style="color:var(--text-light)">Cadastre porções antes de montar uma refeição.</p>';
        return;
    }

    container.innerHTML = porcoes.map(p => {
        const cor = getCorCategoria(p.categoria_nome);
        return `
            <label class="porcao-selecao-item" style="border-color:${cor}20">
                <input type="checkbox" value="${p.id}" 
                       onchange="this.closest('.porcao-selecao-item').classList.toggle('selecionada', this.checked)">
                <div>
                    <div class="porcao-selecao-nome">${p.nome}</div>
                    <div class="porcao-selecao-cat" style="color:${cor}">${p.categoria_nome}</div>
                </div>
            </label>`;
    }).join('');
}

/**
 * POST /refeicoes — Rota 9
 * Coleta o nome, data e porções selecionadas e envia para a API.
 */
async function criarRefeicao() {
    const nome = document.getElementById('refeicao-nome').value.trim();
    const data = document.getElementById('refeicao-data').value;

    // Coleta os ids das checkboxes marcadas
    const checkboxes  = document.querySelectorAll('#porcoes-selecionaveis input[type=checkbox]:checked');
    const porcoesIds  = Array.from(checkboxes).map(cb => parseInt(cb.value));

    if (!nome) {
        mostrarToast('Digite o nome da refeição', 'erro'); return;
    }
    if (!porcoesIds.length) {
        mostrarToast('Selecione ao menos uma porção', 'erro'); return;
    }

    const payload = { nome, porcoes_ids: porcoesIds };
    if (data) payload.data_planejada = data;

    try {
        const resp = await fetch(`${API_URL}/refeicoes`, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify(payload)
        });
        if (!resp.ok) throw new Error();

        document.getElementById('refeicao-nome').value = '';
        document.getElementById('refeicao-data').value = '';
        toggleForm('form-refeicao');
        mostrarToast(`Refeição "${nome}" montada com sucesso!`);
        carregarRefeicoes();
    } catch {
        mostrarToast('Erro ao criar refeição', 'erro');
    }
}

/**
 * DELETE /refeicoes/<id> — Rota 12
 */
async function deletarRefeicao(id, nome) {
    if (!confirm(`Remover a refeição "${nome}"?`)) return;

    try {
        const resp = await fetch(`${API_URL}/refeicoes/${id}`, { method: 'DELETE' });
        if (!resp.ok) throw new Error();
        mostrarToast(`Refeição "${nome}" removida`);
        carregarRefeicoes();
    } catch {
        mostrarToast('Erro ao remover refeição', 'erro');
    }
}

/**
 * GET /refeicoes/<id> — Rota 11
 * Expande os detalhes de uma refeição específica.
 */
async function verDetalhesRefeicao(id) {
    try {
        const resp     = await fetch(`${API_URL}/refeicoes/${id}`);
        const refeicao = await resp.json();
        const nomes    = refeicao.porcoes.map(p => p.nome).join(', ');
        alert(`Refeição: ${refeicao.nome}\nData: ${formatarData(refeicao.data_planejada)}\nComposição: ${nomes}`);
    } catch {
        mostrarToast('Erro ao buscar detalhes', 'erro');
    }
}

/** Renderiza os cards de refeição no DOM */
function renderizarRefeicoes(refeicoes) {
    const container = document.getElementById('lista-refeicoes');

    if (!refeicoes.length) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">🍽️</div>
                <p>Nenhuma refeição montada ainda.<br>Combine suas porções!</p>
            </div>`;
        return;
    }

    container.innerHTML = refeicoes.map(r => {
        const itens = r.porcoes.map(p => {
            const cor = getCorCategoria(p.categoria_nome);
            return `
                <div class="refeicao-porcao-item">
                    <span class="badge-categoria" style="background:${cor};font-size:.7rem">${p.categoria_nome}</span>
                    <span>${p.nome}</span>
                </div>`;
        }).join('');

        return `
            <div class="refeicao-card">
                <div class="refeicao-card-header">
                    <div class="refeicao-card-nome">🍽️ ${r.nome}</div>
                    <div class="refeicao-card-data">📅 ${formatarData(r.data_planejada)}</div>
                </div>
                <div class="refeicao-card-body">
                    <div class="refeicao-porcoes-lista">${itens || '<em>Sem porções</em>'}</div>
                </div>
                <div class="refeicao-card-footer">
                    <button class="btn-edit"   onclick="verDetalhesRefeicao(${r.id})">🔍 Detalhes</button>
                    <button class="btn-danger" onclick="deletarRefeicao(${r.id}, '${r.nome.replace(/'/g,"\\'")}')">🗑️ Remover</button>
                </div>
            </div>`;
    }).join('');
}


/* ═══════════════════════════════════════════════════════
   SEÇÃO: SUGESTÃO DO DIA
═══════════════════════════════════════════════════════ */

/**
 * GET /porcoes/sugestao — Rota 8
 * Pede ao servidor uma sugestão de refeição balanceada.
 * A lógica de seleção fica na API (server-side),
 * o front-end apenas exibe o resultado.
 */
async function gerarSugestao() {
    const container = document.getElementById('sugestao-container');
    container.innerHTML = '<p style="color:var(--text-light);padding:2rem">Gerando sugestão...</p>';

    try {
        const resp     = await fetch(`${API_URL}/porcoes/sugestao`);
        const dados    = await resp.json();
        const porcoes  = dados.sugestao || [];

        if (!porcoes.length) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">😕</div>
                    <p>Nenhuma porção disponível.<br>Cadastre porções com quantidade > 0!</p>
                </div>`;
            return;
        }

        const itens = porcoes.map(p => {
            const cor = getCorCategoria(p.categoria_nome);
            return `
                <div class="sugestao-item" style="border-left-color:${cor}">
                    <div>
                        <div class="sugestao-item-nome">${p.nome}</div>
                        <div class="sugestao-item-detalhe">
                            ${p.categoria_nome} · ${p.tipo_preparo || 'Sem preparo registrado'}
                        </div>
                    </div>
                    <span class="badge-categoria" style="background:${cor};margin-left:auto">${p.quantidade_disponivel} un.</span>
                </div>`;
        }).join('');

        container.innerHTML = `
            <div class="sugestao-card">
                <div class="sugestao-titulo">✨ Sua refeição de hoje</div>
                <div class="sugestao-porcoes">${itens}</div>
            </div>`;

        mostrarToast('Sugestão gerada com sucesso!');
    } catch {
        mostrarToast('Erro ao gerar sugestão. API offline?', 'erro');
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">⚠️</div>
                <p>Não foi possível conectar à API.</p>
            </div>`;
    }
}


/* ═══════════════════════════════════════════════════════
   INICIALIZAÇÃO — ponto de entrada do app
═══════════════════════════════════════════════════════ */

/**
 * Executado uma única vez quando o HTML termina de carregar.
 * DOMContentLoaded garante que todos os elementos já existem
 * antes de o JS tentar manipulá-los.
 */
document.addEventListener('DOMContentLoaded', () => {
    // Verifica a API
    verificarStatusAPI();

    // Define a seção inicial a partir do hash atual (ou 'categorias')
    const hashInicial = window.location.hash || '#categorias';
    mostrarSecao(hashInicial);
});
