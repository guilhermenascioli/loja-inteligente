import unittest
from app.processing import analyze, inspect_file, FileError, workbook_bytes

class MappingTests(unittest.TestCase):
    data = 'Dia;Item;Grupo;Qtd;Preço;Observação\n01/09/2026;Caneca;Casa;2;25,00;teste\n'.encode('utf-8')
    mapping = {'data':'dia','produto':'item','categoria':'grupo','quantidade':'qtd','preco_unitario':'preco'}
    def test_aliases_and_extras(self):
        meta=inspect_file(self.data,'loja.csv','vendas')
        self.assertEqual(meta['sugestoes'],self.mapping)
        result=analyze(self.data,'loja.csv','vendas',self.mapping)
        self.assertEqual(result['total'],50)
        self.assertEqual(result['originais'][0]['observacao'],'teste')
    def test_duplicate_mapping_rejected(self):
        with self.assertRaises(FileError):
            analyze(self.data,'loja.csv','vendas',{**self.mapping,'produto':'dia'})
    def test_sheet_selection(self):
        headers=['data','descricao','categoria','valor']
        content=workbook_bytes({'Primeira':[dict(zip(headers,['01/09/2026','Luz','Serviços',100]))],'Segunda':[dict(zip(headers,['02/09/2026','Água','Serviços',40]))]})
        self.assertEqual(inspect_file(content,'loja.xlsx','despesas')['abas'],['Primeira','Segunda'])
        self.assertEqual(analyze(content,'loja.xlsx','despesas',sheet_name='Segunda')['total'],40)
        with self.assertRaises(FileError):
            analyze(content,'loja.xlsx','despesas',sheet_name='Inexistente')
