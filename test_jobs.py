import unittest,pathlib,math
ROOT=pathlib.Path(__file__).resolve().parents[1]
class JobRadiusTests(unittest.TestCase):
 def test_page_and_home_baseline(self):
  s=(ROOT/'index.html').read_text()
  for part in ['04 · 35-mile job search',"zip:'60432'",'radius:35','haversineMi','jobObs','j-compare','35 miles of 60432']:
   self.assertIn(part,s)
 def test_no_fake_jobs_are_seeded(self):
  lines=(ROOT/'data/job_observations.csv').read_text().splitlines()
  self.assertEqual(len(lines),1)
 def test_fuel_reference_persists(self):
  s=(ROOT/'index.html').read_text()
  self.assertIn('Chicago-area',s)
  self.assertIn('60432 fill-up assumption',s)
