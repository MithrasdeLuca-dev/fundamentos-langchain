# 3. Agentes e tools

Esta pasta demonstra agentes ReAct e ferramentas personalizadas. Um agente recebe uma tarefa, decide se precisa usar uma ferramenta, observa o resultado e então produz a resposta final.

## Pré-requisitos

Os exemplos atuais usam `ChatOpenAI`, portanto precisam de uma `OPENAI_API_KEY` válida no `.env` e de acesso à API da OpenAI:

```bash
source venv/bin/activate
python 3-agentes-tools/1-agente-react-e-tools.py
```

Uma assinatura do ChatGPT não substitui automaticamente a cobrança da API; ChatGPT e API possuem faturamentos separados.

## `1-agente-react-e-tools.py`

Define duas ferramentas com o decorator `@tool`:

- `calculator`: calcula uma expressão matemática;
- `web_search_mock`: simula uma busca de capitais usando um dicionário local.

O agente é criado com `create_react_agent()` e executado por `AgentExecutor`. O executor controla o ciclo de raciocínio e uso das ferramentas:

```text
pergunta → Thought → Action → ferramenta → Observation → resposta
```

O prompt instrui o agente a usar somente as informações retornadas pelas ferramentas. `max_iterations=3` evita que o agente fique executando indefinidamente.

## `2-agente-react-usando-prompt-hub.py`

Mostra uma variação que obtém um prompt ReAct pronto pelo LangChain Hub:

```python
prompt = hub.pull("hwchase17/react")
```

Nesse exemplo, o agente recebe somente a ferramenta de busca simulada.

## Conceitos principais

- **Tool**: função que o modelo pode escolher chamar;
- **Agent**: componente que decide quais ações executar;
- **ReAct**: alternância entre raciocínio, ação e observação;
- **AgentExecutor**: coordena o agente e as ferramentas;
- **Prompt Hub**: reutilização de prompts publicados;
- **mock**: ferramenta falsa usada para estudar o fluxo sem acessar a internet.

## Cuidados de segurança

`calculator` usa `eval()` apenas para fins didáticos. Nunca aceite expressões arbitrárias de usuários em produção dessa forma, pois `eval()` pode executar código indevido. Use um parser matemático seguro ou permita somente operações explicitamente validadas.

## Explicação detalhada

### O que diferencia um agente de uma chain?

Em uma chain, o fluxo normalmente é conhecido antes da execução. Por exemplo: traduzir e depois resumir sempre segue as mesmas etapas.

Em um agente, o modelo escolhe durante a execução se precisa de uma ferramenta e qual ferramenta usar. O código fornece as ferramentas disponíveis, mas a decisão depende da pergunta.

No primeiro exemplo:

- para `How much is 10 + 10?`, o agente deve escolher `calculator`;
- para uma pergunta sobre um país conhecido pelo mock, pode escolher `web_search_mock`;
- para uma capital que não está no dicionário, a ferramenta retorna que não sabe.

### O que é uma tool?

Uma tool é uma função que o agente pode chamar. O decorator `@tool` transforma a função em um objeto com nome, descrição e esquema de entrada.

Por exemplo:

```python
@tool("web_search_mock")
def web_search_mock(query: str) -> str:
    """Return the capital of a given country if it exists in the mock data."""
```

O nome identifica a ferramenta. A anotação `query: str` informa o tipo esperado. A docstring ajuda o modelo a entender quando a ferramenta deve ser usada.

Apesar do nome `web_search_mock`, ela não acessa a web. Ela apenas procura nomes de países em um dicionário local. Isso foi feito para estudar o comportamento do agente sem depender de um serviço externo.

### Como o ReAct toma uma decisão?

O prompt define o formato do ciclo:

```text
Question → Thought → Action → Action Input → Observation → Final Answer
```

1. **Question**: pergunta recebida pelo executor;
2. **Thought**: decisão interna sobre o próximo passo;
3. **Action**: nome da tool escolhida;
4. **Action Input**: argumento enviado à tool;
5. **Observation**: resultado devolvido pela função;
6. **Final Answer**: resposta que será mostrada ao usuário.

Se a primeira observação não for suficiente, o agente pode repetir o ciclo. `max_iterations=3` limita essa repetição.

### O papel do `AgentExecutor`

`create_react_agent()` cria o agente, que contém o prompt e o modelo. `AgentExecutor` é o componente que efetivamente coordena a execução: recebe a pergunta, envia o prompt ao modelo, localiza a tool escolhida, chama a função, devolve a observação ao agente e repete até obter uma resposta final.

`verbose=True` imprime esse processo no terminal, tornando o exemplo útil para acompanhar o raciocínio operacional do agente.

### Por que há tratamento de erro de parsing?

O agente ReAct precisa respeitar o formato definido no prompt. Se o modelo produzir texto fora do padrão esperado, o executor pode não conseguir identificar `Action` e `Action Input`. `handle_parsing_errors` transforma esse caso em uma mensagem controlada para permitir uma nova tentativa, em vez de encerrar imediatamente.

### O que muda no exemplo com Prompt Hub?

No primeiro arquivo, o prompt ReAct é escrito no próprio código. No segundo, `hub.pull("hwchase17/react")` baixa um prompt compartilhado do LangChain Hub.

O restante do fluxo continua parecido: registrar tools, criar o agente e passá-lo para um `AgentExecutor`. A diferença demonstra como separar o prompt da aplicação e reutilizar uma configuração pronta.
