'''
Created on Jan 8, 2016

@author: santhosh
'''
import os, sys

import CommonUtil


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print 'Usage: python -m \"evidence.testAnonEcomm\" csvFolder'
        sys.exit()
    csvFolder = sys.argv[1]

    plotDir = os.path.join(os.path.join(os.path.join(csvFolder, os.pardir), 'stats'), 'fk')

    normal_bnss_key_time_wdw_list = [('284235722', (140, 142)), ('284819997', (150, 152)), ('319927587', (120, 122))]
    anomalous_bnss_key_time_wdw_list = [('284819997', (166, 171)), ('284819997', (173, 178)),
                              ('284819997', (180, 185)), ('284819997', (187, 192)),
                              ('319927587', (189, 194)), ('404593641', (158, 163)),
                              ('412629178', (148, 153)), ('284235722', (147,152))]
    CommonUtil.doGatherEvidence(csvFolder, plotDir, bnss_key_time_wdw_list=anomalous_bnss_key_time_wdw_list)
