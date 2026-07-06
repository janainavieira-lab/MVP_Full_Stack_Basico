from flask import Blueprint, request, jsonify

try:
    from ..database import db
    from ..models import Categoria
except ImportError:
    from database import db
    from models import Categoria

categorias_bp = Blueprint('categorias', __name__)


@categorias_bp.route('/categorias', methods=['POST'])
def cadastrar_categoria():
    """
    Cadastra uma nova categoria de porção.
    ---
    tags:
      - Categorias
    summary: Cria uma categoria
    description: >
      Cadastra uma nova categoria para classificar as porções congeladas.
      Exemplos de categorias: Carboidrato, Proteína, Vegetal, Prato Pronto.
      Nomes duplicados não são permitidos.
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - nome
          properties:
            nome:
              type: string
              example: Proteína
              description: Nome da categoria (deve ser único)
    responses:
      201:
        description: Categoria criada com sucesso
        schema:
          type: object
          properties:
            id:
              type: integer
              example: 1
            nome:
              type: string
              example: Proteína
      400:
        description: Campo "nome" ausente ou inválido
        schema:
          type: object
          properties:
            erro:
              type: string
              example: O campo "nome" é obrigatório
      409:
        description: Categoria com este nome já existe
        schema:
          type: object
          properties:
            erro:
              type: string
              example: Categoria já cadastrada
    """
    dados = request.get_json()

    if not dados or not dados.get('nome'):
        return jsonify({'erro': 'O campo "nome" é obrigatório'}), 400

    existente = Categoria.query.filter_by(nome=dados['nome']).first()
    if existente:
        return jsonify({'erro': 'Categoria já cadastrada'}), 409

    nova = Categoria(nome=dados['nome'])
    db.session.add(nova)
    db.session.commit()

    return jsonify(nova.to_dict()), 201


@categorias_bp.route('/categorias', methods=['GET'])
def listar_categorias():
    """
    Lista todas as categorias cadastradas.
    ---
    tags:
      - Categorias
    summary: Lista categorias
    description: Retorna todas as categorias disponíveis para classificar porções.
    responses:
      200:
        description: Lista de categorias retornada com sucesso
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                example: 1
              nome:
                type: string
                example: Proteína
    """
    categorias = Categoria.query.all()
    return jsonify([c.to_dict() for c in categorias]), 200
