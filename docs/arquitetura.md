# Como o sistema funciona

O navegador envia o arquivo escolhido ao servidor Python local. O servidor lê XLSX com openpyxl ou CSV com a biblioteca padrão, valida registros, calcula indicadores e devolve resultados. Os gráficos SVG e suas tabelas usam os mesmos valores devolvidos. Nenhuma biblioteca de gráficos, fonte externa, telemetria ou serviço de hospedagem é necessário para executar.

## Fluxo

```text
Arquivo no navegador → leitura em memória → validação por linha
                                               ↓
                                  registros válidos + problemas
                                               ↓
                                    cálculos com Decimal
                                               ↓
                          indicadores / gráficos / relatório XLSX
                                               ↓ opcional, consentido
                           agregados → Gemini gratuito ou Ollama
```

## Contrato das rotas

| Rota | Função |
| --- | --- |
| GET / | Interface |
| GET /api/status | Disponibilidade configurada da IA e provedor; sem credenciais |
| GET /api/example?tipo=vendas | Exemplo XLSX fictício; também aceita despesas |
| POST /api/analyze?tipo=...&nome=... | Corpo binário do arquivo; indicadores e apontamentos |
| POST /api/export?tipo=...&nome=... | Reprocessa o mesmo arquivo e devolve relatório XLSX |
| POST /api/explain?tipo=...&nome=... | Reprocessa antes de consultar IA; exige X-Loja-Consent: sim |

Reprocessar na exportação e na IA evita manter arquivos ou análises em uma sessão do servidor. Os agregados enviados à IA são calculados novamente pelo Python, em vez de confiar em indicadores modificáveis pelo navegador. O arquivo permanece na memória da aba até remoção, troca de modo ou fechamento. Não há armazenamento no navegador, cookies, banco, cache de uploads ou arquivos temporários de planilhas.

## Regras verificáveis

- Cálculos usam Decimal. Faturamento de uma linha = quantidade inteira × preço com até duas casas. Grupos somam valores por operação, sem calcular novamente a partir de médias.
- Quantidade positiva inteira; dinheiro não negativo, até duas casas. Entrada monetária `1.234` é rejeitada, pois pode significar milhar ou três casas decimais. Use `1.234,00` ou `1234.00`.
- Normalização de cabeçalhos remove acentos, espaços externos e converte espaços em sublinhado. Não renomeia campos desconhecidos para adivinhar seu significado.
- Datas brasileiras e ISO explícitas; não adivinha data americana ou número serial fora de célula Excel de data.
- Chave de possível duplicação usa campos obrigatórios normalizados e valores convertidos. Repetições são mantidas porque podem representar operações legítimas.
- Linha inválida nunca vira zero. É excluída dos cálculos e preservada em Originais, com status e apontamentos. Sem linhas válidas, a interface mostra indicadores indisponíveis.
- Colunas extra ficam em Originais. Valores excedentes sem cabeçalho são preservados e tornam a linha inválida.
- Faturamento não é lucro. As duas análises são separadas nesta primeira versão.

## Privacidade e limites

Servidor limitado a 127.0.0.1, valida Host e Origin, não disponibiliza arquivos por caminho arbitrário. Apenas HTML, CSS e JS públicos são servidos. Sem logs de nomes, conteúdo, query strings ou credenciais. Cabeçalhos impedem cache e restringem scripts e conexões à origem local. Exportação neutraliza textos que poderiam virar fórmulas ao abrir no Excel.

Limites de tamanho, registros, colunas e ZIP descompactado reduzem uso de recursos. XLSX protegido, inválido ou fora dos limites gera erro claro. Fórmulas são lidas como texto e sinalizadas; não existe mecanismo de cálculo ou execução de macros. Linhas em branco no corpo aparecem como problemas. Planilhas com abas adicionais avisam que somente a primeira foi usada.

Valores decimais viram números JSON apenas após o cálculo; JSON e Excel têm precisão numérica finita. Esta versão não é um sistema contábil nem adequada a valores de grandeza extrema. Para produção: impor teto total por análise, limitar concorrência e chamadas de IA, usar servidor de produção, HTTPS, proteção contra abuso e política de privacidade adequada. O servidor atual é para demonstração local.

## Escolhas de implementação

Python padrão + openpyxl reduzem instalação, dependências e custo. Interface em HTML/CSS/JS permite controle visual e acesso por navegador. Testes unittest não exigem bibliotecas adicionais. Não foi necessário banco, pandas, Databricks ou treinamento de modelos.
