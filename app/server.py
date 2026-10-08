"""Local, stateless HTTP server. Run: python -m app.server."""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from app import ai
from app.processing import MAX_BYTES, FileError, analyze, example, export, inspect_file

STATIC = Path(__file__).parent / 'static'
MIME_XLSX = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Avoid recording uploaded names, content or credentials.
        pass

    def send(self, content, status=200, mime='application/json; charset=utf-8', filename=None):
        if isinstance(content, dict):
            content = json.dumps(content, ensure_ascii=False, allow_nan=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(content)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'")
        if filename:
            self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
        self.end_headers()
        self.wfile.write(content)

    def trusted_request(self):
        host = self.headers.get('Host', '')
        if host not in (f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'):
            return False
        origin = self.headers.get('Origin')
        return not origin or origin in (f'http://127.0.0.1:{self.server.server_port}', f'http://localhost:{self.server.server_port}')

    def do_GET(self):
        if not self.trusted_request():
            return self.send({'erro': 'Acesso permitido somente pelo endereço local.'}, 403)
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        if parsed.path == '/api/status':
            return self.send({'ia_configurada': ai.configured(), 'provedor': ai.provider()})
        if parsed.path == '/api/example':
            try:
                kind = query.get('tipo', ['vendas'])[0]
                return self.send(example(kind), mime=MIME_XLSX, filename=f'exemplo_{kind}.xlsx')
            except FileError as e:
                return self.send({'erro': str(e)}, 400)
        assets = {'/': ('index.html', 'text/html; charset=utf-8'), '/style.css': ('style.css', 'text/css; charset=utf-8'), '/app.js': ('app.js', 'text/javascript; charset=utf-8')}
        if parsed.path not in assets:
            return self.send({'erro': 'Página não encontrada.'}, 404)
        name, mime = assets[parsed.path]
        self.send((STATIC / name).read_bytes(), mime=mime)

    def do_POST(self):
        if not self.trusted_request():
            return self.send({'erro': 'Origem não autorizada.'}, 403)
        parsed = urlparse(self.path)
        if parsed.path not in ('/api/analyze', '/api/export', '/api/explain', '/api/inspect'):
            return self.send({'erro': 'Página não encontrada.'}, 404)
        query = parse_qs(parsed.query)
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if length < 1 or length > MAX_BYTES:
                raise FileError('Selecione um arquivo com até 5 MB.')
            self.connection.settimeout(40)
            content = self.rfile.read(length)
            if len(content) != length:
                raise FileError('O envio do arquivo foi interrompido. Tente novamente.')
            name, kind = query.get('nome', [''])[0], query.get('tipo', [''])[0]
            sheet = query.get('aba', [''])[0] or None
            if parsed.path == '/api/inspect':
                return self.send(inspect_file(content, name, kind, sheet))
            mapping = json.loads(query['mapa'][0]) if 'mapa' in query else None
            result = analyze(content, name, kind, mapping, sheet)
            if parsed.path == '/api/export':
                return self.send(export(result), mime=MIME_XLSX, filename=f'relatorio_{result["tipo"]}.xlsx')
            if parsed.path == '/api/explain':
                if self.headers.get('X-Loja-Consent') != 'sim':
                    return self.send({'erro': 'Autorize o envio dos indicadores antes de consultar a IA.'}, 400)
                return self.send({'texto': ai.explain(result), 'origem': ai.provider()})
            # The browser gets calculated tables; originals stay only in this request.
            public = {k: v for k, v in result.items() if k not in ('originais', 'tratados')}
            public['previa_ia'] = ai.payload(result)
            return self.send(public)
        except (FileError, ai.AIError) as e:
            return self.send({'erro': str(e)}, 400)
        except (TimeoutError, ValueError):
            return self.send({'erro': 'Não foi possível receber o arquivo. Tente enviá-lo novamente.'}, 400)
        except Exception:
            return self.send({'erro': 'Não foi possível concluir a análise. Revise o arquivo e tente novamente.'}, 500)


def main():
    parser = argparse.ArgumentParser(description='Loja Inteligente local')
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()
    server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    print(f'Loja Inteligente: http://localhost:{args.port} — Ctrl+C para encerrar', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()


if __name__ == '__main__':
    main()
