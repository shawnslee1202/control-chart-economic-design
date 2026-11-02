"""Focused checks for statistical definitions and data integrity."""
import unittest,tempfile,json
from pathlib import Path
import numpy as np
from scipy.stats import norm
from control_chart_economic_design.data.parse_run import read_table,timestamp,operating_gaps
import pandas as pd

class Tests(unittest.TestCase):
    def test_arl_known_reference(self):
        self.assertAlmostEqual(1/(2*norm.sf(3)),370.398347,places=5)
    def test_timestamp_does_not_trust_wrong_weekday(self):
        self.assertEqual(timestamp('Thu Oct 26 08:00:46 CST 2026').isoformat(),'2026-10-26T08:00:46')
        self.assertEqual(timestamp('10-26-2026 08:00:46'),timestamp('Mon Oct 26 08:00:46 CDT 2026'))
    def test_reject_truncated_capture(self):
        with tempfile.TemporaryDirectory() as p:
            Path(p,'quality.json').write_text(json.dumps([['a','b','c'],['x','y']]))
            with self.assertRaises(ValueError):read_table(p,'quality')
    def test_lunch_and_night_excluded(self):
        t=pd.Series(pd.to_datetime(['2026-10-26 11:40','2026-10-26 11:50','2026-10-26 13:00','2026-10-26 13:10','2026-10-27 08:00','2026-10-27 08:10']))
        self.assertTrue(np.all(operating_gaps(t)==600))
    def test_shift_symmetry_and_detection_floor(self):
        for n in [2,5,10]:
            for d in [.5,1.,2.]:
                p=norm.sf(3-d*np.sqrt(n))+norm.cdf(-3-d*np.sqrt(n))
                q=norm.sf(3+d*np.sqrt(n))+norm.cdf(-3+d*np.sqrt(n))
                self.assertAlmostEqual(p,q);self.assertGreaterEqual(1/p,1)

if __name__=='__main__':unittest.main()
