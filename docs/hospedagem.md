# Publicação no Render

O render.yaml configura um Web Service no plano Free. Conecte apenas o repositório loja-inteligente, sem acesso aos demais projetos. Use o fluxo Blueprint para importar a configuração.

A chave LOJA_GEMINI_API_KEY deve ser inserida somente nas variáveis secretas da hospedagem. Nunca no GitHub, HTML ou chat. Modelo e limite ficam na configuração pública.

Copie a URL HTTPS real atribuída ao serviço depois que /health responder. Essa URL será usada no iframe do portfólio. O aplicativo permite incorporação somente pelo próprio domínio e por https://guilhermenascioli.github.io.

O limite de IA desta demonstração é global: 30 tentativas por dia UTC, por processo. Reinícios zeram o contador; ele reduz uso casual e não é uma proteção contra abuso nem substitui a cota do provedor. Use um projeto Gemini sem faturamento para manter o limite gratuito. As análises comuns continuam disponíveis após esgotar a IA.

O Render Free suspende o serviço após 15 minutos sem tráfego; o próximo acesso pode aguardar cerca de um minuto. Não há processamento persistente de planilhas nem banco de dados. A IA envia somente os indicadores apresentados mediante consentimento.

Fonte: https://render.com/docs/free
