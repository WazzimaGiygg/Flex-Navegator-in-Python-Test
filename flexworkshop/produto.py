import uuid
from datetime import datetime

class Produto:
    """Classe que representa um produto"""
    
    def __init__(self, nome, preco, quantidade, categoria="Geral", descricao=""):
        self.id = str(uuid.uuid4())
        self.nome = nome
        self.preco = float(preco)
        self.quantidade = int(quantidade)
        self.categoria = categoria
        self.descricao = descricao
        self.data_cadastro = datetime.now().isoformat()
        self.data_atualizacao = datetime.now().isoformat()
    
    def atualizar(self, nome=None, preco=None, quantidade=None, 
                  categoria=None, descricao=None):
        """Atualiza os dados do produto"""
        if nome:
            self.nome = nome
        if preco is not None:
            self.preco = float(preco)
        if quantidade is not None:
            self.quantidade = int(quantidade)
        if categoria:
            self.categoria = categoria
        if descricao is not None:
            self.descricao = descricao
        
        self.data_atualizacao = datetime.now().isoformat()
    
    def to_dict(self):
        """Converte o produto para dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'preco': self.preco,
            'quantidade': self.quantidade,
            'categoria': self.categoria,
            'descricao': self.descricao,
            'data_cadastro': self.data_cadastro,
            'data_atualizacao': self.data_atualizacao
        }
    
    @classmethod
    def from_dict(cls, dados):
        """Cria um produto a partir de um dicionário"""
        produto = cls(
            nome=dados['nome'],
            preco=dados['preco'],
            quantidade=dados['quantidade'],
            categoria=dados['categoria'],
            descricao=dados.get('descricao', '')
        )
        produto.id = dados['id']
        produto.data_cadastro = dados['data_cadastro']
        produto.data_atualizacao = dados['data_atualizacao']
        return produto
    
    def __str__(self):
        return (f"ID: {self.id}\n"
                f"Nome: {self.nome}\n"
                f"Preço: R$ {self.preco:.2f}\n"
                f"Quantidade: {self.quantidade}\n"
                f"Categoria: {self.categoria}\n"
                f"Descrição: {self.descricao}\n"
                f"Última atualização: {self.data_atualizacao}")