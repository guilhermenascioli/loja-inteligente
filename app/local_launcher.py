"""Inicialização local com credencial ignorada pelo Git."""
import json
import os
from pathlib import Path
from app.server import main

def run():
    config = Path(__file__).resolve().parent.parent / '.runtime' / 'ia.local.json'
    if config.exists():
        settings = json.loads(config.read_text(encoding='utf-8-sig'))
        os.environ.setdefault('LOJA_GEMINI_API_KEY', settings['api_key'])
        os.environ.setdefault('LOJA_GEMINI_MODEL', settings['model'])
        if settings.get('free_tier_confirmed') is True:
            os.environ.setdefault('LOJA_GEMINI_FREE_TIER_CONFIRMED', 'sim')
    main()

if __name__ == '__main__':
    run()
