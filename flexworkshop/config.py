import os

class Config:
    """Configurações do sistema"""
    # Nome padrão do arquivo de banco de dados
    DB_FILE = "produtos.json"
    
    # Chave de criptografia (em produção, use variável de ambiente)
    # IMPORTANTE: Em produção, NUNCA hardcode a chave
    ENCRYPTION_KEY = os.environ.get('PRODUTO_KEY', 'minha-chave-secreta-32-caracteres!!')
    
    # Garantir que a chave tenha 32 bytes
    ENCRYPTION_KEY = ENCRYPTION_KEY.ljust(32, '!')[:32]