from datetime import date
from flask import Blueprint, request, jsonify

try:
    from ..database import db
    from ..models import Refeicao, Porcao
except ImportError:
    from database import db
    from models import Refeicao, Porcao

refeicoes_bp = Blueprint('refeicoes', __name__)


@refeicoes_bp.route('/refeicoes', methods=['POST'])
def criar_refeicao():
    """
    Cria uma refeição combinando porções existentes.
    ---
    tags:
      - Refeições
    summary: Monta uma refeição
    description: >
      Cria uma refeição associando múltiplas porções já cadastradas.
      O relacionamento N:N é gerenciado automaticamente pelo sistema.
      Envie uma lista de IDs de porções válidas para compor o prato.
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - nome
            - porcoes_ids
          properties:
            nome:
              type: string
              example: Almoço de terça-feira
            porcoes_ids:
              type: array
              items:
                type: integer
              example: [1, 2, 3]
              description: Lista de IDs das porções que compõem a refeição
            data_planejada:
              type: string
              format: date
              example: "2026-07-01"
    responses:
      201:
        description: Refeição criada com sucesso, retorna a refeição com suas porções
      400:
        description: Campos obrigatórios ausentes
      404:
        description: Uma ou mais porções informadas não foram encontradas
    """
    dados = request.get_json()

    if not dados or not dados.get('nome') or not dados.get('porcoes_ids'):
        return jsonify({'erro': 'Campos "nome" e "porcoes_ids" são obrigatórios'}), 400

    porcoes = []
    for pid in dados['porcoes_ids']:
        porcao = Porcao.query.get(pid)
        if not porcao:
            return jsonify({'erro': f'Porção com id {pid} não encontrada'}), 404
        porcoes.append(porcao)

    data_planejada = None
    if dados.get('data_planejada'):
        try:
            data_planejada = date.fromisoformat(dados['data_planejada'])
        except ValueError:
            return jsonify({'erro': 'Formato de data inválido. Use YYYY-MM-DD'}), 400

    nova_refeicao = Refeicao(
        nome           = dados['nome'],
        data_planejada = data_planejada or date.today()
    )
    nova_refeicao.porcoes = porcoes

    db.session.add(nova_refeicao)
    db.session.commit()

    return jsonify(nova_refeicao.to_dict()), 201


@refeicoes_bp.route('/refeicoes', methods=['GET'])
def listar_refeicoes():
    """
    Lista todas as refeições montadas.
    ---
    tags:
      - Refeições
    summary: Lista refeições
    description: >
      Retorna todas as refeições cadastradas, cada uma com a lista
      completa das porções que a compõem e suas respectivas categorias.
    responses:
      200:
        description: Lista de refeições retornada com sucesso
    """
    refeicoes = Refeicao.query.all()
    return jsonify([r.to_dict() for r in refeicoes]), 200


@refeicoes_bp.route('/refeicoes/<int:id>', methods=['GET'])
def buscar_refeicao(id):
    """
    Busca uma refeição específica pelo ID.
    ---
    tags:
      - Refeições
    summary: Busca refeição por ID
    parameters:
      - name: id
        in: path
        required: true
        type: integer
        description: ID da refeição a ser buscada
        example: 1
    responses:
      200:
        description: Refeição encontrada com suas porções
      404:
        description: Refeição não encontrada
    """
    refeicao = Refeicao.query.get(id)

    if not refeicao:
        return jsonify({'erro': 'Refeição não encontrada'}), 404

    return jsonify(refeicao.to_dict()), 200


@refeicoes_bp.route('/refeicoes/<int:id>', methods=['DELETE'])
def deletar_refeicao(id):
    """
    Remove uma refeição do sistema.
    ---
    tags:
      - Refeições
    summary: Remove refeição
    description: >
      Exclui a refeição e seus vínculos com as porções.
      As porções em si NÃO são removidas — apenas a combinação é desfeita.
    parameters:
      - name: id
        in: path
        required: true
        type: integer
        description: ID da refeição a ser removida
        example: 1
    responses:
      200:
        description: Refeição removida com sucesso
        schema:
          type: object
          properties:
            mensagem:
              type: string
              example: Refeição "Almoço de terça-feira" removida com sucesso
      404:
        description: Refeição não encontrada
    """
    refeicao = Refeicao.query.get(id)

    if not refeicao:
        return jsonify({'erro': 'Refeição não encontrada'}), 404

    db.session.delete(refeicao)
    db.session.commit()

    return jsonify({'mensagem': f'Refeição "{refeicao.nome}" removida com sucesso'}), 200
