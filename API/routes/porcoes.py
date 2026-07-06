from datetime import date
from flask import Blueprint, request, jsonify

try:
    from ..database import db
    from ..models import Porcao, Categoria
except ImportError:
    from database import db
    from models import Porcao, Categoria

porcoes_bp = Blueprint('porcoes', __name__)


@porcoes_bp.route('/porcoes', methods=['POST'])
def cadastrar_porcao():
    """
    Cadastra uma nova porção congelada.
    ---
    tags:
      - Porções
    summary: Cria uma porção
    description: >
      Registra uma porção congelada no sistema, associando-a a uma categoria.
      As datas devem estar no formato ISO 8601 (YYYY-MM-DD).
      Se "data_preparo" não for informada, a data atual é usada.
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - nome
            - categoria_id
          properties:
            nome:
              type: string
              example: Frango desfiado
            categoria_id:
              type: integer
              example: 2
              description: ID de uma categoria já cadastrada
            tipo_preparo:
              type: string
              example: Cozido
            quantidade_disponivel:
              type: integer
              example: 4
              description: Número de porções disponíveis no freezer
            data_preparo:
              type: string
              format: date
              example: "2026-06-30"
            validade_estimada:
              type: string
              format: date
              example: "2026-08-30"
    responses:
      201:
        description: Porção criada com sucesso
      400:
        description: Campos obrigatórios ausentes ou data em formato inválido
      404:
        description: Categoria informada não encontrada
    """
    dados = request.get_json()

    if not dados or not dados.get('nome') or not dados.get('categoria_id'):
        return jsonify({'erro': 'Campos "nome" e "categoria_id" são obrigatórios'}), 400

    categoria = Categoria.query.get(dados['categoria_id'])
    if not categoria:
        return jsonify({'erro': 'Categoria não encontrada'}), 404

    data_preparo = None
    if dados.get('data_preparo'):
        try:
            data_preparo = date.fromisoformat(dados['data_preparo'])
        except ValueError:
            return jsonify({'erro': 'Formato de data inválido. Use YYYY-MM-DD'}), 400

    validade_estimada = None
    if dados.get('validade_estimada'):
        try:
            validade_estimada = date.fromisoformat(dados['validade_estimada'])
        except ValueError:
            return jsonify({'erro': 'Formato de data inválido. Use YYYY-MM-DD'}), 400

    nova = Porcao(
        nome                  = dados['nome'],
        categoria_id          = dados['categoria_id'],
        tipo_preparo          = dados.get('tipo_preparo'),
        quantidade_disponivel = dados.get('quantidade_disponivel', 1),
        data_preparo          = data_preparo or date.today(),
        validade_estimada     = validade_estimada
    )
    db.session.add(nova)
    db.session.commit()

    return jsonify(nova.to_dict()), 201


@porcoes_bp.route('/porcoes', methods=['GET'])
def listar_porcoes():
    """
    Lista todas as porções disponíveis.
    ---
    tags:
      - Porções
    summary: Lista porções
    description: >
      Retorna todas as porções cadastradas. Aceita filtro opcional
      por categoria através do parâmetro de query "categoria_id".
    parameters:
      - name: categoria_id
        in: query
        required: false
        type: integer
        description: Filtra porções por categoria
        example: 2
    responses:
      200:
        description: Lista de porções retornada com sucesso
    """
    categoria_id = request.args.get('categoria_id', type=int)

    query = Porcao.query
    if categoria_id:
        query = query.filter_by(categoria_id=categoria_id)

    porcoes = query.all()
    return jsonify([p.to_dict() for p in porcoes]), 200


@porcoes_bp.route('/porcoes/<int:id>', methods=['GET'])
def buscar_porcao(id):
    """
    Busca uma porção específica pelo ID.
    ---
    tags:
      - Porções
    summary: Busca porção por ID
    parameters:
      - name: id
        in: path
        required: true
        type: integer
        description: ID da porção a ser buscada
        example: 1
    responses:
      200:
        description: Porção encontrada e retornada com sucesso
      404:
        description: Porção não encontrada para o ID informado
    """
    porcao = Porcao.query.get(id)

    if not porcao:
        return jsonify({'erro': 'Porção não encontrada'}), 404

    return jsonify(porcao.to_dict()), 200


