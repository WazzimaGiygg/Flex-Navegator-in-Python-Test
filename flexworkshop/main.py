import os
import sys
from gerenciador import GerenciadorProdutos
from produto import Produto
from config import Config

def limpar_tela():
    """Limpa a tela do terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')

def exibir_menu():
    """Exibe o menu principal"""
    print("\n" + "="*50)
    print("        GERENCIADOR DE PRODUTOS")
    print("="*50)
    print("1. Adicionar Produto")
    print("2. Listar Produtos")
    print("3. Buscar Produto")
    print("4. Atualizar Produto")
    print("5. Remover Produto")
    print("6. Estatísticas")
    print("7. Configurações")
    print("8. Sair")
    print("="*50)

def adicionar_produto(gerenciador):
    """Adiciona um novo produto"""
    print("\n--- ADICIONAR NOVO PRODUTO ---")
    
    try:
        nome = input("Nome do produto: ").strip()
        if not nome:
            print("✗ Nome não pode ser vazio!")
            return
        
        preco = float(input("Preço: R$ "))
        quantidade = int(input("Quantidade: "))
        categoria = input("Categoria (Enter para Geral): ").strip() or "Geral"
        descricao = input("Descrição (opcional): ").strip()
        
        produto = Produto(nome, preco, quantidade, categoria, descricao)
        gerenciador.adicionar_produto(produto)
        
    except ValueError as e:
        print(f"✗ Erro: {e}")
    except Exception as e:
        print(f"✗ Erro inesperado: {e}")

def listar_produtos(gerenciador):
    """Lista todos os produtos"""
    print("\n--- LISTAR PRODUTOS ---")
    
    categoria = input("Filtrar por categoria (Enter para todos): ").strip()
    
    if categoria:
        gerenciador.listar_produtos(categoria)
    else:
        gerenciador.listar_produtos()

def buscar_produto(gerenciador):
    """Busca um produto"""
    print("\n--- BUSCAR PRODUTO ---")
    termo = input("Digite o nome ou ID do produto: ").strip()
    
    if not termo:
        print("✗ Termo de busca inválido!")
        return
    
    resultados = gerenciador.buscar_produto(termo)
    
    if resultados:
        print(f"\n✓ Encontrados {len(resultados)} produto(s):")
        for produto in resultados:
            print("\n" + "-"*40)
            print(produto)
    else:
        print("✗ Nenhum produto encontrado!")

def atualizar_produto(gerenciador):
    """Atualiza um produto existente"""
    print("\n--- ATUALIZAR PRODUTO ---")
    
    # Lista produtos para facilitar
    gerenciador.listar_produtos()
    
    id_produto = input("\nDigite o ID do produto: ").strip()
    
    if not id_produto:
        print("✗ ID inválido!")
        return
    
    produto = gerenciador.get_produto_por_id(id_produto)
    if not produto:
        print(f"✗ Produto com ID {id_produto} não encontrado!")
        return
    
    print(f"\nProduto encontrado: {produto.nome}")
    print("\nDeixe em branco para manter o valor atual.")
    
    try:
        nome = input(f"Novo nome [{produto.nome}]: ").strip()
        preco_str = input(f"Novo preço [R$ {produto.preco:.2f}]: ").strip()
        qtd_str = input(f"Nova quantidade [{produto.quantidade}]: ").strip()
        categoria = input(f"Nova categoria [{produto.categoria}]: ").strip()
        descricao = input(f"Nova descrição [{produto.descricao}]: ").strip()
        
        kwargs = {}
        if nome:
            kwargs['nome'] = nome
        if preco_str:
            kwargs['preco'] = float(preco_str)
        if qtd_str:
            kwargs['quantidade'] = int(qtd_str)
        if categoria:
            kwargs['categoria'] = categoria
        if descricao:
            kwargs['descricao'] = descricao
        
        if kwargs:
            gerenciador.atualizar_produto(id_produto, **kwargs)
        else:
            print("Nenhuma alteração realizada.")
            
    except ValueError as e:
        print(f"✗ Erro: {e}")
    except Exception as e:
        print(f"✗ Erro inesperado: {e}")

def remover_produto(gerenciador):
    """Remove um produto"""
    print("\n--- REMOVER PRODUTO ---")
    
    # Lista produtos para facilitar
    gerenciador.listar_produtos()
    
    id_produto = input("\nDigite o ID do produto: ").strip()
    
    if not id_produto:
        print("✗ ID inválido!")
        return
    
    produto = gerenciador.get_produto_por_id(id_produto)
    if not produto:
        print(f"✗ Produto com ID {id_produto} não encontrado!")
        return
    
    confirmar = input(f"Tem certeza que deseja remover '{produto.nome}'? (s/N): ").strip().lower()
    
    if confirmar == 's':
        try:
            gerenciador.remover_produto(id_produto)
        except Exception as e:
            print(f"✗ Erro: {e}")
    else:
        print("Operação cancelada.")

def exibir_estatisticas(gerenciador):
    """Exibe estatísticas dos produtos"""
    print("\n--- ESTATÍSTICAS DOS PRODUTOS ---")
    
    stats = gerenciador.get_estatisticas()
    
    print(f"\nTotal de produtos: {stats['total_produtos']}")
    print(f"Valor total do estoque: R$ {stats['valor_total_estoque']:.2f}")
    print(f"Preço médio dos produtos: R$ {stats['media_preco']:.2f}")
    
    if stats['categorias']:
        print("\nProdutos por categoria:")
        for categoria, quantidade in stats['categorias'].items():
            print(f"  • {categoria}: {quantidade} produto(s)")

def configurar_sistema():
    """Configurações do sistema"""
    print("\n--- CONFIGURAÇÕES ---")
    print(f"Arquivo de dados atual: {Config.DB_FILE}")
    
    novo_arquivo = input("Novo arquivo de dados (Enter para manter): ").strip()
    if novo_arquivo:
        Config.DB_FILE = novo_arquivo
        print(f"✓ Arquivo alterado para: {novo_arquivo}")
    
    nova_senha = input("Nova senha de criptografia (Enter para manter): ").strip()
    if nova_senha:
        Config.ENCRYPTION_KEY = nova_senha.ljust(32, '!')[:32]
        print("✓ Senha de criptografia alterada!")
        print("⚠ ATENÇÃO: Os dados existentes precisam ser recriados com a nova senha!")

def main():
    """Função principal"""
    try:
        # Inicializa o gerenciador
        gerenciador = GerenciadorProdutos()
        
        while True:
            try:
                exibir_menu()
                opcao = input("\nEscolha uma opção (1-8): ").strip()
                
                if opcao == '1':
                    adicionar_produto(gerenciador)
                elif opcao == '2':
                    listar_produtos(gerenciador)
                elif opcao == '3':
                    buscar_produto(gerenciador)
                elif opcao == '4':
                    atualizar_produto(gerenciador)
                elif opcao == '5':
                    remover_produto(gerenciador)
                elif opcao == '6':
                    exibir_estatisticas(gerenciador)
                elif opcao == '7':
                    configurar_sistema()
                elif opcao == '8':
                    print("\n✓ Salvando dados e saindo...")
                    break
                else:
                    print("✗ Opção inválida! Escolha 1-8.")
                
                input("\nPressione Enter para continuar...")
                limpar_tela()
                
            except KeyboardInterrupt:
                print("\n\n✓ Programa interrompido pelo usuário.")
                break
            except Exception as e:
                print(f"\n✗ Erro: {e}")
                input("Pressione Enter para continuar...")
                limpar_tela()
                
    except Exception as e:
        print(f"Erro fatal ao iniciar o sistema: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()