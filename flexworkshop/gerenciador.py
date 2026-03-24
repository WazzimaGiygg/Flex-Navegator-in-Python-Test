import os
import json
from typing import List, Optional
from produto import Produto
from criptografia import Criptografia
from config import Config

class GerenciadorProdutos:
    """Classe para gerenciar os produtos"""
    
    def __init__(self, arquivo_db=None, senha_cripto=None):
        """Inicializa o gerenciador"""
        self.arquivo_db = arquivo_db or Config.DB_FILE
        self.cripto = Criptografia(senha_cripto or Config.ENCRYPTION_KEY)
        self.produtos = []
        self.carregar_produtos()
    
    def carregar_produtos(self):
        """Carrega os produtos do arquivo JSON criptografado"""
        if not os.path.exists(self.arquivo_db):
            self.produtos = []
            return
        
        try:
            with open(self.arquivo_db, 'r', encoding='utf-8') as f:
                dados_cripto = json.load(f)
            
            # Descriptografa os dados
            dados = self.cripto.descriptografar(dados_cripto['dados'])
            
            # Converte para objetos Produto
            self.produtos = []
            for item in dados:
                self.produtos.append(Produto.from_dict(item))
                
            print(f"✓ {len(self.produtos)} produtos carregados com sucesso!")
            
        except Exception as e:
            print(f"✗ Erro ao carregar produtos: {e}")
            self.produtos = []
    
    def salvar_produtos(self):
        """Salva os produtos no arquivo JSON criptografado"""
        try:
            # Converte produtos para dicionários
            dados = [p.to_dict() for p in self.produtos]
            
            # Criptografa os dados
            dados_cripto = self.cripto.criptografar(dados)
            
            # Salva no arquivo
            with open(self.arquivo_db, 'w', encoding='utf-8') as f:
                json.dump({'dados': dados_cripto}, f, ensure_ascii=False, indent=2)
            
            print(f"✓ {len(self.produtos)} produtos salvos com sucesso!")
            return True
            
        except Exception as e:
            print(f"✗ Erro ao salvar produtos: {e}")
            return False
    
    def adicionar_produto(self, produto: Produto):
        """Adiciona um novo produto"""
        # Verifica se já existe produto com mesmo nome
        for p in self.produtos:
            if p.nome.lower() == produto.nome.lower():
                raise ValueError(f"Produto '{produto.nome}' já existe!")
        
        self.produtos.append(produto)
        self.salvar_produtos()
        print(f"✓ Produto '{produto.nome}' adicionado com sucesso!")
        return produto
    
    def listar_produtos(self, categoria=None):
        """Lista todos os produtos"""
        if not self.produtos:
            print("Nenhum produto cadastrado.")
            return []
        
        produtos_filtrados = self.produtos
        if categoria:
            produtos_filtrados = [p for p in self.produtos 
                                 if p.categoria.lower() == categoria.lower()]
        
        if not produtos_filtrados:
            print(f"Nenhum produto encontrado na categoria '{categoria}'.")
            return []
        
        print("\n" + "="*80)
        print(f"{'ID':<36} {'NOME':<20} {'PREÇO':<10} {'QTD':<6} {'CATEGORIA':<15}")
        print("="*80)
        
        for p in produtos_filtrados:
            print(f"{p.id:<36} {p.nome:<20} R$ {p.preco:<8.2f} {p.quantidade:<6} {p.categoria:<15}")
        
        print("="*80)
        return produtos_filtrados
    
    def buscar_produto(self, termo):
        """Busca produtos por nome ou ID"""
        resultados = []
        
        for p in self.produtos:
            if termo.lower() in p.nome.lower() or termo == p.id:
                resultados.append(p)
        
        return resultados
    
    def atualizar_produto(self, id_produto, **kwargs):
        """Atualiza um produto existente"""
        for produto in self.produtos:
            if produto.id == id_produto:
                produto.atualizar(**kwargs)
                self.salvar_produtos()
                print(f"✓ Produto '{produto.nome}' atualizado com sucesso!")
                return produto
        
        raise ValueError(f"Produto com ID {id_produto} não encontrado!")
    
    def remover_produto(self, id_produto):
        """Remove um produto"""
        for i, produto in enumerate(self.produtos):
            if produto.id == id_produto:
                nome = produto.nome
                del self.produtos[i]
                self.salvar_produtos()
                print(f"✓ Produto '{nome}' removido com sucesso!")
                return True
        
        raise ValueError(f"Produto com ID {id_produto} não encontrado!")
    
    def get_produto_por_id(self, id_produto):
        """Retorna um produto pelo ID"""
        for produto in self.produtos:
            if produto.id == id_produto:
                return produto
        return None
    
    def get_estatisticas(self):
        """Retorna estatísticas dos produtos"""
        if not self.produtos:
            return {
                'total_produtos': 0,
                'valor_total_estoque': 0,
                'media_preco': 0,
                'categorias': {}
            }
        
        total_valor = sum(p.preco * p.quantidade for p in self.produtos)
        media_preco = sum(p.preco for p in self.produtos) / len(self.produtos)
        
        categorias = {}
        for p in self.produtos:
            categorias[p.categoria] = categorias.get(p.categoria, 0) + 1
        
        return {
            'total_produtos': len(self.produtos),
            'valor_total_estoque': total_valor,
            'media_preco': media_preco,
            'categorias': categorias
        }