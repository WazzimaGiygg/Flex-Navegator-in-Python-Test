import sys
import json
import os
import base64
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import QWebEngineView  # Para renderizar HTML

# Importar bibliotecas de criptografia
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("Aviso: Biblioteca 'cryptography' não instalada. Funcionalidade de criptografia desabilitada.")

class Theme:
    """Classe para gerenciar temas do aplicativo"""
    
    def __init__(self, name, colors, fonts, custom_css=""):
        self.name = name
        self.colors = colors
        self.fonts = fonts
        self.custom_css = custom_css
    
    def generate_stylesheet(self):
        """Gerar o CSS completo baseado nas configurações do tema"""
        # Cores padrão
        bg_color = self.colors.get('bg_color', '#f5f5f5')
        text_color = self.colors.get('text_color', '#2c3e50')
        editor_bg = self.colors.get('editor_bg', 'white')
        editor_text = self.colors.get('editor_text', '#2c3e50')
        selection_bg = self.colors.get('selection_bg', '#3498db')
        selection_text = self.colors.get('selection_text', 'white')
        toolbar_bg = self.colors.get('toolbar_bg', '#ecf0f1')
        menubar_bg = self.colors.get('menubar_bg', '#34495e')
        menubar_text = self.colors.get('menubar_text', 'white')
        statusbar_bg = self.colors.get('statusbar_bg', '#34495e')
        statusbar_text = self.colors.get('statusbar_text', 'white')
        button_bg = self.colors.get('button_bg', '#3498db')
        button_hover = self.colors.get('button_hover', '#2980b9')
        button_text = self.colors.get('button_text', 'white')
        
        # Fontes
        editor_font = self.fonts.get('editor', 'Consolas, monospace')
        editor_size = self.fonts.get('editor_size', '11')
        ui_font = self.fonts.get('ui', 'Segoe UI, Arial')
        
        # Gerar CSS
        stylesheet = f"""
        QMainWindow {{
            background-color: {bg_color};
        }}
        
        QPlainTextEdit {{
            background-color: {editor_bg};
            color: {editor_text};
            font-family: '{editor_font}';
            font-size: {editor_size}pt;
            border: none;
            selection-background-color: {selection_bg};
            selection-color: {selection_text};
        }}
        
        QToolBar {{
            background-color: {toolbar_bg};
            border: none;
            spacing: 5px;
            padding: 5px;
        }}
        
        QToolBar QToolButton {{
            background-color: transparent;
            border: none;
            border-radius: 3px;
            padding: 5px;
        }}
        
        QToolBar QToolButton:hover {{
            background-color: {button_hover};
        }}
        
        QToolBar QToolButton:pressed {{
            background-color: {button_hover};
        }}
        
        QMenuBar {{
            background-color: {menubar_bg};
            color: {menubar_text};
            font-family: '{ui_font}';
        }}
        
        QMenuBar::item {{
            background-color: transparent;
            padding: 5px 10px;
        }}
        
        QMenuBar::item:selected {{
            background-color: {button_hover};
        }}
        
        QMenu {{
            background-color: {editor_bg};
            color: {editor_text};
            border: 1px solid {toolbar_bg};
            font-family: '{ui_font}';
        }}
        
        QMenu::item {{
            padding: 5px 30px 5px 20px;
        }}
        
        QMenu::item:selected {{
            background-color: {selection_bg};
            color: {selection_text};
        }}
        
        QStatusBar {{
            background-color: {statusbar_bg};
            color: {statusbar_text};
            font-family: '{ui_font}';
        }}
        
        #search-bar {{
            background-color: {toolbar_bg};
            border-top: 1px solid {button_hover};
        }}
        
        QLineEdit {{
            padding: 5px;
            border: 1px solid {button_hover};
            border-radius: 3px;
            background-color: {editor_bg};
            color: {editor_text};
            font-family: '{ui_font}';
        }}
        
        QLineEdit:focus {{
            border-color: {selection_bg};
        }}
        
        QPushButton {{
            padding: 5px 10px;
            background-color: {button_bg};
            color: {button_text};
            border: none;
            border-radius: 3px;
            font-family: '{ui_font}';
        }}
        
        QPushButton:hover {{
            background-color: {button_hover};
        }}
        
        QPushButton:pressed {{
            background-color: {button_hover};
        }}
        
        QDockWidget::title {{
            background-color: {toolbar_bg};
            padding: 5px;
            text-align: left;
            color: {editor_text};
        }}
        
        QTabWidget::pane {{
            border: 1px solid {toolbar_bg};
            background-color: {editor_bg};
        }}
        
        QTabBar::tab {{
            background-color: {toolbar_bg};
            padding: 5px 10px;
            margin-right: 2px;
            color: {editor_text};
        }}
        
        QTabBar::tab:selected {{
            background-color: {editor_bg};
        }}
        
        QScrollBar:vertical {{
            background: {toolbar_bg};
            width: 12px;
            margin: 0px;
        }}
        
        QScrollBar::handle:vertical {{
            background: {selection_bg};
            min-height: 20px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background: {button_hover};
        }}
        
        QScrollBar:horizontal {{
            background: {toolbar_bg};
            height: 12px;
            margin: 0px;
        }}
        
        QScrollBar::handle:horizontal {{
            background: {selection_bg};
            min-width: 20px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background: {button_hover};
        }}
        
        {self.custom_css}
        """
        
        return stylesheet

