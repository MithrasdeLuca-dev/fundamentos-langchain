# 5. Loaders e banco de dados vetoriais

Esta pasta apresenta a primeira parte de um fluxo de RAG (Retrieval-Augmented Generation): carregar fontes, dividir documentos, gerar embeddings, armazenar vetores e buscar trechos semanticamente semelhantes.

## Fluxo estudado

```text
fonte → loader → documentos → chunks → embeddings → PGVector → busca semântica
```

## Exemplos

### `1-carregamento-usando-WebBaseLoader copy.py`

Usa `WebBaseLoader` para baixar o conteúdo de `https://www.langchain.com/`. Em seguida, `RecursiveCharacterTextSplitter` divide os documentos em partes de até 500 caracteres, com sobreposição de 100.

A sobreposição reduz a chance de uma informação ser cortada entre dois chunks. O nome do arquivo contém espaços; ao executá-lo no shell, coloque o caminho entre aspas.

```bash
python "5-loaders-e-banco-de-dados-vetoriais/1-carregamento-usando-WebBaseLoader copy.py"
```

### `2-carregamento-de-pdf.py`

Carrega `gpt5.pdf` com `PyPDFLoader` e divide o conteúdo em chunks. O exemplo imprime a quantidade de partes criadas.

### `3-ingestion-pgvector.py`

Implementa a ingestão no PostgreSQL com extensão/vector store PGVector:

1. carrega o PDF;
2. divide as páginas em chunks de 1000 caracteres;
3. limpa metadados vazios;
4. gera embeddings com `OpenAIEmbeddings`;
5. grava documentos e vetores na coleção definida por `PGVECTOR_COLLECTION`.

Os embeddings representam o significado do texto como vetores numéricos. O banco consegue comparar esses vetores para encontrar conteúdo semanticamente parecido.

### `4-search-vector.py`

Gera o embedding de uma pergunta e executa `similarity_search_with_score()` no PGVector. O script imprime os três resultados mais semelhantes, suas pontuações e metadados.

## Variáveis de ambiente

Configure no `.env`:

```dotenv
OPENAI_API_KEY=sua_chave
OPENAI_MODEL=text-embedding-3-small
PGVECTOR_URL=postgresql+psycopg://postgres:postgres@localhost:5432/rag
PGVECTOR_COLLECTION=gpt5_collection
```

O PostgreSQL precisa estar acessível e preparado para armazenar vetores. Os scripts 3 e 4 falham de propósito com uma mensagem clara quando uma dessas variáveis não está definida.

## Conceitos principais

- **Document loader**: transforma uma fonte externa em objetos `Document`;
- **Document**: conteúdo textual acompanhado de metadados;
- **chunking**: divisão do conteúdo para processamento e recuperação;
- **embedding**: representação vetorial do significado do texto;
- **vector store**: banco que armazena e compara embeddings;
- **similarity search**: busca pelos vetores mais próximos da consulta;
- **RAG**: recuperação de contexto relevante antes de gerar uma resposta.

## Dependências e custo

Esta pasta possui um `requirements.txt` próprio, baseado em versões anteriores do projeto. O arquivo da raiz pode conter versões diferentes; escolha um ambiente consistente antes de instalar.

Os exemplos de ingestão e busca usam a API da OpenAI para embeddings e, portanto, podem gerar custo e exigir faturamento ativo. O loader web também depende de internet. O PDF `gpt5.pdf` deve permanecer nesta pasta para o caminho relativo funcionar.

## Explicação detalhada

### O que é um loader?

Um loader é o adaptador entre uma fonte de dados e o formato `Document` do LangChain. Cada fonte possui um loader específico:

- `WebBaseLoader` baixa e extrai texto de uma página web;
- `PyPDFLoader` lê páginas de um arquivo PDF.

O resultado não é ainda um vetor nem uma resposta. É apenas conteúdo estruturado, geralmente com texto e metadados de origem.

### Por que dividir documentos?

