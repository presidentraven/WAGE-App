import sys,pathlib,unittest,datetime as dt,json,csv
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from update_data import check_rows
class WageArchiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.feed=json.loads((ROOT/'data/current.json').read_text())
    def test_source_and_frequency(self):
        self.assertEqual(self.feed['series'],'EMM_EPMR_PTE_YORD_DPG')
        self.assertEqual(self.feed['frequency'],'weekly')
        self.assertIn(self.feed['mode'],['eia_api','seed_only'])
    def test_fuel_dates_and_amounts(self):
        check_rows(self.feed['fuel'],dt.date.today())
    def test_dashboard_coverage(self):
        site=(ROOT/'index.html').read_text()
        self.assertIn('Data operations',site)
        self.assertIn('checkFeed',site)
        self.assertIn('date',site)
        self.assertNotIn('/*FUEL_JSON*/',site)
    def test_report_labels_historical_proxy(self):
        self.assertIn('Chicago-area', (ROOT/'index.html').read_text())
        self.assertNotEqual(self.feed.get('geography'),'Joliet pump price')
if __name__=='__main__':unittest.main()

class SourceFetchMockTests(unittest.TestCase):
    def test_eia_response_parsing_offline(self):
        import io
        from unittest.mock import patch
        from update_data import fetch_eia
        rows=json.loads((ROOT/'data/current.json').read_text())['fuel']
        payload={'response':{'data':[{'period':r['date'],'series':'EMM_EPMR_PTE_YORD_DPG','value':str(r['value'])} for r in reversed(rows)]}}
        raw=json.dumps(payload).encode('utf-8')
        with patch('urllib.request.urlopen',return_value=io.BytesIO(raw)):
            actual=fetch_eia('FAKE_KEY',dt.date(2026,10,9))
        self.assertEqual(actual[0]['date'],'2023-01-02')
        self.assertEqual(actual[-1]['date'],'2026-10-05')
        self.assertEqual(len(actual),197)
    def test_reject_future_dated_gas(self):
        from update_data import check_rows
        rows=json.loads((ROOT/'data/current.json').read_text())['fuel']
        with self.assertRaises(ValueError):
            check_rows(rows+[{'date':'2040-01-02','value':3}],dt.date(2026,10,9))
