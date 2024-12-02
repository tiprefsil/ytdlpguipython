from PyQt5.QtWidgets import (QApplication, QMainWindow, QToolBar, 
                           QPushButton, QVBoxLayout, QWidget,
                           QComboBox, QFileDialog, QMessageBox,
                           QProgressBar)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, Qt, QThread, pyqtSignal
import sys
import subprocess
import os
import argparse
import shutil

class DownloadThread(QThread):
    progress = pyqtSignal(float)
    finished = pyqtSignal(bool, str)

    def __init__(self, comando):
        super().__init__()
        self.comando = comando
        print(f"Comando final: {self.comando}")

    def run(self):
        try:
            print("Iniciando download...")
            if sys.platform == 'win32':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                processo = subprocess.Popen(
                    self.comando,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    bufsize=1,
                    startupinfo=startupinfo,
                    encoding='utf-8'
                )
            else:
                processo = subprocess.Popen(
                    self.comando,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    bufsize=1,
                    encoding='utf-8'
                )
            
            # Processa a saída em tempo real
            for line in processo.stdout:
                line = line.strip()
                print(f"Output: {line}")  # Debug
                
                # Procura por diferentes formatos de progresso
                if '[download]' in line and '%' in line:
                    try:
                        # Extrai a porcentagem do formato "[download]  x.x%"
                        percent_str = line.split('%')[0].split()[-1]
                        percent = float(percent_str)
                        if 0 <= percent <= 100:
                            print(f"Progresso detectado: {percent}%")  # Debug
                            self.progress.emit(percent)
                    except (ValueError, IndexError) as e:
                        print(f"Erro ao processar porcentagem: {e}")
                elif '%' in line:
                    try:
                        # Tenta extrair diretamente a porcentagem
                        percent = float(line.strip().replace('%', ''))
                        if 0 <= percent <= 100:
                            print(f"Progresso detectado: {percent}%")  # Debug
                            self.progress.emit(percent)
                    except ValueError as e:
                        print(f"Erro ao processar porcentagem: {e}")

            # Processa possíveis erros
            erros = processo.stderr.read()
            if erros:
                print(f"Erros encontrados: {erros}")
            
            returncode = processo.wait()
            print(f"Download finalizado com código: {returncode}")
            self.finished.emit(returncode == 0, erros if erros else "")
            
        except Exception as e:
            print(f"Erro no download: {str(e)}")
            self.finished.emit(False, str(e))

