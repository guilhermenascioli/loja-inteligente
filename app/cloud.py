"""Aplicação pública WSGI; uploads processados somente em memória."""
import json
import os
import threading
from datetime import date
from pathlib import Path
from flask import Flask, request, jsonify, make_response, send_from_directory
from werkzeug.exceptions import RequestEntityTooLarge
from app import ai
from app.processing import MAX_BYTES, FileError, analyze, example, export, inspect_file

app = Flask(__name__, static_folder=None)
app.config['MAX_CONTENT_LENGTH'] = MAX_BYTES
STATIC = Path(__file__).parent / 'static'
MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
_lock = threading.Lock()
_usage = {'day': None, 'count': 0}

@app.before_request
def origin_check():
    if request.method == 'POST':
        origin = request.headers.get('Origin')
        if origin and origin != request.host_url.rstrip('/'):
            return jsonify(erro='Origem não autorizada.'), 403

@app.after_request
def security(response):
    response.headers['Cache-Control'] = 'no-store'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'no-referrer'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'self' https://guilhermenascioli.github.io; base-uri 'none'"
    return response

@app.errorhandler(RequestEntityTooLarge)
def too_large(error):
    return jsonify(erro='Selecione um arquivo com até 5 MB.'), 413

@app.get('/')
def index():
    return send_from_directory(STATIC, 'index.html')

@app.get('/<name>')
def static_file(name):
    if name not in ('style.css', 'app.js'):
        return jsonify(erro='Página não encontrada.'), 404
    return send_from_directory(STATIC, name)

@app.get('/api/status')
def status():
    return jsonify(ia_configurada=ai.configured(), provedor=ai.provider())

@app.get('/health')
def health():
    return jsonify(status='ok')

def download(data, name):
    response = make_response(data)
    response.headers['Content-Type'] = MIME
    response.headers['Content-Disposition'] = f'attachment; filename="{name}"'
    return response

@app.get('/api/example')
def sample():
    try:
        kind = request.args.get('tipo', 'vendas')
        return download(example(kind), f'exemplo_{kind}.xlsx')
    except FileError as error:
        return jsonify(erro=str(error)), 400

@app.post('/api/<action>')
def process(action):
    if action not in ('inspect', 'analyze', 'export', 'explain'):
        return jsonify(erro='Página não encontrada.'), 404
    try:
        if action == 'explain' and request.headers.get('X-Loja-Consent') != 'sim':
            return jsonify(erro='Autorize o envio dos indicadores antes de consultar a IA.'), 400
        content = request.get_data()
        name = request.args.get('nome', '')
        kind = request.args.get('tipo', '')
        sheet = request.args.get('aba') or None
        if action == 'inspect':
            return jsonify(inspect_file(content, name, kind, sheet))
        mapping = json.loads(request.args['mapa']) if 'mapa' in request.args else None
        result = analyze(content, name, kind, mapping, sheet)
        if action == 'export':
            return download(export(result), f'relatorio_{kind}.xlsx')
        if action == 'explain':
            if not ai.configured():
                raise ai.AIError('A IA ainda não está configurada. Os indicadores continuam disponíveis.')
            with _lock:
                today = date.today().isoformat()
                if _usage['day'] != today:
                    _usage.update(day=today, count=0)
                limit = max(0, int(os.environ.get('LOJA_AI_DAILY_LIMIT', '30')))
                if _usage['count'] >= limit:
                    return jsonify(erro='O limite de explicações desta demonstração foi atingido. Os indicadores e relatórios continuam disponíveis.'), 429
                _usage['count'] += 1
            return jsonify(texto=ai.explain(result), origem=ai.provider())
        public = {key: value for key, value in result.items() if key not in ('originais', 'tratados')}
        public['previa_ia'] = ai.payload(result)
        return jsonify(public)
    except (FileError, ai.AIError) as error:
        return jsonify(erro=str(error)), 400
    except ValueError:
        return jsonify(erro='Não foi possível interpretar as opções da planilha. Confira as colunas.'), 400
    except Exception:
        return jsonify(erro='Não foi possível concluir a análise. Revise o arquivo e tente novamente.'), 500
