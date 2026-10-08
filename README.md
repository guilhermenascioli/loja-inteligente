# Loja Inteligente

Assistente de dados para pequenas lojas: transforma planilhas de vendas e despesas em indicadores, gráficos e relatórios de conferência. Projeto independente para portfólio de dados, IA e automação.

**Gratuito para executar localmente.** A análise não usa IA, API paga, Databricks ou machine learning. IA opcional com **Gemini em projeto Free Tier** ou **Ollama local**. Sem credenciais configuradas, nenhuma API externa é chamada.

## Executar no Windows

Requer Python 3.11 ou superior. No PowerShell, dentro desta pasta:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m app.server
```

Abra **http://localhost:8000**. Mantenha o terminal aberto. Encerre com `Ctrl+C`.

Se o Python já tiver `openpyxl` instalado, basta `python -m app.server`. `iniciar.ps1` também inicia o sistema, preferindo o ambiente `.venv` quando existir. Para outra porta: `python -m app.server --port 8001`.

## Experimentar

1. Escolha **Vendas** e clique **Experimentar com dados fictícios**.
2. Confira faturamento de **R$ 9.489,00**, **612 unidades**, 24 registros e seis meses.
3. Clique **Baixar relatório XLSX**: confira indicadores, evolução mensal, participação, maiores operações, registros tratados, problemas e originais.
4. Escolha **Despesas** e experimente: total **R$ 9.255,00**, 24 registros e quatro categorias.
5. Baixe um exemplo, altere uma data para `31/02/2026`, apague uma categoria e duplique um registro. Envie o arquivo e confira a análise parcial e os avisos.

Os exemplos também ficam em `dados/exemplos/`. Todos os dados são fictícios.

## O que está incluído

- Vendas e despesas em análises separadas.
- XLSX e CSV, seleção ou arrastar, demonstração em um clique e exemplos para baixar.
- Colunas obrigatórias, datas, valores, campos ausentes, fórmulas e duplicados validados com mensagens por linha.
- Indicadores e gráficos com tabelas acessíveis dos mesmos valores.
- Exportação XLSX com dados originais, dados tratados, cálculos e problemas.
- Interface escura responsiva com estados de carregamento, sucesso e erro.
- Explicação por IA opcional, identificada pelo provedor, mediante autorização.
- Nenhum arquivo enviado é salvo em disco; pedidos são processados em memória.

## Colunas e regras

| Análise | Colunas |
| --- | --- |
| Vendas | `data`, `produto`, `categoria`, `quantidade`, `preco_unitario` |
| Despesas | `data`, `descricao`, `categoria`, `valor` |

Cabeçalhos aceitam maiúsculas, espaços e acentos: `Preço unitário` corresponde a `preco_unitario`. Use cabeçalhos na primeira linha. No XLSX, somente a primeira aba é analisada; abas adicionais geram aviso.

Datas: `DD/MM/AAAA`, `AAAA-MM-DD` ou células de data no Excel. Valores: `1234,56`, `1.234,56`, `R$ 1.234,56` ou `1234.56`. Dinheiro deve ter no máximo duas casas decimais. Quantidade é inteira positiva. Dinheiro zero é aceito. Negativos, estornos e devoluções não são suportados nesta versão e geram problema explícito. Fórmulas devem ser substituídas pelo resultado antes do envio.

**Duplicados são mantidos nos indicadores**, com aviso de possível repetição. **Linhas inválidas ficam fora dos indicadores**, explicitamente sinalizadas, e permanecem no relatório original. Registros vazios no corpo são apontados; linhas finais fora da área usada do XLSX não são registros. Colunas adicionais são preservadas em Originais e geram aviso. Limites: 5 MB, 20.000 registros, 100 colunas e 50 MB descompactados para XLSX.

Faturamento = soma de quantidade × preço unitário, com cálculo decimal. Despesas = soma de valores válidos. Participação = valor do produto/categoria ÷ total. Meses intermediários sem registros aparecem com zero. Não há conciliação entre as duas planilhas nem cálculo de lucro contábil nesta versão.

## IA gratuita e opcional

Veja [Configuração da IA](docs/ia.md). Não envie chaves pelo chat nem coloque credenciais no código. Variáveis possuem prefixo `LOJA_`, para não reutilizar automaticamente credenciais de outros projetos. `.env.example` lista nomes, mas a aplicação não carrega `.env` automaticamente.

**Gemini:** crie um projeto próprio no Google AI Studio com nível gratuito e sem faturamento vinculado. Os limites variam por modelo e projeto. A aplicação exige confirmação explícita dessa configuração antes de habilitar Gemini; não consegue verificar o faturamento da conta. Se a cota acabar, ela informa indisponibilidade, sem migrar para outro provedor. [Documentação de faturamento do Gemini](https://ai.google.dev/gemini-api/docs/billing).

**Ollama:** executa um modelo instalado no computador, sem API externa nem cobrança por chamada. Requer espaço e memória para o modelo. Consulte a [documentação do Ollama](https://docs.ollama.com/api/generate).

O visitante vê os dados enviados e precisa autorizar: somente totais, contagens, período, valores mensais e percentuais. Sem planilha completa, nomes de produtos, categorias ou descrições. IA explica resultados calculados; não fornece os indicadores. Respostas incompletas, vazias ou com algarismos são rejeitadas para evitar apresentar novos números. Isso não elimina todos os riscos de interpretação: conclusões devem ser conferidas com as tabelas. Não existe texto comum rotulado como IA quando a consulta falha.

## Testes

```powershell
python -m unittest discover -s tests -v
```

Testes cobrem cálculos conhecidos, precisão decimal, agrupamento mensal e meses vazios, participação, despesas, valores brasileiros, arquivos inválidos, limite de tamanho e registros, campos ausentes, fórmulas, duplicados, exportação segura, consentimento, acesso local e integração simulada de IA. Nenhuma chave real nem chamada paga é necessária.

## Arquitetura e portfólio

- `app/processing.py`: leitura, validação, cálculos, exemplos e exportação.
- `app/server.py`: servidor local e rotas, sem banco de dados ou uploads persistentes.
- `app/ai.py`: integração opcional com Gemini e Ollama.
- `app/static/`: interface HTML, CSS e JavaScript; gráficos SVG, sem serviços ou bibliotecas externas.
- `tests/`: testes de processamento, IA simulada e rotas.
- `docs/`: arquitetura, IA, roteiro de demonstração e publicação no GitHub.

Consulte [Arquitetura](docs/arquitetura.md) e [Guia de portfólio e GitHub](docs/portfolio.md).

Esta primeira versão usa um servidor local de desenvolvimento, acessível apenas no computador. GitHub hospeda o código; **GitHub Pages não executa o processamento Python**. Para uma demonstração pública completa, uma hospedagem com Python e controles adicionais deverá ser escolhida em outra etapa. O projeto financeiro não é alterado por este sistema.