class NavegadorPersonalizado(QMainWindow):
    def __init__(self, modo_silencioso=False, formato_silencioso=None):
        super().__init__()
        self.modo_silencioso = modo_silencioso
        self.formato_silencioso = formato_silencioso
        
        # Cria widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Cria layout vertical
        layout = QVBoxLayout(central_widget)
        
        # Cria toolbar
        toolbar = QToolBar()
        
        # Adiciona botão voltar
        self.back_button = QPushButton(" <-- ")
        self.back_button.clicked.connect(self.voltar_pagina)
        toolbar.addWidget(self.back_button)
        
        # Adiciona um separador
        toolbar.addSeparator()
        
        # Adiciona combobox para escolha do formato
        self.formato_combo = QComboBox()
        self.formato_combo.addItems(["MP4", "MP3"])
        toolbar.addWidget(self.formato_combo)
        
        # Adiciona botão de download
        self.download_button = QPushButton("Baixar")
        self.download_button.clicked.connect(self.download_video)
        toolbar.addWidget(self.download_button)
        
        # Adiciona botão de download de playlist
        self.playlist_button = QPushButton("Baixar Playlist")
        self.playlist_button.clicked.connect(self.download_playlist)
        toolbar.addWidget(self.playlist_button)
        
        # Adiciona botão de lista de músicas
        self.lista_button = QPushButton("Lista de Músicas")
        self.lista_button.clicked.connect(self.download_from_list)
        toolbar.addWidget(self.lista_button)
        
        # Adiciona barra de progresso com configuração de range
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 100)
        
        # Cria o navegador
        self.web_view = QWebEngineView()
        
        # Adiciona widgets ao layout
        layout.addWidget(toolbar)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.web_view)
        
        # Configurações da janela
        self.setWindowTitle("Download Rio Vermelho")
        self.setFixedSize(500, 500)
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | 
                          Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)
        
        # Carrega a URL
        self.web_view.setUrl(QUrl("https://youtube.com"))
        
        # Se estiver em modo silencioso, inicia o download automático
        if self.modo_silencioso:
            self.executar_modo_silencioso()
    
    def executar_modo_silencioso(self):
        arquivo_txt = 'musicas.txt'
        if not os.path.exists(arquivo_txt):
            print("Arquivo musicas.txt não encontrado")
            self.close()
            return
            
        # Cria pasta músicas se não existir
        pasta_destino = 'musicas'
        os.makedirs(pasta_destino, exist_ok=True)
        
        try:
            # Configura o formato
            if self.formato_silencioso:
                self.formato_combo.setCurrentText(self.formato_silencioso.upper())
            
            # Lê o arquivo txt
            with open(arquivo_txt, 'r', encoding='utf-8') as f:
                termos_busca = [linha.strip() for linha in f if linha.strip()]
            
            if not termos_busca:
                print("Arquivo musicas.txt está vazio")
                self.close()
                return
                
            formato = self.formato_combo.currentText().lower()
            
            # Monta o comando para pesquisa e download
            if formato == "mp3":
                comando = [
                    'yt-dlp',
                    '--progress-template', '%(progress._percent_str)s',
                    '--newline',
                    '-x',
                    '--audio-format', 'mp3',
                    '--default-search', 'ytsearch1:',
                    '-o', os.path.join(pasta_destino, '%(title)s.%(ext)s'),
                ] + termos_busca
            else:
                comando = [
                    'yt-dlp',
                    '--progress-template', '%(progress._percent_str)s',
                    '--newline',
                    '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                    '--default-search', 'ytsearch1:',
                    '-o', os.path.join(pasta_destino, '%(title)s.%(ext)s'),
                ] + termos_busca
            
            # Configura e inicia o download em thread separada
            self.download_thread = DownloadThread(comando)
            self.download_thread.progress.connect(self.update_progress)
            self.download_thread.finished.connect(self.finalizar_modo_silencioso)
            
            # Inicia o download
            self.download_thread.start()
                
        except Exception as e:
            print(f"Erro no modo silencioso: {str(e)}")
            self.close()
    
    def finalizar_modo_silencioso(self, success, message):
        if success:
            print("Downloads concluídos com sucesso!")
            try:
                # Limpa o arquivo musicas.txt
                open('musicas.txt', 'w').close()
                print("Arquivo musicas.txt limpo")
            except Exception as e:
                print(f"Erro ao limpar arquivo: {str(e)}")
        else:
            print(f"Erro nos downloads: {message}")
        
        # Fecha o aplicativo
        self.close()
    
    def update_progress(self, percent):
        print(f"Progresso atual: {percent}%")  # Debug
        if 0 <= percent <= 100:
            self.progress_bar.setValue(int(percent))
            print(f"Valor definido na barra: {self.progress_bar.value()}")  # Debug

    def download_finished(self, success, message):
        self.progress_bar.setVisible(False)
        if success:
            QMessageBox.information(self, "Sucesso", "Download concluído com sucesso!")
        else:
            QMessageBox.warning(self, "Erro", f"Erro no download: {message}")
        
        self.download_button.setEnabled(True)
        self.playlist_button.setEnabled(True)
        self.lista_button.setEnabled(True)

    def download_video(self):
        url = self.web_view.url().toString()
        formato = self.formato_combo.currentText().lower()
        
        try:
            # Configuração para ocultar o prompt
            startupinfo = None
            if sys.platform == 'win32':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

            # Obtém o título do vídeo com prompt oculto
            comando_titulo = [
                'yt-dlp',
                '--get-title',
                url
            ]
            titulo = subprocess.check_output(
                comando_titulo, 
                universal_newlines=True,
                startupinfo=startupinfo,
                encoding='utf-8',
                errors='replace'
            ).strip()
            
            # Remove caracteres inválidos do título
            titulo = "".join(c for c in titulo if c.isalnum() or c in (' ', '-', '_')).strip()
            
            # Define o nome do arquivo padrão
            nome_arquivo_padrao = f"{titulo}.{formato}"
            
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Salvar Arquivo",
                os.path.join(os.path.expanduser("~/Downloads"), nome_arquivo_padrao),
                f"Arquivos {formato.upper()} (*.{formato})"
            )
            
            if filename:
                if formato == "mp3":
                    comando = [
                        'yt-dlp',
                        '--progress',
                        '--newline',
                        '--progress-template', '[download] %(progress._percent_str)s',
                        '-x',
                        '--audio-format', 'mp3',
                        '-o', filename,
                        url
                    ]
                else:
                    comando = [
                        'yt-dlp',
                        '--progress',
                        '--newline',
                        '--progress-template', '[download] %(progress._percent_str)s',
                        '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                        '-o', filename,
                        url
                    ]
                
                print(f"Comando a ser executado: {comando}")  # Debug
                
                # Configura e inicia o download em thread separada
                self.download_thread = DownloadThread(comando)
                self.download_thread.progress.connect(self.update_progress)
                self.download_thread.finished.connect(self.download_finished)
                
                # Prepara a interface
                self.progress_bar.setVisible(True)
                self.progress_bar.setValue(0)
                self.download_button.setEnabled(False)
                self.playlist_button.setEnabled(False)
                self.lista_button.setEnabled(False)
                
                # Inicia o download
                self.download_thread.start()
                    
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao baixar: {str(e)}")
            
    def download_playlist(self):
        url = self.web_view.url().toString()
        formato = self.formato_combo.currentText().lower()
        
        try:
            # Configuração para ocultar o prompt
            startupinfo = None
            if sys.platform == 'win32':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

            # Verifica se é uma playlist válida com prompt oculto
            comando_check = [
                'yt-dlp',
                '--flat-playlist',
                '--dump-json',
                url
            ]
            
            try:
                subprocess.check_output(
                    comando_check, 
                    universal_newlines=True,
                    startupinfo=startupinfo
                )
            except subprocess.CalledProcessError:
                QMessageBox.warning(self, "Erro", "URL não é uma playlist válida!")
                return
            
            # Pede o diretório para salvar a playlist
            pasta_destino = QFileDialog.getExistingDirectory(
                self,
                "Selecione a pasta para salvar a playlist",
                os.path.expanduser("~/Downloads"),
                QFileDialog.ShowDirsOnly
            )
            
            if pasta_destino:
                if formato == "mp3":
                    comando = [
                        'yt-dlp',
                        '--progress-template', '%(progress._percent_str)s',
                        '--newline',
                        '-x',
                        '--audio-format', 'mp3',
                        '--yes-playlist',
                        '-o', os.path.join(pasta_destino, '%(title)s.%(ext)s'),
                        url
                    ]
                else:
                    comando = [
                        'yt-dlp',
                        '--progress-template', '%(progress._percent_str)s',
                        '--newline',
                        '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                        '--yes-playlist',
                        '-o', os.path.join(pasta_destino, '%(title)s.%(ext)s'),
                        url
                    ]
                
                print(f"Comando a ser executado: {comando}")  # Debug
                
                # Configura e inicia o download em thread separada
                self.download_thread = DownloadThread(comando)
                self.download_thread.progress.connect(self.update_progress)
                self.download_thread.finished.connect(self.download_finished)
                
                # Prepara a interface
                self.progress_bar.setVisible(True)
                self.progress_bar.setValue(0)
                self.download_button.setEnabled(False)
                self.playlist_button.setEnabled(False)
                self.lista_button.setEnabled(False)
                
                # Inicia o download
                self.download_thread.start()
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao baixar playlist: {str(e)}")

    def download_from_list(self):
        # Abre diálogo para selecionar arquivo .txt
        arquivo_txt, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar arquivo de lista",
            os.path.expanduser("~/Downloads"),
            "Arquivos de texto (*.txt)"
        )
        
        if not arquivo_txt:
            return
            
        try:
            # Seleciona pasta de destino
            pasta_destino = QFileDialog.getExistingDirectory(
                self,
                "Selecione a pasta para salvar as músicas",
                os.path.expanduser("~/Downloads"),
                QFileDialog.ShowDirsOnly
            )
            
            if not pasta_destino:
                return
                
            formato = self.formato_combo.currentText().lower()
            
            # Lê o arquivo txt
            with open(arquivo_txt, 'r', encoding='utf-8') as f:
                termos_busca = [linha.strip() for linha in f if linha.strip()]
            
            # Monta o comando para pesquisa e download
            if formato == "mp3":
                comando = [
                    'yt-dlp',
                    '--progress-template', '%(progress._percent_str)s',
                    '--newline',
                    '-x',
                    '--audio-format', 'mp3',
                    '--default-search', 'ytsearch1:',  # Limita a 1 resultado por pesquisa
                    '-o', os.path.join(pasta_destino, '%(title)s.%(ext)s'),
                ] + termos_busca  # Adiciona todos os termos de busca ao comando
            else:
                comando = [
                    'yt-dlp',
                    '--progress-template', '%(progress._percent_str)s',
                    '--newline',
                    '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                    '--default-search', 'ytsearch1:',  # Limita a 1 resultado por pesquisa
                    '-o', os.path.join(pasta_destino, '%(title)s.%(ext)s'),
                ] + termos_busca
            
            # Configura e inicia o download em thread separada
            self.download_thread = DownloadThread(comando)
            self.download_thread.progress.connect(self.update_progress)
            self.download_thread.finished.connect(self.download_finished)
            
            # Prepara a interface
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.download_button.setEnabled(False)
            self.playlist_button.setEnabled(False)
            self.lista_button.setEnabled(False)
            
            # Inicia o download
            self.download_thread.start()
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao processar lista: {str(e)}")

    def contextMenuEvent(self, event):
        # Sobrescreve o evento do menu de contexto para não fazer nada
        pass

    def voltar_pagina(self):
        """Função para voltar uma página no navegador"""
        self.web_view.back()

def main():
    # Configura o parser de argumentos
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--silent', help='formato para modo silencioso (mp3 ou mp4)')
    args = parser.parse_args()
    
    app = QApplication(sys.argv)
    
    # Verifica se está em modo silencioso
    modo_silencioso = bool(args.silent)
    formato_silencioso = args.silent
    
    window = NavegadorPersonalizado(modo_silencioso, formato_silencioso)
    
    if not modo_silencioso:
        window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
