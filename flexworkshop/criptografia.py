import json
import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from config import Config

class Criptografia:
    """Classe para gerenciar criptografia de dados"""
    
    def __init__(self, senha=None):
        """Inicializa o sistema de criptografia"""
        self.senha = senha or Config.ENCRYPTION_KEY
        self.fernet = self._gerar_fernet()
    
    def _gerar_fernet(self):
        """Gera uma chave Fernet a partir da senha"""
        # Converte a senha para bytes
        senha_bytes = self.senha.encode('utf-8')
        
        # Gera um salt (em produção, use um salt fixo ou armazene)
        salt = b'fixed_salt_123456'  # Em produção, use um salt único
        
        # Deriva uma chave usando PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        chave = base64.urlsafe_b64encode(kdf.derive(senha_bytes))
        return Fernet(chave)
    
    def criptografar(self, dados):
        """Criptografa os dados"""
        if isinstance(dados, (dict, list)):
            dados_str = json.dumps(dados, ensure_ascii=False)
        else:
            dados_str = str(dados)
        
        dados_bytes = dados_str.encode('utf-8')
        dados_cripto = self.fernet.encrypt(dados_bytes)
        return base64.b64encode(dados_cripto).decode('utf-8')
    
    def descriptografar(self, dados_cripto):
        """Descriptografa os dados"""
        try:
            dados_bytes = base64.b64decode(dados_cripto.encode('utf-8'))
            dados_dec = self.fernet.decrypt(dados_bytes)
            return json.loads(dados_dec.decode('utf-8'))
        except Exception as e:
            raise ValueError(f"Erro ao descriptografar dados: {e}")