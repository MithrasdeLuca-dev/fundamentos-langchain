# 2. Chains e processamentos

Esta pasta mostra como combinar componentes LangChain em pipelines reutilizáveis. O foco é a LCEL (LangChain Expression Language), na qual prompts, modelos, parsers e funções são conectados com o operador `|`.

## Como executar

Na raiz do projeto, com o ambiente virtual ativado:

```bash
source venv/bin/activate
python 2-chains-e-processamentos/1-iniciando-com-chains.py
```

Os exemplos que usam Gemini precisam de `GOOGLE_API_KEY` no `.env`. Os exemplos de sumarização podem fazer várias chamadas ao modelo, especialmente os exemplos map-reduce e pipeline; uma API gratuita pode atingir a cota rapidamente.

## Exemplos

### `1-iniciando-com-chains.py`

Combina `PromptTemplate` e modelo:

```python
chain = question_template | model
```

O dicionário recebido por `invoke()` preenche o template e o resultado é encaminhado ao modelo.

Conceitos: composição LCEL, entrada estruturada e passagem de dados entre etapas.

### `2-iniciando-com-chains-com-decorators.py`

Transforma uma função Python em uma chain com o decorator `@chain`. A função calcula o quadrado de um número e entrega um dicionário para o próximo prompt.

```text
{x} → square → {square_result} → prompt → modelo
```

Isso demonstra que uma chain pode conter lógica própria, e não apenas componentes de IA.

### `3-runnable-lambda.py`

Usa `RunnableLambda` para adaptar uma função comum ao protocolo Runnable do LangChain. O texto `"10"` é convertido para o inteiro `10` por meio de `invoke()`.

### `4-pipeline-de-processamento.py`

Cria um pipeline com duas etapas de modelo:

1. traduz o texto para inglês;
2. resume o texto traduzido em quatro palavras.

`StrOutputParser` converte a resposta do modelo em uma string simples, facilitando sua passagem para a etapa seguinte.

### `5-sumarizacao.py`

Divide um texto longo em documentos menores usando `RecursiveCharacterTextSplitter` e resume os documentos com `load_summarize_chain(..., chain_type="stuff")`.

O tipo `stuff` coloca todos os documentos no mesmo prompt. É simples, mas pode exceder o limite de contexto quando o texto for grande. Como o LangChain 1.x moveu as chains legadas, o exemplo importa a função de `langchain_classic`.

### `6-sumarizacao-com-map-reduce.py`

Aplica o padrão map-reduce:

1. **map**: gera um resumo para cada trecho;
2. **reduce**: combina os resumos em um resumo final.

Esse padrão suporta textos maiores, mas faz várias chamadas ao modelo e pode consumir mais cota.

### `7-pipeline-sumarizacao.py`

Implementa manualmente o fluxo map-reduce com LCEL:

- `RunnableLambda` prepara cada `Document`;
- `.map()` executa a etapa de resumo para cada trecho;
- outra chain combina os resumos;
- `StrOutputParser` retorna texto puro.

O `.map()` pode disparar chamadas em paralelo. Para reduzir simultaneidade, é possível usar:

```python
pipeline.invoke(parts, config={"max_concurrency": 1})
```

Isso ajuda com limites por minuto, mas não aumenta uma cota diária já esgotada.

## Conceitos principais

- **Chain**: sequência de etapas executadas como uma unidade;
- **Runnable**: componente que pode receber uma entrada e produzir uma saída;
- **LCEL**: sintaxe declarativa para compor Runnables;
- **parser**: conversão da resposta do modelo para um formato útil;
- **chunking**: divisão de textos longos em partes menores;
- **stuff** e **map-reduce**: estratégias diferentes de sumarização.

## Explicação detalhada

### O que é uma chain?

Uma chain é uma sequência de operações em que a saída de uma etapa alimenta a entrada da próxima. Em vez de escrever manualmente:

```python
prompt_text = template.format(name="Mithras")
model_response = model.invoke(prompt_text)
```

podemos declarar o fluxo com LCEL:

```python
chain = template | model
result = chain.invoke({"name": "Mithras"})
```

O operador `|` não é uma chamada ao modelo por si só. Ele monta um novo Runnable composto. A chamada acontece quando `invoke()` é executado.

### O que é `@chain`?

