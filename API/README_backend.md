# 🧊 MarmitApp — Back-end (API REST)

API REST para gerenciamento de **meal prep** (preparo antecipado de refeições).
Permite cadastrar porções congeladas por categoria, combinar porções em refeições
balanceadas e obter sugestões automáticas de pratos com base no estoque disponível.

---

## 🎯 Problema que resolve

Pessoas que praticam meal prep enfrentam dificuldade para catalogar itens congelados,
combiná-los com variedade e planejar o preparo com antecedência. Esta API fornece o
back-end para um sistema que organiza esse processo de ponta a ponta.

---

## 🛠️ Tecnologias utilizadas

| Tecnologia | Versão | Função |
|------------|--------|--------|
| Python | 3.10+ | Linguagem base |
| Flask | 3.x | Framework web |
| Flask-SQLAlchemy | 3.x | ORM para banco de dados |
| Flask-CORS | 4.x | Permite acesso do front-end |
| Flasgger | 0.9.x | Documentação Swagger/OpenAPI |
| SQLite | — | Banco de dados embutido |

---

## 📁 Estrutura do projeto

```
backend/
├── app.py              # Ponto de entrada — inicializa Flask e registra blueprints
├── database.py         # Configuração da conexão com o SQLite via SQLAlchemy
├── models.py           # Definição das tabelas (Categoria, Porção, Refeição)
├── routes/
│   ├── __init__.py     # Torna a pasta um módulo Python
│   ├── categorias.py   # Rotas de gerenciamento de categorias
│   ├── porcoes.py      # Rotas de gerenciamento de porções
│   └── refeicoes.py    # Rotas de gerenciamento de refeições
└── requirements.txt    # Dependências do projeto
```

---

## ⚙️ Instalação e execução

### Pré-requisitos

- Python 3.10 ou superior instalado
- pip disponível no terminal

### Passo a passo

**1. Clone o repositório**

```bash
git clone https://github.com/seu-usuario/marmitapp-backend.git
cd marmitapp-backend
```

**2. Crie e ative um ambiente virtual**

```bash
# Criar
python -m venv venv

# Ativar no Windows
venv\Scripts\activate

# Ativar no macOS/Linux
source venv/bin/activate
```

**3. Instale as dependências**

```bash
pip install -r requirements.txt
```

**4. Execute a API**

```bash
python app.py
```

A API estará disponível em: `http://localhost:5000`

> O arquivo `meal_prep.db` é criado automaticamente na primeira execução.

---

## 📄 Documentação da API (Swagger)

Com a API rodando, acesse:

```
http://localhost:5000/apidocs
```

A interface Swagger UI exibe todas as rotas organizadas em três seções,
com exemplos de requisição, resposta e possibilidade de teste interativo.

---

## 🛣️ Rotas implementadas

### Categorias

| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/categorias` | Cadastra uma nova categoria |
| `GET` | `/categorias` | Lista todas as categorias |

### Porções

| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/porcoes` | Cadastra uma nova porção |
| `GET` | `/porcoes` | Lista porções (filtro opcional: `?categoria_id=N`) |
| `GET` | `/porcoes/<id>` | Busca uma porção por ID |
| `PUT` | `/porcoes/<id>` | Atualiza dados de uma porção |
| `DELETE` | `/porcoes/<id>` | Remove uma porção |
| `GET` | `/porcoes/sugestao` | Sugere refeição aleatória com porções disponíveis |

### Refeições

| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/refeicoes` | Cria uma refeição combinando porções |
| `GET` | `/refeicoes` | Lista todas as refeições montadas |
| `GET` | `/refeicoes/<id>` | Busca uma refeição por ID |
| `DELETE` | `/refeicoes/<id>` | Remove uma refeição |

---

## 🗄️ Modelo de dados

```
Categoria (1) ──── (N) Porção (N) ──── (N) Refeição
                                  (via tabela associativa refeicao_porcao)
```

**Tabelas:** `categoria`, `porcao`, `refeicao`, `refeicao_porcao`

**Relacionamentos:**
- 1:N entre Categoria e Porção (uma categoria tem várias porções)
- N:N entre Porção e Refeição (uma refeição é composta por várias porções; uma porção pode aparecer em várias refeições)

---

## 📐 Decisões de projeto

- **SQLite** foi escolhido por ser embutido, sem necessidade de servidor separado, adequado para o escopo de MVP.
- **Blueprints Flask** foram usados para separar as rotas em arquivos independentes (Separation of Concerns).
- **Migrations** não foram implementadas — `db.create_all()` é suficiente para o MVP, pois o banco é criado do zero a cada nova instalação.
- **CORS** está habilitado globalmente para permitir que o front-end acesse a API ao abrir `index.html` diretamente no navegador.
