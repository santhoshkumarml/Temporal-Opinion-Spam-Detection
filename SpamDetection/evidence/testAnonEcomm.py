'''
Created on Jan 8, 2016

@author: santhosh
'''
import os, sys

import CommonUtil
from util.data_reader_utils.anon_ecomm_utils.AnonEcommDataReader import AnonEcommDataReader


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print 'Usage: python -m \"evidence.testAnonEcomm\" csvFolder'
        sys.exit()
    csvFolder = sys.argv[1]

    plotDir = os.path.join(os.path.join(os.path.join(csvFolder, os.pardir), 'stats'), 'fk')

    anomalous_bnss_key_time_wdw_list = [('8df49a65474732e4f63d378df4bd67e4', (93, 98)),
                           ('5f2c7517a7012640763148a38b1372b6', (71, 76)),
                            ('fb57b2749835facf54d9c73f0d9a8d4c', (32, 37)),
                             ('8edd789d64c7279592057487ff5bb264', (31, 36)),
                              ('a9856cb97ebd363a0581d08f27f8b379', (30, 35))]
#     anomalous_bnss_key_time_wdw_list = [
#                         ('8df49a65474732e4f63d378df4bd67e4', (93, 96)), ('8df49a65474732e4f63d378df4bd67e4', (94, 97)), ('8df49a65474732e4f63d378df4bd67e4', (95, 98)),
#                         ('5f2c7517a7012640763148a38b1372b6', (71, 74)), ('5f2c7517a7012640763148a38b1372b6', (72, 75)), ('5f2c7517a7012640763148a38b1372b6', (73, 76)),
#                         ('fb57b2749835facf54d9c73f0d9a8d4c', (32, 35)), ('fb57b2749835facf54d9c73f0d9a8d4c', (33, 36)), ('fb57b2749835facf54d9c73f0d9a8d4c', (34, 37)),
#                         ('8edd789d64c7279592057487ff5bb264', (31, 34)), ('8edd789d64c7279592057487ff5bb264', (32, 35)), ('8edd789d64c7279592057487ff5bb264', (33, 36)),
#                         ('a9856cb97ebd363a0581d08f27f8b379', (30, 33)), ('a9856cb97ebd363a0581d08f27f8b379', (31, 34)), ('a9856cb97ebd363a0581d08f27f8b379', (32, 35))]
    CommonUtil.doGatherEvidence(csvFolder, plotDir, bnss_key_time_wdw_list=anomalous_bnss_key_time_wdw_list, rdr=AnonEcommDataReader())
