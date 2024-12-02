nos meus testes rodar diretamente com python a velocidade é bem maior, principalmente quando for baixar uma playlist ja que a requisição para capturar o nome de todas as musicas é um pouco demorada.

a versao de windows so foi compilada para casos bem especificos.

adicionei uma opção via linha de comando bara baixar sem interferencia do usuario

adicione -s [mp3 - mp4] e os nomes das musicas no arquivo musicas.txt, todas as musicas baixadas vao para a pasta musicas.
adicionei essa opção para funcionar em um servidor de uma radio

app.exe -s mp3
app.exe -s mp4
python3 app.py -s mp3
python3 app.py -s mp4

funciona no modo silencioso e nenhuma interface é mostrada.
