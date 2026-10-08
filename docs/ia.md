# IA sem cobrança obrigatória

## Estado inicial

Nenhuma credencial ou modelo é configurado por padrão. O sistema funciona sem IA e informa isso claramente. Os testes usam respostas simuladas; não fazem chamadas reais. Não foram lidas ou reutilizadas credenciais do projeto financeiro.

## Gemini gratuito

1. Abra o [Google AI Studio](https://aistudio.google.com/api-keys) e crie uma chave em um **projeto próprio** para Loja Inteligente.
2. Confirme que o projeto está no **Free Tier** e **não vincule faturamento nem forma de pagamento**. Verifique os modelos com cota gratuita disponíveis na sua conta. Não use uma chave de projeto pago.
3. No mesmo PowerShell que iniciará a aplicação, configure:

```powershell
$env:LOJA_GEMINI_API_KEY = 'sua-chave-propria'
$env:LOJA_GEMINI_MODEL = 'nome-do-modelo-com-cota-gratuita'
$env:LOJA_GEMINI_FREE_TIER_CONFIRMED = 'sim'
python -m app.server
```

O nome do modelo é explícito para não depender de um modelo antigo ou indisponível. Use o identificador `gemini-...` exibido no AI Studio. A confirmação não verifica o faturamento remotamente: a gratuidade depende do projeto realmente permanecer no Free Tier. Não existe mecanismo da aplicação que ative faturamento ou compra de créditos. Consulta única, sem repetição automática, sem ferramentas pagas e sem troca de provedor quando a cota termina.

A chave fica somente no processo Python e é enviada ao Google no cabeçalho de autenticação. Nunca aparece no HTML, JavaScript, respostas de erro, relatório ou logs da aplicação. Não coloque uma chave real em `.env.example`, README ou repositório. Variáveis padrão como `GEMINI_API_KEY` não são lidas.

Antes da consulta, a interface revela a prévia exata dos indicadores. No nível gratuito, o Google pode utilizar dados para aprimorar produtos; evite indicadores confidenciais. [Faturamento](https://ai.google.dev/gemini-api/docs/billing), [termos](https://ai.google.dev/gemini-api/terms) e [API generateContent](https://ai.google.dev/api/generate-content).

## Ollama local

Alternativa sem chave, cota de API ou envio externo. Instale o [Ollama para Windows](https://ollama.com/download/windows) se desejar usar IA local. Baixe um modelo de texto compatível com a memória do computador, confira a licença e o nome em `ollama list` e deixe o Ollama aberto.

```powershell
$env:LOJA_OLLAMA_MODEL = 'nome-do-modelo-instalado'
python -m app.server
```

O servidor chama exclusivamente `http://127.0.0.1:11434`. Modelos com `cloud` no nome ou metadados de execução remota são recusados. Não baixa modelos automaticamente. Proxies e redirecionamentos são desativados nas chamadas de IA. Se Gemini e Ollama estiverem configurados, Gemini tem prioridade; remova a variável `LOJA_GEMINI_FREE_TIER_CONFIRMED` para usar somente Ollama.

Para operação estritamente local, também desabilite recursos cloud do Ollama conforme sua [documentação oficial](https://docs.ollama.com/faq). Recursos locais dependem de memória, espaço e energia do computador.

## O que a IA recebe

Tipo da análise, total, quantidade de unidades (vendas), contagens de registros, datas inicial/final, totais por mês e percentuais das maiores participações. Nenhuma linha original, chave, nome de arquivo, produto, categoria ou descrição. A mesma prévia é exibida na interface antes do consentimento.

Os números são calculados em Python antes da consulta. O modelo recebe instruções para explicar tendências, tratar causas como hipóteses e evitar números novos, previsões e lucro. A aplicação rejeita respostas vazias, incompletas ou com algarismos, mas não garante a correção de toda frase gerada. Os indicadores permanecem a referência verificável.

Sem configuração, sem consentimento, sem registros válidos ou com falha: mensagem clara, sem simular autoria por IA.
