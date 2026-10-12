# 1. Fundamentos

Esta pasta apresenta os conceitos básicos para conversar com modelos de linguagem usando LangChain: inicialização de modelos, criação de prompts e organização de mensagens de chat.

## Pré-requisitos

Execute os exemplos a partir da raiz do projeto, com o ambiente virtual ativado e uma variável `GOOGLE_API_KEY` configurada no arquivo `.env`:

```bash
source venv/bin/activate
python 1-fundamentos/hello-word.py
```

Os exemplos que chamam o Gemini precisam de internet e de uma chave válida. O arquivo `3-prompt-template.py` apenas monta e imprime um prompt; ele não faz uma chamada ao modelo.

## Exemplos

### `hello-word.py`

Cria um `ChatGoogleGenerativeAI` e envia uma mensagem simples com `invoke()`.

Conceitos utilizados:

- `ChatGoogleGenerativeAI`: integração entre LangChain e o Gemini;
- `temperature`: controla a variação das respostas;
- `invoke()`: executa o modelo para uma entrada;
- `AIMessage.content`: acessa o texto retornado pelo modelo.

### `2-init-chat-model.py`

Mostra a inicialização genérica com `init_chat_model()`. O provedor (`google_genai`) é informado separadamente do nome do modelo.

Essa abordagem facilita trocar o provedor sem alterar a estrutura principal do código.

### `3-prompt-template.py`

Usa `PromptTemplate` para definir um texto com a variável `{name}` e preenchê-la com `format()`.

O template separa a instrução fixa dos dados variáveis. Isso evita concatenar strings manualmente e permite reutilizar o mesmo prompt com diferentes entradas.

### `4-chat-prompr-template.py`

Usa `ChatPromptTemplate` para montar uma conversa com duas mensagens:

- `system`: define o comportamento e o estilo do assistente;
- `user`: contém a pergunta do usuário.

Depois de preencher as variáveis, as mensagens são enviadas ao modelo. Essa estrutura é adequada para prompts de chat com papéis distintos.

## Fluxo geral

```text
entrada/variáveis → template de prompt → mensagens → modelo → resposta
```

## Observação

Os nomes dos modelos e os limites de uso podem mudar. Se o Gemini retornar erro `429 RESOURCE_EXHAUSTED`, a cota da API foi atingida; isso não indica um problema no template ou no código Python.

## Explicação detalhada

### O que é um modelo de chat?

Um modelo de chat recebe mensagens e devolve uma mensagem. Mesmo quando enviamos apenas uma string, a integração transforma essa entrada no formato de mensagens esperado pelo provedor.

No projeto, a chamada básica é:

```python
response = model.invoke("Hello, how are you?")
print(response.content)
```

`invoke()` é uma execução síncrona: o programa espera o modelo responder. O objeto retornado contém mais informações além do texto, como metadados e, dependendo do provedor, dados de uso de tokens. `content` é somente o conteúdo textual que queremos exibir.

### O que é `PromptTemplate`?

`PromptTemplate` é um molde de texto com campos nomeados. No exemplo, o molde é:

```text
Hi, I'm {name}! Tell me a joke with my name!
```

Quando o código executa `template.format(name="Mithras")`, o valor substitui `{name}` e o resultado é uma string comum. Nesse arquivo ainda não existe chamada ao modelo: o objetivo é visualizar a etapa de preparação do prompt isoladamente.

### O que é `ChatPromptTemplate`?

Um `ChatPromptTemplate` representa uma conversa com papéis. O exemplo cria:

1. uma mensagem `system`, que diz ao modelo para responder em determinado estilo;
2. uma mensagem `user`, que contém a pergunta;
3. valores para `{style}` e `{question}`;
4. uma lista de mensagens pronta para ser enviada ao Gemini.

Essa separação é importante porque instruções do sistema e perguntas do usuário têm finalidades diferentes. O sistema define comportamento; o usuário fornece a solicitação concreta.

### Por que existem dois modos de inicializar o modelo?

`ChatGoogleGenerativeAI` instancia diretamente a integração com o Google. Já `init_chat_model()` usa uma função genérica e recebe o provedor em `model_provider`. O segundo formato torna mais explícita a ideia de que a aplicação pode trocar de provedor mantendo a mesma interface `invoke()`.

### O papel de `temperature`

`temperature=0` tende a produzir respostas mais previsíveis, útil para tradução, classificação e testes. Valores maiores, como `0.5`, permitem mais variação e criatividade. A temperatura não transforma um modelo em mais inteligente; ela altera a distribuição das respostas possíveis.
