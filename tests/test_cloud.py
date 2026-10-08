import unittest
from unittest.mock import patch
from app.cloud import app
from app.processing import example

class CloudTests(unittest.TestCase):
    def setUp(self):
        self.client=app.test_client()
    def test_health_and_embedding(self):
        self.assertEqual(self.client.get('/health').status_code,200)
        r=self.client.get('/')
        self.assertEqual(r.status_code,200)
        self.assertIn('https://guilhermenascioli.github.io',r.headers['Content-Security-Policy'])
    def test_analysis_and_download(self):
        data=example('vendas')
        url='/api/analyze?tipo=vendas&nome=exemplo.xlsx'
        r=self.client.post(url,data=data,content_type='application/octet-stream')
        self.assertEqual(r.status_code,200)
        self.assertEqual(r.json['total'],9489)
        self.assertNotIn('originais',r.json)
        r=self.client.post('/api/export?tipo=vendas&nome=exemplo.xlsx',data=data)
        self.assertEqual(r.status_code,200)
        self.assertTrue(r.data.startswith(b'PK'))
    def test_consent_and_origin(self):
        with patch('app.cloud.ai.explain') as explain:
            self.assertEqual(self.client.post('/api/explain',data=b'x').status_code,400)
            explain.assert_not_called()
        self.assertEqual(self.client.post('/api/analyze',data=b'x',headers={'Origin':'https://other.example'}).status_code,403)
    def test_cloud_inspection(self):
        r=self.client.post('/api/inspect?tipo=despesas&nome=a.xlsx',data=example('despesas'))
        self.assertEqual(r.status_code,200)
        self.assertIn('valor',r.json['campos'])
