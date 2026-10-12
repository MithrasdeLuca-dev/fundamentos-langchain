# 4. Gerenciamento de memória

Esta pasta mostra como manter histórico de conversas e como limitar esse histórico para controlar o tamanho do contexto enviado ao modelo.

## Pré-requisitos

Os scripts usam `ChatOpenAI`, por isso precisam de `OPENAI_API_KEY` no `.env`:

```bash
source venv/bin/activate
python 4-gerenciamento-de-memoria/1-armazenamento-de-historico.py
```

## `1-armazenamento-de-historico.py`

Cria um `InMemoryChatMessageHistory` para cada `session_id` e conecta o histórico ao pipeline com `RunnableWithMessageHistory`.

As mensagens são inseridas automaticamente no placeholder `{history}` do prompt. Como as três chamadas usam a sessão `demo-session`, o modelo consegue recuperar o nome informado na primeira interação.

Conceitos utilizados:

- `MessagesPlaceholder`: ponto do prompt onde o histórico será inserido;
- `InMemoryChatMessageHistory`: armazenamento temporário de mensagens;
- `RunnableWithMessageHistory`: wrapper que gerencia histórico por sessão;
- `session_id`: identifica uma conversa independente.

## `2-historico-baseado-em-sliding-window.py`

Aplica uma janela deslizante ao histórico com `trim_messages()`. O código conserva apenas as mensagens mais recentes, respeitando `max_tokens=2` no exemplo didático.

O fluxo usa `RunnableLambda` para preparar a entrada antes do prompt:

```text
histórico completo → trim_messages → histórico reduzido → prompt → modelo
```

Essa técnica reduz custo e evita estourar a janela de contexto, mas pode remover informações antigas importantes.

## Limitações

O histórico é mantido somente em um dicionário Python:

```python
session_store: dict[str, InMemoryChatMessageHistory] = {}
```

Ele é perdido quando o processo termina e não funciona como armazenamento compartilhado entre múltiplas instâncias. Em produção, substitua-o por uma implementação persistente, como Redis, PostgreSQL ou outro banco apropriado.

## Explicação detalhada

### O modelo tem memória própria?

Não. O modelo não lembra automaticamente de chamadas anteriores. Cada chamada precisa receber no prompt as mensagens que devem ser consideradas.

Neste projeto, a “memória” é o código que guarda as mensagens e as inclui novamente na próxima solicitação. O modelo apenas recebe o histórico anexado àquela chamada.

### Como a sessão funciona?

O dicionário `session_store` associa um identificador a um histórico:

```python
session_store["demo-session"] = InMemoryChatMessageHistory()
```

Quando `get_session_history("demo-session")` é chamado novamente, o mesmo objeto é devolvido. Se outro identificador for usado, uma conversa independente será criada.

Isso permite que vários usuários tenham históricos separados:

```text
user-1 → histórico A
user-2 → histórico B
```

### O que faz `RunnableWithMessageHistory`?

Esse wrapper recebe uma chain normal e adiciona o gerenciamento do histórico. No exemplo:

```python
conversational_chain = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)
```

O wrapper realiza, conceitualmente, estas operações:

1. lê `session_id` na configuração;
2. obtém o histórico usando `get_session_history`;
3. coloca esse histórico no `MessagesPlaceholder("history")`;
4. envia o prompt completo ao modelo;
5. registra a nova mensagem do usuário e a resposta do modelo.

Por isso as chamadas seguintes conseguem responder a perguntas como “qual é o meu nome?”.

### Por que usar `MessagesPlaceholder`?

O histórico tem quantidade variável de mensagens. `MessagesPlaceholder` reserva um ponto do prompt para inserir uma lista de mensagens sem precisar montar manualmente o texto a cada chamada.

O prompt final fica parecido com:

```text
system: You are a helpful assistant.
human: Hello, my name is Wesley.
ai: ...
human: Can you repeat my name?
```

### O que é uma janela deslizante?

Conversas longas podem ultrapassar a janela de contexto e aumentar o custo. `trim_messages()` seleciona somente uma parte do histórico, normalmente as mensagens mais recentes.

No segundo arquivo, `strategy="last"` prioriza o final da conversa. `start_on="human"` evita começar a lista aparada com uma resposta do assistente sem a pergunta correspondente. `include_system=True` preserva a instrução de sistema.

O parâmetro `max_tokens=2` foi escolhido para tornar o efeito visível no exemplo; em uma aplicação real, o valor deve ser calibrado para o modelo e para o tamanho das mensagens.

### O que faz `RunnableLambda` nesse exemplo?

`prepare_inputs` recebe o payload produzido pelo wrapper, lê `raw_history`, aplica `trim_messages()` e devolve um novo dicionário com `input` e `history`. `RunnableLambda(prepare_inputs)` transforma essa função em uma etapa LCEL:

```text
payload com histórico bruto → prepare → prompt → modelo
```

O nome `raw_history` é usado na configuração do wrapper, enquanto o nome `history` é o campo esperado pelo `MessagesPlaceholder` depois da preparação.

### O que acontece quando o processo termina?

Como o projeto usa `InMemoryChatMessageHistory`, todas as sessões desaparecem ao fechar o Python. Isso é adequado para experimentos, mas não para uma aplicação real. Um armazenamento persistente também deve considerar expiração, privacidade, isolamento por usuário e limite de tamanho do histórico.
