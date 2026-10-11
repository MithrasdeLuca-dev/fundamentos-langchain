# Fundamentos LangChain

Exemplos introdutórios de uso do LangChain com modelos do Google Gemini.

## Pré-requisitos

- Python 3.10 ou superior
- Uma chave de API do Google Gemini
- Git, opcionalmente, para clonar o projeto

## Configuração do ambiente

Execute os comandos a partir da raiz do projeto.

### Linux/macOS

Crie e ative um ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

No Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Com o ambiente virtual ativado, instale as dependências:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Quando o ambiente estiver ativado, o terminal normalmente exibirá `(.venv)`
no início da linha. Para sair dele:

```bash
deactivate
```

## Variáveis de ambiente

O projeto usa o pacote `python-dotenv`. Os scripts chamam `load_dotenv()` e
carregam as variáveis do arquivo `.env` localizado na raiz do projeto.

Crie o arquivo `.env` copiando o modelo:

```bash
cp .env.example .env
```

No Windows PowerShell, use:

```powershell
Copy-Item .env.example .env
```

Depois, abra o arquivo `.env` e substitua os valores de exemplo:

```dotenv
# Obrigatória para os exemplos com Google Gemini
GOOGLE_API_KEY=sua_chave_do_google_gemini

# Usadas por exemplos futuros com OpenAI e PostgreSQL/pgvector
OPENAI_API_KEY=sua_chave_da_openai
OPENAI_MODEL=text-embedding-3-small
PGVECTOR_URL=postgresql+psycopg://postgres:postgres@localhost:5432/rag
PGVECTOR_COLLECTION=gpt5_collection
```

Para obter uma chave do Gemini, acesse o [Google AI Studio](https://aistudio.google.com/app/apikey).

Nunca compartilhe nem versione o arquivo `.env`. Ele já está listado no
`.gitignore`; use `.env.example` apenas como modelo, sem chaves reais.

## Executando os exemplos

Com o ambiente virtual ativado e o `.env` configurado:

```bash
python 1-fundamentos/hello-word.py
python 1-fundamentos/2-init-chat-model.py
python 1-fundamentos/3-prompt-template.py
python 1-fundamentos/4-chat-prompr-template.py
python 2-chains-e-processamentos/1-iniciando-com-chains.py
```

Os exemplos que chamam o Gemini precisam de uma `GOOGLE_API_KEY` válida e de
acesso à internet. O exemplo `3-prompt-template.py` apenas formata um prompt e
não faz uma chamada ao modelo.

## Desativando e reativando o ambiente virtual

Ao abrir um novo terminal, ative novamente o ambiente:

```bash
source .venv/bin/activate
```

No Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```
