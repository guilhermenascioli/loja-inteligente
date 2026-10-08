"""IA opcional: Gemini gratuito explicitamente habilitado ou Ollama local."""
import json
import os
import re
import ssl
import urllib.error
import urllib.request


class AIError(ValueError):
    pass


def provider():
    if (os.environ.get('LOJA_GEMINI_API_KEY') and os.environ.get('LOJA_GEMINI_MODEL')
            and os.environ.get('LOJA_GEMINI_FREE_TIER_CONFIRMED') == 'sim'):
        return 'Gemini'
    model = os.environ.get('LOJA_OLLAMA_MODEL', '').strip()
    if model and 'cloud' not in model.lower():
        return 'Ollama local'
    return None


def configured():
    return provider() is not None


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise AIError('A consulta de IA foi redirecionada e interrompida. Confira a configuração.')


def api_request(url, body, headers=None):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={'Content-Type': 'application/json', **(headers or {})})
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.load_default_certs()
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect(), urllib.request.HTTPSHandler(context=context))
    with opener.open(req, timeout=55) as response:
        return json.load(response)


def payload(result):
    return {k: result[k] for k in ('tipo', 'total', 'quantidade', 'recebidos', 'validos', 'invalidos', 'duplicados', 'inicio', 'fim', 'mensal')} | {
        'participacoes_principais_percentual': [r['participacao'] for r in result['ranking'][:5]],
    }


def explain(result):
    if not configured():
        raise AIError('A IA ainda não está configurada. Os indicadores e a exportação continuam disponíveis.')
    if not result['validos']:
        raise AIError('Corrija a planilha antes de solicitar uma explicação por IA.')
    instructions = 'Você explica indicadores de pequenas lojas em português brasileiro. Use apenas os dados fornecidos, sem supor causas, lucro, previsões ou dados ausentes. Responda em até três parágrafos curtos, SEM algarismos e SEM escrever valores numéricos por extenso: os números são exibidos separadamente pelo sistema. Descreva tendências observáveis e sugestões de investigação como hipóteses. Informe limitações se há linhas inválidas ou duplicadas. Não afirme que observou nomes de produtos ou categorias. O total de vendas é faturamento; não é lucro.'
    prompt = json.dumps(payload(result), ensure_ascii=False)
    try:
        if provider() == 'Gemini':
            model = os.environ['LOJA_GEMINI_MODEL'].strip()
            if not re.fullmatch(r'gemini-[a-zA-Z0-9._-]+', model):
                raise AIError('Nome de modelo Gemini inválido.')
            data = api_request(f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent', {
                'systemInstruction': {'parts': [{'text': instructions}]},
                'contents': [{'parts': [{'text': prompt}]}],
                'generationConfig': {'temperature': 0, 'maxOutputTokens': 1500},
            }, {'x-goog-api-key': os.environ['LOJA_GEMINI_API_KEY']})
            candidates = data.get('candidates', [])
            candidate = candidates[0] if candidates else {}
            text = '\n'.join(part.get('text', '') for part in candidate.get('content', {}).get('parts', []) if not part.get('thought')).strip()
            complete = candidate.get('finishReason') == 'STOP'
        else:
            model = os.environ['LOJA_OLLAMA_MODEL'].strip()
            metadata = api_request('http://127.0.0.1:11434/api/show', {'model': model})
            if metadata.get('remote_model') or metadata.get('remote_host'):
                raise AIError('Use um modelo instalado localmente. Modelos Ollama na nuvem não são permitidos.')
            data = api_request('http://127.0.0.1:11434/api/generate', {
                'model': model, 'system': instructions, 'prompt': prompt,
                'stream': False, 'keep_alive': 0, 'options': {'temperature': 0, 'num_predict': 500},
            })
            text = data.get('response', '').strip()
            complete = data.get('done') and data.get('done_reason') != 'length'
        if not text or not complete or re.search(r'\d', text):
            raise AIError('A resposta da IA não pôde ser validada. Tente novamente; os indicadores continuam disponíveis.')
        return text
    except AIError:
        raise
    except (urllib.error.URLError, TimeoutError, OSError, ValueError):
        raise AIError('A IA está indisponível: confira a configuração, a conexão ou o limite gratuito do Gemini. Para IA local, mantenha o Ollama aberto com o modelo instalado. Nenhum resultado calculado foi alterado.') from None
