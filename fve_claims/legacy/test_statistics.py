import unittest
import numpy as np
import pandas as pd
from claim_stats import bootstrap_weights, summarize, contrast


class StatisticsTests(unittest.TestCase):
    def test_shared_document_resampling(self):
        frame=pd.DataFrame(dict(pilot_id=[0,0,1,1],truth=['true','false','true','false'],fve_drop_released=[2.,1.,12.,11.]))
        ids,w=bootstrap_weights(frame.pilot_id)
        c=contrast(frame,ids,w)
        self.assertEqual(c['mean_difference'],1)
        self.assertEqual((c['lo'],c['hi']),(1.,1.))
        self.assertAlmostEqual(c['auc'],.75)
    def test_missing_cells_and_negative_drops(self):
        frame=pd.DataFrame(dict(pilot_id=[0,0,1],truth=['true']*3,fve_drop_released=[-2.,0.,5.]))
        ids,w=bootstrap_weights([0,1,2])
        s=summarize(frame,ids,w)
        self.assertEqual(s['n'],3)
        self.assertAlmostEqual(s['negative_fraction'],1/3)
        self.assertEqual(s['mean'],1)
        self.assertEqual(s['document_weighted_mean'],2)
        self.assertLess(s['valid_bootstrap_draws'],1000)
        self.assertIsNone(contrast(frame,ids,w)['mean_difference'])
        self.assertIsNone(summarize(frame.iloc[:0],ids,w)['mean'])


if __name__=='__main__': unittest.main()
