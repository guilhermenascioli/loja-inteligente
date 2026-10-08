# GitHub, demonstração e entrevistas

## Texto para apresentar o projeto

**Loja Inteligente — dados, IA e automação para pequenas lojas.** Aplicação Python que transforma planilhas de vendas e despesas em indicadores, evolução mensal e rankings, com validação transparente por registro. Exporta dados tratados e problemas para conferência e integra explicações opcionais por Gemini no nível gratuito ou IA local. Interface responsiva, cálculos determinísticos e testes automatizados.

Competências demonstradas: qualidade de dados, leitura e tratamento de arquivos, agregações, precisão monetária, visualização, integração de IA com dados calculados, privacidade e comunicação de indicadores.

## Roteiro de entrevista

1. Apresente a dificuldade da pequena loja: dados disponíveis em planilhas, mas pouca clareza para decidir.
2. Use o exemplo de vendas: explique faturamento, quantidade, evolução e participação por produto.
3. Envie uma cópia com data inválida e registro duplicado. Mostre a diferença entre erro e possível repetição, sem perder a rastreabilidade.
4. Baixe o relatório e mostre Originais, Tratados e Problemas.
5. Explique por que cálculos pertencem ao código e a IA interpreta os indicadores. Mostre consentimento e prévia de compartilhamento.
6. Mostre testes, limites e escolhas: arquitetura pequena, custo zero local, nenhuma necessidade de ML ou Databricks para o problema.
7. Próximas etapas: comparação de vendas e despesas como saldo informado, histórico consentido, integração de fontes e publicação gratuita apropriada. Nunca chamar saldo de lucro contábil sem dados contábeis suficientes.

## Subir ao GitHub

Use **um repositório independente** para esta pasta, sem adicionar a pasta pessoal inteira ou o projeto financeiro. A configuração Git do computador indicou um repositório na pasta pessoal; os comandos devem ser executados apenas depois de confirmar que a raiz do repositório é esta pasta.

```powershell
git init -b main
git rev-parse --show-toplevel
# Confira que a resposta termina em Projeto_Loja_Inteligente_2.
git add README.md requirements.txt .gitignore .env.example iniciar.ps1 app tests docs dados/exemplos .github
git diff --cached --stat
git diff --cached
git commit -m "Implementa Loja Inteligente com análise local de planilhas"
```

Crie no GitHub um repositório vazio e conecte o endereço real fornecido pelo GitHub:

```powershell
git remote add origin ENDERECO_DO_SEU_REPOSITORIO
git push -u origin main
```

Nunca adicione chaves, planilhas reais, `.env`, `.venv`, `.runtime` ou relatórios de usuários. `.gitignore` protege esses locais comuns. A publicação não é feita automaticamente pelo projeto.

O workflow em `.github/workflows/tests.yml` roda os testes a cada push ou pull request. Não usa segredo nem API real. Confira as regras de gratuidade do GitHub para o tipo de repositório escolhido antes de habilitar automações; para repositório público, o workflow foi planejado para uso padrão de runner Linux.

## Inserir no portfólio depois

Depois de escolher a hospedagem e validar a demonstração, inclua o cartão Loja Inteligente abaixo do cartão do projeto financeiro, com imagem, descrição, tecnologias e links de demonstração/código. Nenhum arquivo do financeiro ou do portfólio foi modificado nesta etapa.

GitHub Pages serve arquivos estáticos e não executa este servidor Python. Publicar apenas o HTML desta versão não oferece upload/análise. A escolha de hospedagem e a publicação da aplicação completa ficam para uma etapa própria, respeitando custo zero. Não há promessa de hospedagem permanente gratuita com IA externa ilimitada.