Modelos e embeddings trabalham melhor quando recebem partes controláveis do conteúdo. Um PDF inteiro pode ser grande demais para uma chamada e uma página inteira pode misturar assuntos diferentes.

`RecursiveCharacterTextSplitter` tenta dividir respeitando separadores naturais, como parágrafos e quebras de linha. No exemplo:

```python
RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=150,
)
```

Cada chunk tem aproximadamente até 1000 caracteres e compartilha cerca de 150 caracteres com o próximo. Esse compartilhamento preserva contexto nas fronteiras.

### O que é um embedding?

Um embedding é uma lista de números que representa características semânticas de um texto. Textos relacionados tendem a produzir vetores próximos no espaço matemático.

Por exemplo, uma consulta sobre “avaliação do GPT-5” pode ficar próxima de um trecho que usa as palavras “benchmark de desempenho”, mesmo que as frases não sejam idênticas.

O modelo usado no exemplo é configurado por `OPENAI_MODEL`, com `text-embedding-3-small` como valor padrão. O embedding não é a resposta final de um chatbot; ele é usado para localizar contexto relevante.

### O que acontece na ingestão?

O arquivo `3-ingestion-pgvector.py` executa a preparação inicial da base:

1. carrega `gpt5.pdf`;
2. transforma suas páginas em `Document`;
3. divide os documentos em chunks;
4. remove metadados vazios;
5. cria IDs determinísticos como `doc-0`, `doc-1` e assim por diante;
6. gera um embedding para cada chunk;
7. insere textos, metadados e vetores na coleção PGVector.

O `Document` continua armazenando o texto original. O vetor é um índice semântico adicional, não uma substituição do conteúdo.

### Por que usar metadados?

Metadados permitem rastrear a origem do resultado. No PDF, podem indicar página, arquivo ou posição do trecho. Depois da busca, esses dados ajudam a mostrar a fonte ao usuário ou filtrar resultados por documento.

O código cria uma nova lista `enriched` para remover valores vazios, mantendo somente metadados úteis.

### O que é o PGVector?

PGVector é uma extensão/ecossistema que permite armazenar vetores no PostgreSQL. O objeto `PGVector` recebe:

- o modelo de embeddings;
- o nome da coleção;
- a URL de conexão;
- a opção de usar JSONB para metadados.

Na primeira execução, o banco precisa estar disponível e a coleção pode ser criada pelo próprio componente, conforme a versão instalada. Executar a ingestão novamente com os mesmos IDs pode exigir uma estratégia de atualização ou limpeza para evitar duplicações/conflitos.

### Como funciona a busca semântica?

No arquivo `4-search-vector.py`, a pergunta também é transformada em embedding. Depois, `similarity_search_with_score(query, k=3)` compara esse vetor com os vetores armazenados e retorna os três candidatos mais próximos.

Cada resultado contém:

```python
(document, score)
```

O `document` traz o texto e os metadados; `score` representa a medida de similaridade/distância usada pela integração. A interpretação exata de “maior” ou “menor” depende da métrica e da versão do vector store, por isso o valor deve ser tratado como um indicador de ordenação, não como uma probabilidade.

### Isso já é um sistema RAG completo?

Ainda não. A pasta implementa principalmente a etapa de recuperação:

```text
pergunta → embedding da pergunta → busca vetorial → documentos relevantes
```

Um RAG completo adicionaria um modelo de chat depois da busca, colocaria os documentos retornados em um prompt e pediria uma resposta fundamentada nesse contexto:

```text
pergunta → busca → contexto recuperado → prompt → modelo → resposta
```

### Por que há dois arquivos de dependências?

O `requirements.txt` desta pasta foi congelado em uma versão anterior do curso, enquanto o `requirements.txt` da raiz contém versões mais recentes. Misturar os dois conjuntos no mesmo ambiente pode causar incompatibilidades, principalmente em imports e APIs do LangChain. Para reproduzir exatamente os exemplos desta pasta, use um ambiente separado e instale o arquivo local; para continuar o projeto atual, mantenha uma única estratégia de versões.
