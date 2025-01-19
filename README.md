# Zarea de Risco

**Zarea de Risco** é um projeto voltado para a segurança pública do estado do Ceará, focando na coleta e análise de notícias e informações relevantes para a área. O nome "Zarea de Risco" é uma expressão originária da região, comumente usada entre os mais jovens para se referir a áreas de risco, como locais perigosos ou com alta vulnerabilidade.

O projeto visa ajudar no monitoramento e na disseminação de informações que podem contribuir para a segurança pública e prevenção de riscos.

## Objetivo

O objetivo principal do projeto é coletar notícias e dados sobre segurança pública no Ceará, analisá-los e gerar relatórios úteis para as autoridades e a população. A partir de dados coletados em plataformas como o Telegram e outras fontes, o projeto permite uma visão mais detalhada e organizada sobre questões de segurança.

## Tecnologias Usadas

- **Python**(backend):
- **Javacript**(frontend): 
- **MinIO**: 
- **Docker**:
- **Flask**:
- **React + Vite**:
  
## Funcionalidades

- Coleta de notícias e informações em tempo real.
- Armazenamento e organização de dados coletados.
- Análise de conteúdos com foco em segurança pública.
  
## Como rodar o backend

1. Clone este repositório:
```bash
git clone https://github.com/nycolasdiaas/zarea-de-risco.git
```

2. Crie um ambiente virtual (opcional):
```bash
python3 -m venv .venv
```
2.1 Ative o ambiente virtual:

```bash
source .venv/bin/activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Para rodar localmente:
```bash
flask --app backend/app.py --debug run 
```

4.1 No docker:
```bash
cd ./backend/
docker compose up --build
```
