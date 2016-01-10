'''
Created on Jan 6, 2016

@author: santhosh
'''

from main import AppUtil
from datetime import datetime
import sys, os
import CommonUtil

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print 'Usage: python -m \"evidence.testItunes\" csvFolder'
        sys.exit()
    csvFolder = sys.argv[1]

    plotDir = os.path.join(os.path.join(os.path.join(csvFolder, os.pardir), 'stats'), 'it')

    currentDateTime = datetime.now().strftime('%d-%b--%H:%M')
#     bnss_key_time_wdw_list = [('284235722', (140, 142)),
#                               ('284819997', (150, 152)),
#                               ('319927587', (120, 122)),
#                               ('284819997', (166, 171)), ('284819997', (173, 178)),
#                               ('284819997', (180, 185)), ('284819997', (187, 192)),
#                               ('319927587', (189, 194)), ('404593641', (158, 163)),
#                               ('412629178', (148, 153)), ('284235722', (147,152))]
    bnss_key_time_wdw_list = [('284819997', (166, 171)), ('284819997', (173, 178)),
                            ('284819997', (180, 185)), ('284819997', (187, 192)),
                            ('319927587', (189, 194)), ('284235722', (147,152))]

    bnss_key_time_wdw_list = [('284819997', (167, 170)), ('284819997', (174, 177)),
                            ('284819997', (181, 184)), ('284819997', (188, 192)),
                            ('319927587', (190, 193)), ('284235722', (148,152))]

#     bnss_key_time_wdw_list = [('284819997', (167, 169))]
    #Rating Distribution
    bnss_key_time_wdw_list = [('284819997', (168, 169)), ('284819997', (175, 176)),
                            ('284819997', (182, 183)), ('284819997', (189, 190)),
                            ('319927587', (191, 192)), ('284235722', (149,150))]
    #Time wise Rating
    bnss_key_time_wdw_list = [('284819997', (167, 170)), ('284819997', (174, 177)),
                            ('284819997', (181, 184)), ('284819997', (188, 191)),
                            ('319927587', (190, 193)), ('284235722', (148,151))]

    CommonUtil.doGatherEvidence(csvFolder, plotDir, bnss_key_time_wdw_list=bnss_key_time_wdw_list)