`@chain` é um decorator do LangChain. Um decorator recebe uma função Python e devolve uma versão enriquecida dela. Neste exemplo:

```python
@chain
def square(input_dict: dict) -> dict:
    x = input_dict["x"]
    return {"square_result": x * x}
```

A função original calcula o quadrado. O decorator faz com que essa função também se comporte como um Runnable, com métodos como `invoke()` e possibilidade de ser conectada a outras etapas com `|`.

Sem o decorator, `square` seria apenas uma função comum e o uso seria `square({"x": 10})`. Com o decorator, podemos usar:

```python
square.invoke({"x": 10})
```

O resultado é `{"square_result": 100}`. Depois, esse dicionário entra no próximo prompt:

```python
chain2 = square | question_template2 | model
```

O valor `square_result` é encontrado pelo campo `{square_result}` do template. Portanto, o exemplo combina uma transformação determinística de Python com uma geração feita pelo modelo.

### O que é `RunnableLambda`?

`RunnableLambda` é outra forma de transformar uma função comum em Runnable. No arquivo `3-runnable-lambda.py`, a função:

```python
def parse_number(text: str) -> int:
    return int(text.strip())
```

recebe o texto `"10"`, remove espaços e devolve o inteiro `10`. Depois:

```python
parse_runnable = RunnableLambda(parse_number)
number = parse_runnable.invoke("10")
```

A diferença didática é que `@chain` decora a função diretamente, enquanto `RunnableLambda` recebe a função como argumento. Os dois mecanismos permitem incluir lógica Python em um pipeline LCEL.

### O que acontece no pipeline de tradução e resumo?

No arquivo `4-pipeline-de-processamento.py`, a entrada é:

```python
{"initial_text": "LangChain é um framework para desenvolvimento de aplicações com IA"}
```

O fluxo executa estas etapas:

1. `template_translate` procura o campo `initial_text`;
2. o Gemini traduz o texto para inglês;
3. `StrOutputParser` extrai somente o texto da resposta;
4. o resultado é colocado no campo `text` por `{"text": translate}`;
5. `template_summary` pede um resumo de quatro palavras;
6. o segundo resultado é novamente convertido em string.

Essa construção mostra que uma etapa pode preparar a entrada nomeada que a próxima etapa espera.

### O que é um `Document`?

Os splitters não retornam apenas strings. `create_documents()` cria objetos `Document`, que normalmente possuem:

- `page_content`: texto do trecho;
- `metadata`: informações como origem, página ou índice.

Essa estrutura é útil porque o texto pode ser enviado ao modelo enquanto os metadados continuam disponíveis para rastreamento.

### Como funciona o `RecursiveCharacterTextSplitter`?

No exemplo, `chunk_size=250` pede trechos pequenos e `chunk_overlap=70` repete parte do final de um trecho no começo do seguinte. O splitter tenta quebrar em separadores naturais antes de cortar caracteres diretamente.

O overlap ajuda quando uma ideia começa no fim de um chunk e termina no começo do próximo. Em compensação, ele aumenta a quantidade total de texto e pode aumentar o número de chamadas.

### `stuff` versus `map-reduce`

Em `5-sumarizacao.py`, `chain_type="stuff"` coloca todos os documentos em uma única solicitação. O fluxo é simples:

```text
vários Documents → um prompt grande → um resumo
```

Em `6-sumarizacao-com-map-reduce.py`, cada chunk é resumido primeiro e os resultados são combinados depois:

```text
chunk 1 ─┐
chunk 2 ─┼→ resumos individuais → resumo final
chunk 3 ─┘
```

Map-reduce suporta mais texto, mas consome pelo menos uma chamada por chunk e outra chamada na redução. Por isso, uma execução pode esgotar rapidamente a cota gratuita do provedor.

### Como funciona o pipeline manual do arquivo 7?

O arquivo `7-pipeline-sumarizacao.py` implementa as mesmas ideias sem usar `load_summarize_chain`:

1. `prepare_map_inputs` transforma cada `Document` em `{"context": texto}`;
2. `map_chain` resume um contexto;
3. `.map()` aplica essa chain a todos os itens da lista;
4. `prepare_reduce_input` junta os resumos com quebras de linha;
5. `reduce_chain` produz o resumo final.

Esse exemplo é importante porque mostra o que uma chain pronta faz internamente e dá mais controle sobre prompts, parsers e concorrência.