class ThemeManager:
    """Gerenciador de temas"""
    
    def __init__(self, app):
        self.app = app
        self.themes = {}
        self.current_theme = None
        self.themes_dir = "themes"
        
        # Criar diretório de temas se não existir
        if not os.path.exists(self.themes_dir):
            os.makedirs(self.themes_dir)
        
        # Carregar temas padrão
        self.load_default_themes()
        
        # Carregar temas salvos
        self.load_saved_themes()
    
    def load_default_themes(self):
        """Carregar temas padrão"""
        # Tema Claro (padrão)
        light_colors = {
            'bg_color': '#f5f5f5',
            'text_color': '#2c3e50',
            'editor_bg': 'white',
            'editor_text': '#2c3e50',
            'selection_bg': '#3498db',
            'selection_text': 'white',
            'toolbar_bg': '#ecf0f1',
            'menubar_bg': '#34495e',
            'menubar_text': 'white',
            'statusbar_bg': '#34495e',
            'statusbar_text': 'white',
            'button_bg': '#3498db',
            'button_hover': '#2980b9',
            'button_text': 'white'
        }
        
        light_fonts = {
            'editor': 'Consolas',
            'editor_size': '11',
            'ui': 'Segoe UI'
        }
        
        self.themes['Claro'] = Theme('Claro', light_colors, light_fonts)
        
        # Tema Escuro
        dark_colors = {
            'bg_color': '#1e1e1e',
            'text_color': '#d4d4d4',
            'editor_bg': '#252526',
            'editor_text': '#d4d4d4',
            'selection_bg': '#264f78',
            'selection_text': 'white',
            'toolbar_bg': '#2d2d30',
            'menubar_bg': '#2d2d30',
            'menubar_text': '#d4d4d4',
            'statusbar_bg': '#007acc',
            'statusbar_text': 'white',
            'button_bg': '#0e639c',
            'button_hover': '#1177bb',
            'button_text': 'white'
        }
        
        dark_fonts = {
            'editor': 'Consolas',
            'editor_size': '11',
            'ui': 'Segoe UI'
        }
        
        self.themes['Escuro'] = Theme('Escuro', dark_colors, dark_fonts)
        
        # Tema Solarized
        solarized_colors = {
            'bg_color': '#fdf6e3',
            'text_color': '#657b83',
            'editor_bg': '#fdf6e3',
            'editor_text': '#657b83',
            'selection_bg': '#eee8d5',
            'selection_text': '#586e75',
            'toolbar_bg': '#eee8d5',
            'menubar_bg': '#002b36',
            'menubar_text': '#839496',
            'statusbar_bg': '#073642',
            'statusbar_text': '#839496',
            'button_bg': '#2aa198',
            'button_hover': '#268bd2',
            'button_text': '#fdf6e3'
        }
        
        solarized_fonts = {
            'editor': 'Consolas',
            'editor_size': '11',
            'ui': 'Segoe UI'
        }
        
        self.themes['Solarized'] = Theme('Solarized', solarized_colors, solarized_fonts)
        
        # Tema Monokai
        monokai_colors = {
            'bg_color': '#272822',
            'text_color': '#f8f8f2',
            'editor_bg': '#272822',
            'editor_text': '#f8f8f2',
            'selection_bg': '#49483e',
            'selection_text': '#f8f8f2',
            'toolbar_bg': '#3e3d32',
            'menubar_bg': '#272822',
            'menubar_text': '#f8f8f2',
            'statusbar_bg': '#75715e',
            'statusbar_text': '#f8f8f2',
            'button_bg': '#e6db74',
            'button_hover': '#f8f8f2',
            'button_text': '#272822'
        }
        
        monokai_fonts = {
            'editor': 'Consolas',
            'editor_size': '11',
            'ui': 'Segoe UI'
        }
        
        self.themes['Monokai'] = Theme('Monokai', monokai_colors, monokai_fonts)
    
    def load_saved_themes(self):
        """Carregar temas salvos pelo usuário"""
        if os.path.exists(self.themes_dir):
            for filename in os.listdir(self.themes_dir):
                if filename.endswith('.json'):
                    try:
                        with open(os.path.join(self.themes_dir, filename), 'r', encoding='utf-8') as f:
                            theme_data = json.load(f)
                            name = theme_data.get('name', filename[:-5])
                            colors = theme_data.get('colors', {})
                            fonts = theme_data.get('fonts', {})
                            custom_css = theme_data.get('custom_css', '')
                            self.themes[name] = Theme(name, colors, fonts, custom_css)
                    except Exception as e:
                        print(f"Erro ao carregar tema {filename}: {e}")
    
    def save_theme(self, theme):
        """Salvar tema personalizado"""
        theme_data = {
            'name': theme.name,
            'colors': theme.colors,
            'fonts': theme.fonts,
            'custom_css': theme.custom_css
        }
        
        filename = theme.name.replace(' ', '_') + '.json'
        filepath = os.path.join(self.themes_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(theme_data, f, indent=2, ensure_ascii=False)
    
    def apply_theme(self, theme_name):
        """Aplicar tema ao aplicativo"""
        if theme_name in self.themes:
            self.current_theme = self.themes[theme_name]
            stylesheet = self.current_theme.generate_stylesheet()
            self.app.setStyleSheet(stylesheet)
            return True
        return False
    
    def get_theme_names(self):
        """Obter lista de nomes de temas"""
        return list(self.themes.keys())
    
    def create_custom_theme(self, name, colors, fonts, custom_css=""):
        """Criar um tema personalizado"""
        if name in self.themes:
            return False
        
        theme = Theme(name, colors, fonts, custom_css)
        self.themes[name] = theme
        self.save_theme(theme)
        return True
    
    def delete_theme(self, theme_name):
        """Excluir um tema personalizado"""
        if theme_name in ['Claro', 'Escuro', 'Solarized', 'Monokai']:
            return False  # Não pode excluir temas padrão
        
        if theme_name in self.themes:
            # Remover arquivo
            filename = theme_name.replace(' ', '_') + '.json'
            filepath = os.path.join(self.themes_dir, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
            
            # Remover do dicionário
            del self.themes[theme_name]
            return True
        
        return False

class HTMLPlugin:
    """Classe para gerenciar plugins HTML"""
    
    def __init__(self, name, html_code, description=""):
        self.name = name
        self.html_code = html_code
        self.description = description
        self.is_active = False
        self.widget = None
    
    def create_widget(self):
        """Cria o widget do plugin"""
        self.widget = QWebEngineView()
        self.widget.setHtml(self.html_code)
        return self.widget

class ThemeDialog(QDialog):
    """Diálogo para criar/editar temas"""
    
    def __init__(self, theme_manager, parent=None, edit_theme=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.edit_theme = edit_theme
        self.setWindowTitle(f"{'Editar' if edit_theme else 'Criar'} Tema")
        self.setModal(True)
        self.resize(600, 700)
        
        self.init_ui()
        
        if edit_theme:
            self.load_theme_data()
    
    def init_ui(self):
        """Inicializar interface do diálogo"""
        layout = QVBoxLayout()
        
        # Nome do tema
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Nome do Tema:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ex: Meu Tema Personalizado")
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # Abas para configurações
        tabs = QTabWidget()
        
        # Aba de cores
        colors_tab = QWidget()
        colors_layout = QFormLayout()
        
        self.color_inputs = {}
        color_fields = [
            ('bg_color', 'Cor de Fundo Principal'),
            ('editor_bg', 'Cor de Fundo do Editor'),
            ('editor_text', 'Cor do Texto'),
            ('selection_bg', 'Cor de Seleção'),
            ('selection_text', 'Cor do Texto Selecionado'),
            ('toolbar_bg', 'Cor da Barra de Ferramentas'),
            ('menubar_bg', 'Cor da Barra de Menus'),
            ('menubar_text', 'Cor do Texto do Menu'),
            ('statusbar_bg', 'Cor da Barra de Status'),
            ('statusbar_text', 'Cor do Texto da Barra de Status'),
            ('button_bg', 'Cor dos Botões'),
            ('button_hover', 'Cor ao Passar o Mouse'),
            ('button_text', 'Cor do Texto dos Botões')
        ]
        
        for field, label in color_fields:
            color_layout = QHBoxLayout()
            color_input = QLineEdit()
            color_input.setPlaceholderText("#RRGGBB")
            color_input.setMaximumWidth(100)
            
            color_btn = QPushButton("Selecionar")
            color_btn.clicked.connect(lambda checked, inp=color_input: self.select_color(inp))
            
            color_layout.addWidget(color_input)
            color_layout.addWidget(color_btn)
            
            colors_layout.addRow(label, color_layout)
            self.color_inputs[field] = color_input
        
        colors_tab.setLayout(colors_layout)
        tabs.addTab(colors_tab, "Cores")
        
        # Aba de fontes
        fonts_tab = QWidget()
        fonts_layout = QFormLayout()
        
        self.font_inputs = {}
        font_fields = [
            ('editor', 'Fonte do Editor'),
            ('editor_size', 'Tamanho da Fonte'),
            ('ui', 'Fonte da Interface')
        ]
        
        for field, label in font_fields:
            font_input = QLineEdit()
            if field == 'editor_size':
                font_input.setPlaceholderText("Ex: 11")
            else:
                font_input.setPlaceholderText("Ex: Consolas, 'Segoe UI'")
            fonts_layout.addRow(label, font_input)
            self.font_inputs[field] = font_input
        
        fonts_tab.setLayout(fonts_layout)
        tabs.addTab(fonts_tab, "Fontes")
        
        # Aba de CSS personalizado
        css_tab = QWidget()
        css_layout = QVBoxLayout()
        
        css_label = QLabel("CSS Personalizado (adicione suas próprias regras):")
        css_layout.addWidget(css_label)
        
        self.css_edit = QPlainTextEdit()
        self.css_edit.setPlaceholderText("""
/* Exemplo de CSS personalizado */
QPlainTextEdit {
    border-radius: 5px;
    margin: 5px;
}

QPushButton {
    font-weight: bold;
}
        """.strip())
        css_layout.addWidget(self.css_edit)
        
        css_tab.setLayout(css_layout)
        tabs.addTab(css_tab, "CSS Personalizado")
        
        layout.addWidget(tabs)
        
        # Botões
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def select_color(self, input_field):
        """Abrir seletor de cores"""
        color = QColorDialog.getColor()
        if color.isValid():
            input_field.setText(color.name())
    
    def load_theme_data(self):
        """Carregar dados do tema para edição"""
        theme = self.edit_theme
        self.name_input.setText(theme.name)
        self.name_input.setEnabled(False)  # Não pode editar nome
        
        # Carregar cores
        for field, input_field in self.color_inputs.items():
            if field in theme.colors:
                input_field.setText(theme.colors[field])
        
        # Carregar fontes
        for field, input_field in self.font_inputs.items():
            if field in theme.fonts:
                input_field.setText(str(theme.fonts[field]))
        
        # Carregar CSS
        self.css_edit.setPlainText(theme.custom_css)
    
    def get_theme_data(self):
        """Obter dados do tema do formulário"""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Erro", "Por favor, informe um nome para o tema.")
            return None
        
        # Coletar cores
        colors = {}
        for field, input_field in self.color_inputs.items():
            value = input_field.text().strip()
            if value:
                colors[field] = value
        
        # Coletar fontes
        fonts = {}
        for field, input_field in self.font_inputs.items():
            value = input_field.text().strip()
            if value:
                fonts[field] = value
        
        # Coletar CSS
        custom_css = self.css_edit.toPlainText()
        
        return {
            'name': name,
            'colors': colors,
            'fonts': fonts,
            'custom_css': custom_css
        }

class SimpleTextEditor(QMainWindow):
    """
    Editor de texto simples que salva arquivos em formato JSON com suporte a criptografia
    Versão com criptografia por senha e suporte a plugins HTML
    """
    
    def __init__(self):
        super().__init__()
        
        # Configurações da janela
        self.setWindowTitle("FlexNotepad - Bloco de Notas JSON com Criptografia e Plugins")
        self.setGeometry(100, 100, 1200, 700)
        self.setWindowIcon(QIcon("icone.ico"))
        
        # Variáveis de estado
        self.current_file = None
        self.is_modified = False
        self.search_text = ""
        self.replace_text = ""
        self.is_encrypted = False  # Indica se o arquivo atual está criptografado
        
        # Variáveis para plugins
        self.plugins = {}  # Dicionário de plugins carregados
        self.active_plugins = []  # Lista de plugins ativos
        self.plugin_dock = None  # Dock widget para os plugins
        
        # Gerenciador de temas
        self.theme_manager = ThemeManager(self)
        
        # Configurar interface
        self.init_ui()
        
        # Aplicar tema padrão
        self.theme_manager.apply_theme('Claro')
        
        # Mostrar boas-vindas
        self.show_welcome()
        
        # Carregar plugin padrão (Google Search)
        self.load_default_plugin()
    
    def load_default_plugin(self):
        """Carrega o plugin de busca do Google automaticamente"""
        google_plugin_html = """<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Busca Personalizada</title>
    <style>
        body { font-family: sans-serif; display: flex; justify-content: center; padding-top: 50px; background: inherit; }
        .search-box { display: flex; gap: 10px; }
        input[type="text"] { padding: 10px; width: 300px; border: 1px solid #ccc; border-radius: 4px; }
        button { padding: 10px 20px; background-color: #4285f4; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background-color: #357ae8; }
    </style>
</head>
<body>

    <form action="https://www.google.com/search" method="GET" class="search-box">
        <input type="text" name="q" placeholder="Pesquisar no Google..." required>
        <button type="submit">Buscar</button>
    </form>

</body>
</html>"""
        
        # Criar e adicionar o plugin
        plugin = HTMLPlugin("🔍 Busca Google", google_plugin_html, "Pesquise diretamente no Google")
        self.plugins["🔍 Busca Google"] = plugin
        self.add_plugin_to_interface(plugin)
        
        self.update_plugins_label()
        self.status_bar.showMessage("Plugin de Busca Google carregado automaticamente!", 3000)
    
    def init_ui(self):
        """Inicializar interface do usuário"""
        
        # ========== BARRA DE MENUS ==========
        menubar = self.menuBar()
        
        # Menu Arquivo
        file_menu = menubar.addMenu("&Arquivo")
        
        # Ações do menu Arquivo
        new_action = QAction("&Novo", self)
        new_action.setShortcut("Ctrl+N")
        new_action.setStatusTip("Criar novo arquivo")
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction("&Abrir...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.setStatusTip("Abrir arquivo existente")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        # Menu Importar com opção de plugins
        import_menu = file_menu.addMenu("&Importar")
        
        import_json_action = QAction("Importar &JSON...", self)
        import_json_action.setStatusTip("Importar arquivo JSON")
        import_json_action.triggered.connect(self.import_json)
        import_menu.addAction(import_json_action)
        
        import_txt_action = QAction("Importar &TXT...", self)
        import_txt_action.setStatusTip("Importar arquivo de texto")
        import_txt_action.triggered.connect(self.import_txt)
        import_menu.addAction(import_txt_action)
        
        import_menu.addSeparator()
        
        # NOVA OPÇÃO: Adicionar Plugin HTML
        add_plugin_action = QAction("➕ &Adicionar Plugin HTML...", self)
        add_plugin_action.setShortcut("Ctrl+P")
        add_plugin_action.setStatusTip("Adicionar um plugin HTML para auxiliar no editor")
        add_plugin_action.triggered.connect(self.add_html_plugin)
        import_menu.addAction(add_plugin_action)
        
        file_menu.addSeparator()
        
        save_action = QAction("&Salvar", self)
        save_action.setShortcut("Ctrl+S")
        save_action.setStatusTip("Salvar arquivo atual")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Salvar &Como...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.setStatusTip("Salvar arquivo com novo nome")
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        # Ação para salvar com senha
        self.save_encrypted_action = QAction("Salvar &Criptografado...", self)
        self.save_encrypted_action.setShortcut("Ctrl+E")
        self.save_encrypted_action.setStatusTip("Salvar arquivo com criptografia por senha")
        self.save_encrypted_action.triggered.connect(self.save_encrypted_file)
        if not CRYPTO_AVAILABLE:
            self.save_encrypted_action.setEnabled(False)
            self.save_encrypted_action.setToolTip("Funcionalidade indisponível - instale a biblioteca 'cryptography'")
        file_menu.addAction(self.save_encrypted_action)
        
        file_menu.addSeparator()
        
        export_txt_action = QAction("Exportar como &TXT...", self)
        export_txt_action.setStatusTip("Exportar como arquivo de texto simples")
        export_txt_action.triggered.connect(self.export_as_txt)
        file_menu.addAction(export_txt_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("&Sair", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Sair do programa")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menu Plugins
        plugins_menu = menubar.addMenu("&Plugins")
        
        manage_plugins_action = QAction("&Gerenciar Plugins", self)
        manage_plugins_action.setStatusTip("Gerenciar plugins carregados")
        manage_plugins_action.triggered.connect(self.manage_plugins)
        plugins_menu.addAction(manage_plugins_action)
        
        plugins_menu.addSeparator()
        
        self.show_plugins_action = QAction("&Mostrar Painel de Plugins", self)
        self.show_plugins_action.setCheckable(True)
        self.show_plugins_action.setStatusTip("Mostrar/ocultar painel de plugins")
        self.show_plugins_action.triggered.connect(self.toggle_plugin_panel)
        plugins_menu.addAction(self.show_plugins_action)
        
        # Menu Temas
        themes_menu = menubar.addMenu("🎨 &Temas")
        
        # Submenu de temas disponíveis
        self.themes_menu = themes_menu.addMenu("Aplicar Tema")
        
        # Atualizar lista de temas
        self.update_themes_menu()
        
        themes_menu.addSeparator()
        
        # Opção para criar novo tema
        create_theme_action = QAction("➕ Criar Novo Tema...", self)
        create_theme_action.setStatusTip("Criar um tema personalizado")
        create_theme_action.triggered.connect(self.create_custom_theme)
        themes_menu.addAction(create_theme_action)
        
        # Opção para editar tema
        edit_theme_action = QAction("✏️ Editar Tema Atual...", self)
        edit_theme_action.setStatusTip("Editar o tema atual")
        edit_theme_action.triggered.connect(self.edit_current_theme)
        themes_menu.addAction(edit_theme_action)
        
        # Opção para excluir tema
        delete_theme_action = QAction("🗑️ Excluir Tema...", self)
        delete_theme_action.setStatusTip("Excluir um tema personalizado")
        delete_theme_action.triggered.connect(self.delete_theme)
        themes_menu.addAction(delete_theme_action)
        
        # Menu Editar
        edit_menu = menubar.addMenu("&Editar")
        
        undo_action = QAction("&Desfazer", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.setStatusTip("Desfazer")
        undo_action.triggered.connect(self.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("&Refazer", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.setStatusTip("Refazer")
        redo_action.triggered.connect(self.redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        cut_action = QAction("&Recortar", self)
        cut_action.setShortcut("Ctrl+X")
        cut_action.setStatusTip("Recortar")
        cut_action.triggered.connect(self.cut)
        edit_menu.addAction(cut_action)
        
        copy_action = QAction("&Copiar", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.setStatusTip("Copiar")
        copy_action.triggered.connect(self.copy)
        edit_menu.addAction(copy_action)
        
        paste_action = QAction("&Colar", self)
        paste_action.setShortcut("Ctrl+V")
        paste_action.setStatusTip("Colar")
        paste_action.triggered.connect(self.paste)
        edit_menu.addAction(paste_action)
        
        edit_menu.addSeparator()
        
        select_all_action = QAction("Selecionar &Tudo", self)
        select_all_action.setShortcut("Ctrl+A")
        select_all_action.setStatusTip("Selecionar tudo")
        select_all_action.triggered.connect(self.select_all)
        edit_menu.addAction(select_all_action)
        
        # Menu Localizar
        search_menu = menubar.addMenu("&Localizar")
        
        find_action = QAction("&Localizar...", self)
        find_action.setShortcut("Ctrl+F")
        find_action.setStatusTip("Localizar texto")
        find_action.triggered.connect(self.show_search)
        search_menu.addAction(find_action)
        
        find_next_action = QAction("Localizar &Próximo", self)
        find_next_action.setShortcut("F3")
        find_next_action.setStatusTip("Localizar próximo")
        find_next_action.triggered.connect(self.find_next)
        search_menu.addAction(find_next_action)
        
        replace_action = QAction("&Substituir...", self)
        replace_action.setShortcut("Ctrl+H")
        replace_action.setStatusTip("Substituir texto")
        replace_action.triggered.connect(self.show_replace)
        search_menu.addAction(replace_action)
        
        # Menu Exibir
        view_menu = menubar.addMenu("&Exibir")
        
        word_wrap_action = QAction("&Quebra de Linha", self)
        word_wrap_action.setCheckable(True)
        word_wrap_action.setChecked(True)
        word_wrap_action.setStatusTip("Ativar/desativar quebra de linha")
        word_wrap_action.triggered.connect(self.toggle_word_wrap)
        view_menu.addAction(word_wrap_action)
        
        toolbar_action = QAction("&Barra de Ferramentas", self)
        toolbar_action.setCheckable(True)
        toolbar_action.setChecked(True)
        toolbar_action.setStatusTip("Mostrar/ocultar barra de ferramentas")
        toolbar_action.triggered.connect(self.toggle_toolbar)
        view_menu.addAction(toolbar_action)
        
        statusbar_action = QAction("&Barra de Status", self)
        statusbar_action.setCheckable(True)
        statusbar_action.setChecked(True)
        statusbar_action.setStatusTip("Mostrar/ocultar barra de status")
        statusbar_action.triggered.connect(self.toggle_statusbar)
        view_menu.addAction(statusbar_action)
        
        view_menu.addSeparator()
        
        zoom_in_action = QAction("Aumentar &Zoom", self)
        zoom_in_action.setShortcut("Ctrl++")
        zoom_in_action.setStatusTip("Aumentar zoom")
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("Diminuir &Zoom", self)
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.setStatusTip("Diminuir zoom")
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)
        
        zoom_reset_action = QAction("&Resetar Zoom", self)
        zoom_reset_action.setShortcut("Ctrl+0")
        zoom_reset_action.setStatusTip("Resetar zoom")
        zoom_reset_action.triggered.connect(self.zoom_reset)
        view_menu.addAction(zoom_reset_action)
        
        # Menu Ajuda
        help_menu = menubar.addMenu("A&juda")
        
        about_action = QAction("&Sobre", self)
        about_action.setStatusTip("Sobre o programa")
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        # ========== BARRA DE FERRAMENTAS ==========
        self.toolbar = QToolBar("Barra de Ferramentas")
        self.toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(self.toolbar)
        
        # Botões da barra de ferramentas
        btn_new = QAction(QIcon.fromTheme("document-new"), "Novo", self)
        btn_new.setStatusTip("Novo arquivo")
        btn_new.triggered.connect(self.new_file)
        self.toolbar.addAction(btn_new)
        
        btn_open = QAction(QIcon.fromTheme("document-open"), "Abrir", self)
        btn_open.setStatusTip("Abrir arquivo")
        btn_open.triggered.connect(self.open_file)
        self.toolbar.addAction(btn_open)
        
        btn_save = QAction(QIcon.fromTheme("document-save"), "Salvar", self)
        btn_save.setStatusTip("Salvar arquivo")
        btn_save.triggered.connect(self.save_file)
        self.toolbar.addAction(btn_save)
        
        self.toolbar.addSeparator()
        
        btn_cut = QAction(QIcon.fromTheme("edit-cut"), "Recortar", self)
        btn_cut.setStatusTip("Recortar")
        btn_cut.triggered.connect(self.cut)
        self.toolbar.addAction(btn_cut)
        
        btn_copy = QAction(QIcon.fromTheme("edit-copy"), "Copiar", self)
        btn_copy.setStatusTip("Copiar")
        btn_copy.triggered.connect(self.copy)
        self.toolbar.addAction(btn_copy)
        
        btn_paste = QAction(QIcon.fromTheme("edit-paste"), "Colar", self)
        btn_paste.setStatusTip("Colar")
        btn_paste.triggered.connect(self.paste)
        self.toolbar.addAction(btn_paste)
        
        self.toolbar.addSeparator()
        
        btn_undo = QAction(QIcon.fromTheme("edit-undo"), "Desfazer", self)
        btn_undo.setStatusTip("Desfazer")
        btn_undo.triggered.connect(self.undo)
        self.toolbar.addAction(btn_undo)
        
        btn_redo = QAction(QIcon.fromTheme("edit-redo"), "Refazer", self)
        btn_redo.setStatusTip("Refazer")
        btn_redo.triggered.connect(self.redo)
        self.toolbar.addAction(btn_redo)
        
        self.toolbar.addSeparator()
        
        btn_find = QAction(QIcon.fromTheme("edit-find"), "Localizar", self)
        btn_find.setStatusTip("Localizar texto")
        btn_find.triggered.connect(self.show_search)
        self.toolbar.addAction(btn_find)
        
        self.toolbar.addSeparator()
        
        # Botão para adicionar plugin
        btn_plugin = QAction(self)
        btn_plugin.setText("🔌 Adicionar Plugin")
        btn_plugin.setStatusTip("Adicionar plugin HTML")
        btn_plugin.triggered.connect(self.add_html_plugin)
        self.toolbar.addAction(btn_plugin)
        
        # Botão de temas
        btn_theme = QAction(self)
        btn_theme.setText("🎨 Tema")
        btn_theme.setStatusTip("Abrir menu de temas")
        btn_theme.triggered.connect(self.show_theme_menu)
        self.toolbar.addAction(btn_theme)
        
        # ========== ÁREA CENTRAL COM SPLITTER ==========
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Criar splitter para dividir editor e plugins
        self.main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.main_splitter)
        
        # Widget do editor
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        
        # Área de texto
        self.text_area = QPlainTextEdit()
        self.text_area.setFont(QFont("Consolas", 11))
        self.text_area.textChanged.connect(self.on_text_changed)
        self.text_area.cursorPositionChanged.connect(self.on_cursor_position_changed)
        editor_layout.addWidget(self.text_area)
        
        # Barra de localização (inicialmente oculta)
        self.search_bar = QWidget()
        self.search_bar.setObjectName("search-bar")
        search_layout = QHBoxLayout(self.search_bar)
        search_layout.setContentsMargins(5, 5, 5, 5)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Localizar...")
        self.search_input.textChanged.connect(self.on_search_text_changed)
        self.search_input.returnPressed.connect(self.find_next)
        
        self.replace_input = QLineEdit()
        self.replace_input.setPlaceholderText("Substituir por...")
        self.replace_input.returnPressed.connect(self.replace_current)
        self.replace_input.hide()
        
        btn_find_prev = QPushButton("⬆")
        btn_find_prev.setToolTip("Anterior")
        btn_find_prev.setMaximumWidth(30)
        btn_find_prev.clicked.connect(self.find_previous)
        
        btn_find_next = QPushButton("⬇")
        btn_find_next.setToolTip("Próximo")
        btn_find_next.setMaximumWidth(30)
        btn_find_next.clicked.connect(self.find_next)
        
        self.btn_replace = QPushButton("Substituir")
        self.btn_replace.setToolTip("Substituir ocorrência atual")
        self.btn_replace.hide()
        self.btn_replace.clicked.connect(self.replace_current)
        
        self.btn_replace_all = QPushButton("Substituir Tudo")
        self.btn_replace_all.setToolTip("Substituir todas as ocorrências")
        self.btn_replace_all.hide()
        self.btn_replace_all.clicked.connect(self.replace_all)
        
        btn_close_search = QPushButton("✕")
        btn_close_search.setToolTip("Fechar")
        btn_close_search.setMaximumWidth(30)
        btn_close_search.clicked.connect(self.hide_search)
        
        search_layout.addWidget(QLabel("🔍"))
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(btn_find_prev)
        search_layout.addWidget(btn_find_next)
        search_layout.addWidget(self.replace_input)
        search_layout.addWidget(self.btn_replace)
        search_layout.addWidget(self.btn_replace_all)
        search_layout.addStretch()
        search_layout.addWidget(btn_close_search)
        
        editor_layout.addWidget(self.search_bar)
        self.search_bar.hide()
        
        self.main_splitter.addWidget(editor_widget)
        
        # ========== DOCK DE PLUGINS ==========
        self.plugin_dock = QDockWidget("Plugins", self)
        self.plugin_dock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
        
        self.plugin_tab_widget = QTabWidget()
        self.plugin_tab_widget.setTabsClosable(True)
        self.plugin_tab_widget.tabCloseRequested.connect(self.close_plugin_tab)
        
        self.plugin_dock.setWidget(self.plugin_tab_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.plugin_dock)
        self.plugin_dock.show()  # Mostrar o dock pois já temos um plugin padrão
        
        # ========== BARRA DE STATUS ==========
        self.status_bar = self.statusBar()
        
        # Label de posição do cursor
        self.position_label = QLabel("Lin 1, Col 1")
        self.status_bar.addPermanentWidget(self.position_label)
        
        # Label de modo de inserção
        self.mode_label = QLabel("INS")
        self.status_bar.addPermanentWidget(self.mode_label)
        
        # Label de tamanho do arquivo
        self.size_label = QLabel("0 caracteres")
        self.status_bar.addPermanentWidget(self.size_label)
        
        # Label de status de criptografia
        self.encrypt_label = QLabel("🔓")
        self.encrypt_label.setToolTip("Arquivo não criptografado")
        self.status_bar.addPermanentWidget(self.encrypt_label)
        
        # Label de plugins ativos
        self.plugins_label = QLabel("🔌 0 plugins")
        self.status_bar.addPermanentWidget(self.plugins_label)
        
        # Label do tema atual
        self.theme_label = QLabel("🎨 Claro")
        self.status_bar.addPermanentWidget(self.theme_label)
    
    def update_themes_menu(self):
        """Atualizar o menu de temas"""
        self.themes_menu.clear()
        
        for theme_name in self.theme_manager.get_theme_names():
            action = QAction(theme_name, self)
            action.triggered.connect(lambda checked, name=theme_name: self.apply_theme(name))
            self.themes_menu.addAction(action)
    
    def apply_theme(self, theme_name):
        """Aplicar um tema"""
        if self.theme_manager.apply_theme(theme_name):
            self.theme_label.setText(f"🎨 {theme_name}")
            self.status_bar.showMessage(f"Tema '{theme_name}' aplicado!", 3000)
            
            # Atualizar a fonte do editor
            theme = self.theme_manager.current_theme
            if theme and 'editor' in theme.fonts and 'editor_size' in theme.fonts:
                font = QFont(theme.fonts['editor'], int(theme.fonts['editor_size']))
                self.text_area.setFont(font)
    
    def show_theme_menu(self):
        """Mostrar menu de temas na posição da barra de ferramentas"""
        menu = QMenu(self)
        for theme_name in self.theme_manager.get_theme_names():
            action = menu.addAction(theme_name)
            action.triggered.connect(lambda checked, name=theme_name: self.apply_theme(name))
        menu.exec_(QCursor.pos())
    
    def create_custom_theme(self):
        """Criar um tema personalizado"""
        dialog = ThemeDialog(self.theme_manager, self)
        if dialog.exec_() == QDialog.Accepted:
            theme_data = dialog.get_theme_data()
            if theme_data:
                success = self.theme_manager.create_custom_theme(
                    theme_data['name'],
                    theme_data['colors'],
                    theme_data['fonts'],
                    theme_data['custom_css']
                )
                if success:
                    self.update_themes_menu()
                    QMessageBox.information(self, "Sucesso", f"Tema '{theme_data['name']}' criado com sucesso!")
                    self.apply_theme(theme_data['name'])
                else:
                    QMessageBox.warning(self, "Erro", "Já existe um tema com este nome.")
    
    def edit_current_theme(self):
        """Editar o tema atual"""
        if self.theme_manager.current_theme:
            theme = self.theme_manager.current_theme
            dialog = ThemeDialog(self.theme_manager, self, edit_theme=theme)
            if dialog.exec_() == QDialog.Accepted:
                # Recriar o tema com os dados editados
                # (como o nome não pode ser editado, apenas recriamos)
                theme_data = dialog.get_theme_data()
                if theme_data:
                    # Atualizar o tema existente
                    theme.colors = theme_data['colors']
                    theme.fonts = theme_data['fonts']
                    theme.custom_css = theme_data['custom_css']
                    self.theme_manager.save_theme(theme)
                    self.apply_theme(theme.name)
                    QMessageBox.information(self, "Sucesso", f"Tema '{theme.name}' atualizado com sucesso!")
        else:
            QMessageBox.warning(self, "Erro", "Nenhum tema ativo para editar.")
    
    def delete_theme(self):
        """Excluir um tema personalizado"""
        theme_names = self.theme_manager.get_theme_names()
        # Filtrar temas que podem ser excluídos (não padrão)
        deletable_themes = [name for name in theme_names if name not in ['Claro', 'Escuro', 'Solarized', 'Monokai']]
        
        if not deletable_themes:
            QMessageBox.information(self, "Informação", "Não há temas personalizados para excluir.")
            return
        
        theme_name, ok = QInputDialog.getItem(
            self, "Excluir Tema",
            "Selecione o tema para excluir:",
            deletable_themes, 0, False
        )
        
        if ok and theme_name:
            reply = QMessageBox.question(
                self, "Confirmar",
                f"Tem certeza que deseja excluir o tema '{theme_name}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                if self.theme_manager.delete_theme(theme_name):
                    self.update_themes_menu()
                    # Se o tema excluído era o atual, voltar para o tema Claro
                    if self.theme_manager.current_theme and self.theme_manager.current_theme.name == theme_name:
                        self.apply_theme('Claro')
                    QMessageBox.information(self, "Sucesso", f"Tema '{theme_name}' excluído com sucesso!")
                else:
                    QMessageBox.warning(self, "Erro", "Não foi possível excluir o tema.")
    
    # ========== FUNÇÕES DE PLUGIN ==========
    
    def add_html_plugin(self):
        """Adicionar um novo plugin HTML"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Adicionar Plugin HTML")
        dialog.setModal(True)
        dialog.resize(600, 500)
        
        layout = QVBoxLayout()
        
        # Nome do plugin
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Nome do Plugin:"))
        name_input = QLineEdit()
        name_input.setPlaceholderText("Ex: Calculadora, Tradutor, etc...")
        name_layout.addWidget(name_input)
        layout.addLayout(name_layout)
        
        # Descrição
        desc_layout = QHBoxLayout()
        desc_layout.addWidget(QLabel("Descrição:"))
        desc_input = QLineEdit()
        desc_input.setPlaceholderText("Descrição opcional do plugin")
        desc_layout.addWidget(desc_input)
        layout.addLayout(desc_layout)
        
        # Área para código HTML
        layout.addWidget(QLabel("Código HTML:"))
        html_edit = QPlainTextEdit()
        html_edit.setPlaceholderText("""
Exemplo de plugin HTML:
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            font-family: Arial;
            padding: 10px;
            background: #f0f0f0;
        }
        button {
            background: #3498db;
            color: white;
            border: none;
            padding: 10px;
            margin: 5px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <h3>Minha Ferramenta</h3>
    <button onclick="alert('Olá!')">Clique aqui</button>
</body>
</html>
        """.strip())
        layout.addWidget(html_edit)
        
        # Botões
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        dialog.setLayout(layout)
        
        if dialog.exec_() == QDialog.Accepted:
            name = name_input.text().strip()
            html_code = html_edit.toPlainText().strip()
            description = desc_input.text().strip()
            
            if not name:
                QMessageBox.warning(self, "Erro", "Por favor, informe um nome para o plugin.")
                return
            
            if not html_code:
                QMessageBox.warning(self, "Erro", "Por favor, insira o código HTML do plugin.")
                return
            
            # Criar e adicionar plugin
            plugin = HTMLPlugin(name, html_code, description)
            self.plugins[name] = plugin
            self.add_plugin_to_interface(plugin)
            
            self.update_plugins_label()
            self.status_bar.showMessage(f"Plugin '{name}' adicionado com sucesso!", 3000)
    
    def add_plugin_to_interface(self, plugin):
        """Adicionar plugin à interface"""
        # Criar widget do plugin
        widget = plugin.create_widget()
        
        # Adicionar à tab widget
        index = self.plugin_tab_widget.addTab(widget, plugin.name)
        self.plugin_tab_widget.setTabToolTip(index, plugin.description or plugin.name)
        
        # Mostrar dock se estiver oculto
        if not self.plugin_dock.isVisible():
            self.plugin_dock.show()
            self.show_plugins_action.setChecked(True)
        
        plugin.is_active = True
        self.active_plugins.append(plugin)
    
    def close_plugin_tab(self, index):
        """Fechar uma aba de plugin"""
        tab_text = self.plugin_tab_widget.tabText(index)
        
        reply = QMessageBox.question(
            self, "Remover Plugin",
            f"Deseja remover o plugin '{tab_text}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Remover da lista de plugins
            if tab_text in self.plugins:
                plugin = self.plugins[tab_text]
                if plugin in self.active_plugins:
                    self.active_plugins.remove(plugin)
                del self.plugins[tab_text]
            
            # Remover a tab
            self.plugin_tab_widget.removeTab(index)
            
            # Se não houver mais plugins, ocultar o dock
            if self.plugin_tab_widget.count() == 0:
                self.plugin_dock.hide()
                self.show_plugins_action.setChecked(False)
            
            self.update_plugins_label()
            self.status_bar.showMessage(f"Plugin '{tab_text}' removido", 3000)
    
    def manage_plugins(self):
        """Gerenciar plugins carregados"""
        if not self.plugins:
            QMessageBox.information(self, "Gerenciar Plugins", 
                                   "Nenhum plugin carregado.\nUse Arquivo > Importar > Adicionar Plugin HTML para adicionar plugins.")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Gerenciar Plugins")
        dialog.setModal(True)
        dialog.resize(500, 300)
        
        layout = QVBoxLayout()
        
        # Lista de plugins
        layout.addWidget(QLabel("Plugins carregados:"))
        
        list_widget = QListWidget()
        for name, plugin in self.plugins.items():
            item = QListWidgetItem(f"🔌 {name}")
            if plugin.description:
                item.setToolTip(plugin.description)
            list_widget.addItem(item)
        
        layout.addWidget(list_widget)
        
        # Botões de ação
        button_layout = QHBoxLayout()
        
        btn_remove = QPushButton("Remover Selecionado")
        btn_remove.clicked.connect(lambda: self.remove_plugin_from_manager(list_widget, dialog))
        button_layout.addWidget(btn_remove)
        
        button_layout.addStretch()
        
        btn_close = QPushButton("Fechar")
        btn_close.clicked.connect(dialog.accept)
        button_layout.addWidget(btn_close)
        
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def remove_plugin_from_manager(self, list_widget, dialog):
        """Remover plugin da interface de gerenciamento"""
        current_item = list_widget.currentItem()
        if current_item:
            name = current_item.text().replace("🔌 ", "")
            
            reply = QMessageBox.question(
                self, "Remover Plugin",
                f"Deseja remover o plugin '{name}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Encontrar e fechar a tab correspondente
                for i in range(self.plugin_tab_widget.count()):
                    if self.plugin_tab_widget.tabText(i) == name:
                        self.close_plugin_tab(i)
                        break
                
                # Atualizar lista
                list_widget.takeItem(list_widget.row(current_item))
                
                if list_widget.count() == 0:
                    dialog.accept()
    
    def toggle_plugin_panel(self, checked):
        """Alternar visibilidade do painel de plugins"""
        if checked:
            if self.plugin_tab_widget.count() > 0:
                self.plugin_dock.show()
            else:
                QMessageBox.information(self, "Plugins", 
                                       "Nenhum plugin carregado.\nUse Arquivo > Importar > Adicionar Plugin HTML para adicionar plugins.")
                self.show_plugins_action.setChecked(False)
        else:
            self.plugin_dock.hide()
    
    def update_plugins_label(self):
        """Atualizar label de plugins na barra de status"""
        count = len(self.plugins)
        if count == 0:
            self.plugins_label.setText("🔌 0 plugins")
        else:
            self.plugins_label.setText(f"🔌 {count} plugin{'s' if count > 1 else ''}")
    
    # ========== FUNÇÕES DE IMPORTAÇÃO ==========
    
    def import_json(self):
        """Importar arquivo JSON para o editor"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Importar JSON", "",
            "Arquivos JSON (*.json);;Todos os Arquivos (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.text_area.setPlainText(json.dumps(data, indent=2, ensure_ascii=False))
                self.status_bar.showMessage(f"JSON importado: {file_path}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao importar JSON:\n{str(e)}")
    
    def import_txt(self):
        """Importar arquivo TXT para o editor"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Importar TXT", "",
            "Arquivos de Texto (*.txt);;Todos os Arquivos (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.text_area.setPlainText(content)
                self.status_bar.showMessage(f"Texto importado: {file_path}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao importar TXT:\n{str(e)}")
    
    # ========== FUNÇÕES DE CRIPTOGRAFIA ==========
    
    def derive_key(self, password: str, salt: bytes = None) -> tuple:
        """Derivar chave a partir da senha usando PBKDF2"""
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt
    
    def encrypt_content(self, content: str, password: str) -> dict:
        """Criptografar o conteúdo com a senha"""
        if not CRYPTO_AVAILABLE:
            raise Exception("Biblioteca 'cryptography' não está instalada")
        
        # Gerar salt aleatório
        salt = os.urandom(16)
        
        # Derivar chave
        key, _ = self.derive_key(password, salt)
        
        # Criar cipher
        f = Fernet(key)
        
        # Criptografar o conteúdo
        encrypted_data = f.encrypt(content.encode('utf-8'))
        
        # Retornar dados criptografados com salt
        return {
            'encrypted': True,
            'salt': base64.b64encode(salt).decode(),
            'data': base64.b64encode(encrypted_data).decode(),
            'algorithm': 'AES-256-CBC',
            'key_derivation': 'PBKDF2-HMAC-SHA256'
        }
    
    def decrypt_content(self, encrypted_data: dict, password: str) -> str:
        """Descriptografar o conteúdo com a senha"""
        if not CRYPTO_AVAILABLE:
            raise Exception("Biblioteca 'cryptography' não está instalada")
        
        # Verificar se é um arquivo criptografado
        if not encrypted_data.get('encrypted', False):
            return None
        
        try:
            # Recuperar salt
            salt = base64.b64decode(encrypted_data['salt'])
            
            # Derivar chave
            key, _ = self.derive_key(password, salt)
            
            # Criar cipher
            f = Fernet(key)
            
            # Descriptografar
            encrypted_content = base64.b64decode(encrypted_data['data'])
            decrypted_content = f.decrypt(encrypted_content)
            
            return decrypted_content.decode('utf-8')
        except Exception as e:
            raise Exception("Senha incorreta ou arquivo corrompido")
    
    def get_password(self, title="Senha", message="Digite a senha:", is_new=False):
        """Dialog para obter senha do usuário"""
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setModal(True)
        layout = QVBoxLayout()
        
        # Mensagem
        label = QLabel(message)
        layout.addWidget(label)
        
        # Campo de senha
        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(password_input)
        
        if is_new:
            # Confirmar senha
            label_confirm = QLabel("Confirme a senha:")
            layout.addWidget(label_confirm)
            
            confirm_input = QLineEdit()
            confirm_input.setEchoMode(QLineEdit.Password)
            layout.addWidget(confirm_input)
        
        # Botões
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        dialog.setLayout(layout)
        
        if dialog.exec_() == QDialog.Accepted:
            password = password_input.text()
            if is_new:
                confirm = confirm_input.text()
                if password != confirm:
                    QMessageBox.warning(self, "Erro", "As senhas não coincidem!")
                    return None
                if not password:
                    QMessageBox.warning(self, "Erro", "A senha não pode estar vazia!")
                    return None
            return password
        
        return None
    
    def save_encrypted_file(self):
        """Salvar arquivo com criptografia"""
        if not CRYPTO_AVAILABLE:
            QMessageBox.critical(self, "Erro", 
                               "Biblioteca 'cryptography' não está instalada.\n"
                               "Instale com: pip install cryptography")
            return
        
        # Verificar se precisa salvar antes
        if self.is_modified and self.current_file and not self.is_encrypted:
            reply = QMessageBox.question(
                self, "Salvar?",
                "O arquivo atual não está salvo. Deseja salvá-lo primeiro?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            if reply == QMessageBox.Cancel:
                return
            elif reply == QMessageBox.Yes:
                self.save_file()
        
        # Escolher local para salvar
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Salvar Arquivo Criptografado", "",
            "Arquivos JSON (*.json);;Todos os Arquivos (*.*)"
        )
        
        if not file_path:
            return
        
        # Obter senha
        password = self.get_password("Criptografar Arquivo", 
                                     "Digite uma senha para proteger o arquivo:", 
                                     is_new=True)
        if not password:
            return
        
        try:
            content = self.text_area.toPlainText()
            
            # Criar metadados
            metadata = {
                'created': datetime.now().isoformat() if not self.current_file else None,
                'modified': datetime.now().isoformat(),
                'characters': len(content),
                'words': len(content.split()),
                'lines': content.count('\n') + 1
            }
            
            # Criptografar o conteúdo
            encrypted_data = self.encrypt_content(content, password)
            
            # Salvar dados criptografados com metadados
            save_data = {
                'encrypted': True,
                'metadata': metadata,
                'crypto_info': encrypted_data
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            self.current_file = file_path
            self.is_modified = False
            self.is_encrypted = True
            self.update_window_title()
            self.update_encrypt_label()
            self.status_bar.showMessage(f"Arquivo criptografado salvo: {file_path}", 5000)
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar arquivo criptografado:\n{str(e)}")
    
    def save_to_file(self, file_path):
        """Salvar conteúdo no arquivo (sem criptografia)"""
        try:
            content = self.text_area.toPlainText()
            
            if file_path.endswith('.json'):
                # Salvar com metadados
                data = {
                    'encrypted': False,
                    'content': content,
                    'metadata': {
                        'created': datetime.now().isoformat() if not self.current_file else None,
                        'modified': datetime.now().isoformat(),
                        'characters': len(content),
                        'words': len(content.split()),
                        'lines': content.count('\n') + 1
                    }
                }
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                # Salvar como texto simples
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            self.current_file = file_path
            self.is_modified = False
            self.is_encrypted = False
            self.update_window_title()
            self.update_encrypt_label()
            self.status_bar.showMessage(f"Arquivo salvo: {file_path}", 3000)
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar arquivo:\n{str(e)}")
    
    def open_file(self):
        """Abrir arquivo"""
        if not self.check_save():
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Abrir Arquivo", "",
            "Arquivos JSON (*.json);;Arquivos de Texto (*.txt);;Todos os Arquivos (*.*)"
        )
        
        if not file_path:
            return
        
        try:
            if file_path.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Verificar se é arquivo criptografado
                    if isinstance(data, dict) and data.get('encrypted', False):
                        # Solicitar senha
                        password = self.get_password("Arquivo Criptografado", 
                                                    "Este arquivo está criptografado.\nDigite a senha para abrir:")
                        if not password:
                            return
                        
                        # Descriptografar
                        content = self.decrypt_content(data['crypto_info'], password)
                        if content is None:
                            QMessageBox.critical(self, "Erro", "Falha ao descriptografar o arquivo.")
                            return
                        
                        self.text_area.setPlainText(content)
                        self.is_encrypted = True
                    else:
                        # Arquivo normal
                        if isinstance(data, dict) and 'content' in data:
                            content = data['content']
                        else:
                            content = str(data)
                        self.text_area.setPlainText(content)
                        self.is_encrypted = False
            else:
                # Arquivo de texto simples
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.text_area.setPlainText(content)
                self.is_encrypted = False
            
            self.current_file = file_path
            self.is_modified = False
            self.update_window_title()
            self.update_size_label()
            self.update_encrypt_label()
            self.status_bar.showMessage(f"Arquivo carregado: {file_path}", 3000)
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao abrir arquivo:\n{str(e)}")
    
    def new_file(self):
        """Criar novo arquivo"""
        if self.check_save():
            self.text_area.clear()
            self.current_file = None
            self.is_modified = False
            self.is_encrypted = False
            self.update_window_title()
            self.update_size_label()
            self.update_encrypt_label()
            self.status_bar.showMessage("Novo arquivo criado", 3000)
    
    def export_as_txt(self):
        """Exportar como TXT"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exportar como TXT", "",
            "Arquivos de Texto (*.txt);;Todos os Arquivos (*.*)"
        )
        
        if file_path:
            try:
                content = self.text_area.toPlainText()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.status_bar.showMessage(f"Arquivo exportado: {file_path}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao exportar:\n{str(e)}")
    
    def check_save(self):
        """Verificar se precisa salvar antes de fechar/abrir novo"""
        if self.is_modified:
            reply = QMessageBox.question(
                self, "Salvar?",
                "O arquivo foi modificado. Deseja salvar as alterações?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Save:
                self.save_file()
                return True
            elif reply == QMessageBox.Cancel:
                return False
        
        return True
    
    def save_file(self):
        """Salvar arquivo (formato normal ou criptografado dependendo do estado)"""
        if self.current_file:
            if self.is_encrypted:
                # Se o arquivo atual é criptografado, salvar como criptografado
                self.save_encrypted_file()
            else:
                self.save_to_file(self.current_file)
        else:
            # Perguntar se quer salvar criptografado ou não
            reply = QMessageBox.question(
                self, "Tipo de Salvamento",
                "Deseja salvar com criptografia?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Cancel:
                return
            elif reply == QMessageBox.Yes:
                self.save_encrypted_file()
            else:
                self.save_file_as()
    
    def save_file_as(self):
        """Salvar arquivo como (sem criptografia)"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Salvar Arquivo Como", "",
            "Arquivos JSON (*.json);;Arquivos de Texto (*.txt);;Todos os Arquivos (*.*)"
        )
        
        if file_path:
            self.save_to_file(file_path)
    
    def closeEvent(self, event):
        """Evento de fechar a janela"""
        if self.check_save():
            event.accept()
        else:
            event.ignore()
    
    # ========== FUNÇÕES DE EDIÇÃO ==========
    
    def on_text_changed(self):
        """Quando o texto muda"""
        self.is_modified = True
        self.update_window_title()
        self.update_size_label()
    
    def on_cursor_position_changed(self):
        """Quando o cursor muda de posição"""
        cursor = self.text_area.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        self.position_label.setText(f"Lin {line}, Col {col}")
    
    def update_window_title(self):
        """Atualizar título da janela"""
        title = "FlexNotepad"
        if self.current_file:
            title += f" - {os.path.basename(self.current_file)}"
        if self.is_encrypted:
            title += " [Criptografado]"
        if self.is_modified:
            title += " *"
        self.setWindowTitle(title)
    
    def update_size_label(self):
        """Atualizar label de tamanho"""
        text = self.text_area.toPlainText()
        chars = len(text)
        words = len(text.split())
        lines = text.count('\n') + 1
        
        self.size_label.setText(f"{chars} caracteres | {words} palavras | {lines} linhas")
    
    def update_encrypt_label(self):
        """Atualizar label de criptografia na barra de status"""
        if self.is_encrypted:
            self.encrypt_label.setText("🔒")
            self.encrypt_label.setToolTip("Arquivo criptografado")
        else:
            self.encrypt_label.setText("🔓")
            self.encrypt_label.setToolTip("Arquivo não criptografado")
    
    def undo(self):
        self.text_area.undo()
    
    def redo(self):
        self.text_area.redo()
    
    def cut(self):
        self.text_area.cut()
    
    def copy(self):
        self.text_area.copy()
    
    def paste(self):
        self.text_area.paste()
    
    def select_all(self):
        self.text_area.selectAll()
    
    # ========== FUNÇÕES DE LOCALIZAÇÃO ==========
    
    def show_search(self):
        """Mostrar barra de localização"""
        self.search_bar.show()
        self.search_input.setFocus()
        self.replace_input.hide()
        self.btn_replace.hide()
        self.btn_replace_all.hide()
    
    def show_replace(self):
        """Mostrar barra de substituição"""
        self.search_bar.show()
        self.search_input.setFocus()
        self.replace_input.show()
        self.btn_replace.show()
        self.btn_replace_all.show()
    
    def hide_search(self):
        """Ocultar barra de localização"""
        self.search_bar.hide()
        self.search_input.clear()
        self.replace_input.clear()
        self.text_area.setExtraSelections([])
    
    def on_search_text_changed(self, text):
        """Quando o texto de busca muda"""
        self.search_text = text
        self.highlight_all()
    
    def highlight_all(self):
        """Destacar todas as ocorrências"""
        extra_selections = []
        
        if self.search_text:
            highlight_format = QTextCharFormat()
            highlight_format.setBackground(QColor(255, 255, 0, 100))
            
            document = self.text_area.document()
            cursor = QTextCursor(document)
            
            while True:
                cursor = document.find(self.search_text, cursor)
                if cursor.isNull():
                    break
                
                selection = QTextEdit.ExtraSelection()
                selection.cursor = cursor
                selection.format = highlight_format
                extra_selections.append(selection)
        
        self.text_area.setExtraSelections(extra_selections)
    
    def find_next(self):
        """Encontrar próxima ocorrência"""
        if not self.search_text:
            return
        
        cursor = self.text_area.textCursor()
        
        if cursor.hasSelection() and cursor.selectedText() == self.search_text:
            cursor.movePosition(QTextCursor.NextCharacter)
            self.text_area.setTextCursor(cursor)
        
        found = self.text_area.find(self.search_text)
        
        if not found:
            cursor.movePosition(QTextCursor.Start)
            self.text_area.setTextCursor(cursor)
            found = self.text_area.find(self.search_text)
            
            if found:
                self.status_bar.showMessage("Início do documento alcançado", 3000)
            else:
                self.status_bar.showMessage(f"Texto '{self.search_text}' não encontrado", 3000)
                return False
        
        return True
    
    def find_previous(self):
        """Encontrar ocorrência anterior"""
        if not self.search_text:
            return
        
        found = self.text_area.find(self.search_text, QTextDocument.FindBackward)
        
        if not found:
            cursor = self.text_area.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.text_area.setTextCursor(cursor)
            found = self.text_area.find(self.search_text, QTextDocument.FindBackward)
            
            if found:
                self.status_bar.showMessage("Final do documento alcançado", 3000)
            else:
                self.status_bar.showMessage(f"Texto '{self.search_text}' não encontrado", 3000)
                return False
        
        return True
    
    def replace_current(self):
        """Substituir ocorrência atual"""
        if not self.search_text:
            return
        
        cursor = self.text_area.textCursor()
        
        if cursor.hasSelection() and cursor.selectedText() == self.search_text:
            cursor.insertText(self.replace_input.text())
            self.is_modified = True
            self.update_window_title()
            self.find_next()
        else:
            if self.find_next():
                self.replace_current()
    
    def replace_all(self):
        """Substituir todas as ocorrências"""
        if not self.search_text:
            return
        
        original_cursor = self.text_area.textCursor()
        cursor = self.text_area.textCursor()
        cursor.beginEditBlock()
        
        cursor.movePosition(QTextCursor.Start)
        self.text_area.setTextCursor(cursor)
        
        count = 0
        replace_text = self.replace_input.text()
        
        while self.text_area.find(self.search_text):
            cursor = self.text_area.textCursor()
            cursor.insertText(replace_text)
            count += 1
        
        cursor.endEditBlock()
        self.text_area.setTextCursor(original_cursor)
        
        if count > 0:
            self.is_modified = True
            self.update_window_title()
            QMessageBox.information(self, "Substituir", f"Foram substituídas {count} ocorrências.")
        else:
            QMessageBox.information(self, "Substituir", f"Nenhuma ocorrência de '{self.search_text}' encontrada.")
    
    # ========== FUNÇÕES DE EXIBIÇÃO ==========
    
    def toggle_word_wrap(self, checked):
        """Alternar quebra de linha"""
        if checked:
            self.text_area.setLineWrapMode(QPlainTextEdit.WidgetWidth)
        else:
            self.text_area.setLineWrapMode(QPlainTextEdit.NoWrap)
    
    def toggle_toolbar(self, checked):
        """Alternar barra de ferramentas"""
        if checked:
            self.toolbar.show()
        else:
            self.toolbar.hide()
    
    def toggle_statusbar(self, checked):
        """Alternar barra de status"""
        if checked:
            self.status_bar.show()
        else:
            self.status_bar.hide()
    
    def zoom_in(self):
        """Aumentar zoom"""
        font = self.text_area.font()
        font.setPointSize(font.pointSize() + 1)
        self.text_area.setFont(font)
    
    def zoom_out(self):
        """Diminuir zoom"""
        font = self.text_area.font()
        size = font.pointSize()
        if size > 8:
            font.setPointSize(size - 1)
            self.text_area.setFont(font)
    
    def zoom_reset(self):
        """Resetar zoom"""
        font = QFont("Consolas", 11)
        self.text_area.setFont(font)
    
    # ========== FUNÇÕES DE AJUDA ==========
    
    def show_welcome(self):
        """Mostrar mensagem de boas-vindas"""
        welcome_text = """# FlexNotepad - Bloco de Notas JSON com Criptografia, Plugins e Temas Personalizáveis

## 📝 Bem-vindo!

Este é um editor de texto que salva arquivos em formato JSON com suporte a criptografia, plugins HTML e temas personalizáveis.

### ✨ Funcionalidades:
- ✅ Salvar arquivos em formato JSON
- ✅ Criptografia por senha (AES-256)
- ✅ Abrir arquivos criptografados e não criptografados
- ✅ **🔌 Suporte a plugins HTML** (adicione ferramentas auxiliares)
- ✅ **🎨 Temas personalizáveis** (crie seu próprio visual!)
- ✅ **🔍 Plugin de Busca Google incluso automaticamente!**
- ✅ Localizar e substituir texto
- ✅ Desfazer/Refazer
- ✅ Quebra de linha
- ✅ Zoom ajustável

### 🎨 Como usar os temas:
- Use o menu "Temas" para escolher entre os temas prontos
- Crie seu próprio tema personalizado com cores e fontes
- Edite temas existentes
- Exclua temas personalizados quando não precisar mais

### 🔌 Como usar plugins HTML:
- O plugin de busca do Google já está carregado no painel lateral!
- Use **Ctrl+P** ou menu Arquivo > Importar > "Adicionar Plugin HTML..." para adicionar mais plugins
- Cole o código HTML de uma ferramenta auxiliar
- O plugin aparecerá no painel lateral
- Você pode adicionar vários plugins e alternar entre eles

### 🔒 Como usar a criptografia:
- Use **Ctrl+E** ou menu Arquivo > "Salvar Criptografado..."
- Digite uma senha forte para proteger seu arquivo
- O arquivo será salvo com extensão .json (mas estará criptografado)
- Ao abrir um arquivo criptografado, será solicitada a senha

### 🚀 Como usar:
- Use **Ctrl+N** para novo arquivo
- Use **Ctrl+O** para abrir
- Use **Ctrl+S** para salvar (sem criptografia)
- Use **Ctrl+E** para salvar com criptografia
- Use **Ctrl+P** para adicionar plugin
- Use **Ctrl+F** para localizar
- Use **Ctrl+H** para substituir

### 📁 Formato JSON:
Os arquivos são salvos com metadados incluindo:
- Data de criação e modificação
- Contagem de caracteres, palavras e linhas
- Indicação de criptografia

Divirta-se! 🎉
"""
        self.text_area.setPlainText(welcome_text)
        self.current_file = None
        self.is_modified = False
        self.is_encrypted = False
        self.update_window_title()
        self.update_encrypt_label()
    
    def show_about(self):
        """Mostrar diálogo sobre"""
        crypto_status = "✅ Disponível" if CRYPTO_AVAILABLE else "❌ Não disponível (instale cryptography)"
        
        about_text = f"""
        <h2>Flex Notepad</h2>
        <p><b>Versão:</b> 4.0.0</p>
        <p>Um editor de texto que salva em formato JSON com suporte a criptografia, plugins HTML e temas personalizáveis.</p>
        
        <h3>🎨 Temas:</h3>
        <p>Crie seus próprios temas com cores e fontes personalizadas!</p>
        <p><b>Temas inclusos:</b> Claro, Escuro, Solarized, Monokai</p>
        
        <h3>🔌 Plugins:</h3>
        <p>Adicione ferramentas HTML auxiliares para ajudar no editor!</p>
        <p>Exemplos: calculadoras, conversores, geradores de código, etc.</p>
        <p><b>Plugin padrão:</b> 🔍 Busca Google - Pesquise diretamente sem sair do editor!</p>
        
        <h3>🔒 Criptografia:</h3>
        <p><b>Status:</b> {crypto_status}</p>
        <p><b>Algoritmo:</b> AES-256 (Fernet)</p>
        <p><b>Derivação de chave:</b> PBKDF2-HMAC-SHA256</p>
        
        <h3>Funcionalidades:</h3>
        <ul>
            <li>Salvar arquivos em JSON com metadados</li>
            <li>Criptografia por senha (AES-256)</li>
            <li><b>Plugins HTML personalizáveis</b></li>
            <li><b>Temas personalizáveis (cores, fontes, CSS customizado)</b></li>
            <li><b>Plugin de Busca Google incluso automaticamente</b></li>
            <li>Abrir arquivos criptografados e não criptografados</li>
            <li>Localizar e substituir texto</li>
            <li>Contador de caracteres, palavras e linhas</li>
            <li>Zoom ajustável</li>
            <li>Quebra de linha</li>
        </ul>
        
        <h3>Atalhos:</h3>
        <ul>
            <li>Ctrl+N: Novo arquivo</li>
            <li>Ctrl+O: Abrir</li>
            <li>Ctrl+S: Salvar</li>
            <li>Ctrl+E: Salvar Criptografado</li>
            <li><b>Ctrl+P: Adicionar Plugin HTML</b></li>
            <li>Ctrl+F: Localizar</li>
            <li>Ctrl+H: Substituir</li>
            <li>Ctrl+Z: Desfazer</li>
            <li>Ctrl+Y: Refazer</li>
            <li>Ctrl++: Aumentar zoom</li>
            <li>Ctrl+-: Diminuir zoom</li>
        </ul>
        
        <p><i>Desenvolvido com auxílio do DeepSeek</i></p>
        <p><i>Όχι, ο Χρόνος δεν είναι ο άρχοντας της γνώσης</i></p>
        """
        
        QMessageBox.about(self, "Sobre o FlexNotepad", about_text)


class StartupDialog(QDialog):
    """Diálogo inicial com opções"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FlexNotepad")
        self.setModal(True)
        self.setGeometry(400, 300, 500, 350)
        
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("📝 FLEXNOTEPAD\ncom Criptografia 🔒, Plugins 🔌 e Temas 🎨")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #3498db;
            padding: 20px;
            background-color: #ecf0f1;
            border-radius: 10px;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Opções
        options = QWidget()
        options_layout = QVBoxLayout(options)
        
        btn_new = QPushButton("📄 Novo Arquivo")
        btn_new.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 15px;
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 5px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        btn_new.clicked.connect(self.accept)
        options_layout.addWidget(btn_new)
        
        btn_open = QPushButton("📂 Abrir Arquivo")
        btn_open.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 15px;
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        btn_open.clicked.connect(self.open_file)
        options_layout.addWidget(btn_open)
        
        btn_plugin = QPushButton("🔌 Adicionar Plugin")
        btn_plugin.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 15px;
                background-color: #9b59b6;
                color: white;
                border: none;
                border-radius: 5px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        btn_plugin.clicked.connect(self.add_plugin)
        options_layout.addWidget(btn_plugin)
        
        btn_theme = QPushButton("🎨 Criar Tema")
        btn_theme.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 15px;
                background-color: #e67e22;
                color: white;
                border: none;
                border-radius: 5px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        btn_theme.clicked.connect(self.create_theme)
        options_layout.addWidget(btn_theme)
        
        if not CRYPTO_AVAILABLE:
            warning = QLabel("⚠️ Funcionalidade de criptografia não disponível.\nInstale: pip install cryptography")
            warning.setStyleSheet("color: orange; padding: 10px;")
            warning.setAlignment(Qt.AlignCenter)
            options_layout.addWidget(warning)
        
        layout.addWidget(options)
        
        # Botão sair
        btn_exit = QPushButton("❌ Sair")
        btn_exit.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 10px;
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        btn_exit.clicked.connect(self.reject)
        layout.addWidget(btn_exit)
        
        self.setLayout(layout)
        self.open_file_requested = False
        self.add_plugin_requested = False
        self.create_theme_requested = False
    
    def open_file(self):
        """Abrir arquivo diretamente"""
        self.open_file_requested = True
        self.accept()
    
    def add_plugin(self):
        """Adicionar plugin diretamente"""
        self.add_plugin_requested = True
        self.accept()
    
    def create_theme(self):
        """Criar tema diretamente"""
        self.create_theme_requested = True
        self.accept()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("FlexNotepad")
    
    if not CRYPTO_AVAILABLE:
        QMessageBox.warning(None, "Aviso", 
                          "Biblioteca 'cryptography' não instalada.\n"
                          "A funcionalidade de criptografia estará desabilitada.\n\n"
                          "Para instalar: pip install cryptography")
    
    # Diálogo inicial
    dialog = StartupDialog()
    if dialog.exec_() == QDialog.Accepted:
        editor = SimpleTextEditor()
        if dialog.open_file_requested:
            editor.open_file()
        if dialog.add_plugin_requested:
            editor.add_html_plugin()
        if dialog.create_theme_requested:
            editor.create_custom_theme()
        editor.show()
        sys.exit(app.exec_())
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