@porcoes_bp.route('/porcoes/<int:id>', methods=['PUT'])
def atualizar_porcao(id):
    """
    Atualiza os dados de uma porção existente.
    ---
    tags:
      - Porções
    summary: Atualiza porção
    description: >
      Atualiza um ou mais campos de uma porção já cadastrada.
      Apenas os campos enviados no corpo serão alterados;
      os demais mantêm seus valores atuais.
    parameters:
      - name: id
        in: path
        required: true
        type: integer
        description: ID da porção a ser atualizada
        example: 1
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            nome:
              type: string
              example: Frango grelhado
            tipo_preparo:
              type: string
              example: Grelhado
            quantidade_disponivel:
              type: integer
              example: 2
            validade_estimada:
              type: string
              format: date
              example: "2026-09-01"
    responses:
      200:
        description: Porção atualizada com sucesso
      400:
        description: Nenhum dado enviado ou formato de data inválido
      404:
        description: Porção não encontrada
    """
    porcao = Porcao.query.get(id)

    if not porcao:
        return jsonify({'erro': 'Porção não encontrada'}), 404

    dados = request.get_json()
    if not dados:
        return jsonify({'erro': 'Nenhum dado enviado'}), 400

    if 'nome' in dados:
        porcao.nome = dados['nome']
    if 'tipo_preparo' in dados:
        porcao.tipo_preparo = dados['tipo_preparo']
    if 'quantidade_disponivel' in dados:
        porcao.quantidade_disponivel = dados['quantidade_disponivel']
    if 'validade_estimada' in dados:
        try:
            porcao.validade_estimada = date.fromisoformat(dados['validade_estimada'])
        except ValueError:
            return jsonify({'erro': 'Formato de data inválido. Use YYYY-MM-DD'}), 400

    db.session.commit()

    return jsonify(porcao.to_dict()), 200


@porcoes_bp.route('/porcoes/<int:id>', methods=['DELETE'])
def deletar_porcao(id):
    """
    Remove uma porção do sistema.
    ---
    tags:
      - Porções
    summary: Remove porção
    description: >
      Exclui permanentemente uma porção do banco de dados.
      Se a porção faz parte de alguma refeição montada,
      o vínculo também é removido automaticamente.
    parameters:
      - name: id
        in: path
        required: true
        type: integer
        description: ID da porção a ser removida
        example: 1
    responses:
      200:
        description: Porção removida com sucesso
        schema:
          type: object
          properties:
            mensagem:
              type: string
              example: Porção "Frango desfiado" removida com sucesso
      404:
        description: Porção não encontrada
    """
    porcao = Porcao.query.get(id)

    if not porcao:
        return jsonify({'erro': 'Porção não encontrada'}), 404

    db.session.delete(porcao)
    db.session.commit()

    return jsonify({'mensagem': f'Porção "{porcao.nome}" removida com sucesso'}), 200


@porcoes_bp.route('/porcoes/sugestao', methods=['GET'])
def sugerir_refeicao():
    """
    Sugere uma refeição balanceada automaticamente.
    ---
    tags:
      - Porções
    summary: Sugestão automática de refeição
    description: >
      Gera uma sugestão de refeição sorteando aleatoriamente
      uma porção disponível (quantidade > 0) de cada categoria cadastrada.
      Útil para quem não quer decidir o que comer — o sistema decide.
    responses:
      200:
        description: Sugestão gerada com sucesso ou aviso de ausência de porções
        schema:
          type: object
          properties:
            mensagem:
              type: string
              example: Sugestão de refeição gerada com sucesso
            sugestao:
              type: array
              items:
                type: object
    """
    from models import Categoria
    import random

    categorias = Categoria.query.all()
    sugestao = []

    for cat in categorias:
        disponiveis = Porcao.query.filter_by(categoria_id=cat.id)\
                                  .filter(Porcao.quantidade_disponivel > 0)\
                                  .all()
        if disponiveis:
            escolha = random.choice(disponiveis)
            sugestao.append(escolha.to_dict())

    if not sugestao:
        return jsonify({'mensagem': 'Nenhuma porção disponível para sugestão'}), 200

    return jsonify({
        'mensagem': 'Sugestão de refeição gerada com sucesso',
        'sugestao': sugestao
    }), 200
