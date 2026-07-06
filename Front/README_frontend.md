# 🧊 MarmitApp — Front-end (SPA)

Interface web para gerenciamento de **meal prep** (preparo antecipado de refeições).
Permite visualizar porções congeladas em cards coloridos por categoria, montar
refeições combinando porções e receber sugestões automáticas de pratos balanceados.

---

## 🎯 Problema que resolve

Organizar visualmente o estoque de um freezer de meal prep, facilitando a decisão
diária sobre o que comer e o planejamento semanal de refeições.

---

## 🛠️ Tecnologias utilizadas

| Tecnologia | Função |
|------------|--------|
| HTML5 | Estrutura semântica da SPA |
| CSS3 (customizado) | Design visual — sistema de variáveis, layout, animações |
| JavaScript (ES2017+) | Lógica da SPA: hash routing, Fetch API, manipulação do DOM |
| Bootstrap 5 (CDN) | Grid e utilitários básicos (sobrepostos por CSS customizado) |
| Google Fonts — DM Sans | Tipografia de identidade do projeto |

> ⚠️ Nenhum framework JavaScript (React, Vue, Angular) foi utilizado, em conformidade com os requisitos do projeto.

---

## 📁 Estrutura do projeto

```
frontend/
├── index.html       # Estrutura HTML da SPA — 4 seções, modal, toast
├── css/
│   └── style.css    # Design visual completo com variáveis CSS customizadas
└── js/
    └── app.js       # Lógica da SPA: hash routing, chamadas à API, renderização
```

---

## ⚙️ Como executar

**Pré-requisito:** a API do back-end deve estar rodando em `http://localhost:5000`.

**1. Clone o repositório**

```bash
git clone https://github.com/seu-usuario/marmitapp-frontend.git
cd marmitapp-frontend
```

**2. Abra o arquivo diretamente no navegador**

```
Clique duas vezes em index.html
— ou —
Arraste o arquivo para uma aba do navegador
```

> Nenhuma extensão, servidor local ou dependência adicional é necessária.

---

## 🗺️ Navegação

A SPA usa **hash routing** — a URL muda sem recarregar a página:

| Hash | Seção exibida |
|------|---------------|
| `#categorias` | Cadastro e listagem de categorias |
| `#porcoes` | Cadastro, filtro, edição e remoção de porções |
| `#refeicoes` | Montagem e listagem de refeições |
| `#sugestao` | Sugestão automática de refeição balanceada |

---

## 🔗 Rotas da API consumidas

| Ação na interface | Método | Rota |
|-------------------|--------|------|
| Criar categoria | `POST` | `/categorias` |
| Listar categorias | `GET` | `/categorias` |
| Criar porção | `POST` | `/porcoes` |
| Listar porções (com filtro) | `GET` | `/porcoes?categoria_id=N` |
| Abrir modal de edição | `GET` | `/porcoes/<id>` |
| Salvar edição | `PUT` | `/porcoes/<id>` |
| Remover porção | `DELETE` | `/porcoes/<id>` |
| Gerar sugestão | `GET` | `/porcoes/sugestao` |
| Montar refeição | `POST` | `/refeicoes` |
| Listar refeições | `GET` | `/refeicoes` |
| Ver detalhes | `GET` | `/refeicoes/<id>` |
| Remover refeição | `DELETE` | `/refeicoes/<id>` |

---

## 🎨 Design

**Conceito:** "Etiquetas do Freezer" — cada categoria de alimento tem uma cor
própria que aparece como borda lateral nos cards, evocando as etiquetas coloridas
usadas em potes de meal prep.

**Paleta principal:**

| Papel | Cor |
|-------|-----|
| Fundo da aplicação | `#EDF2F7` (cinza-azulado frio) |
| Sidebar | `#1A2744` (azul-marinho profundo) |
| Ação primária | `#00C9A7` (verde-menta) |
| Cards | `#FFFFFF` com sombra sutil |

**Cores de categoria:**

| Categoria | Cor |
|-----------|-----|
| Carboidrato | `#F6B93B` âmbar |
| Proteína | `#E55039` vermelho-salmão |
| Vegetal | `#00C9A7` verde-menta |
| Prato Pronto | `#A29BFE` lavanda |
