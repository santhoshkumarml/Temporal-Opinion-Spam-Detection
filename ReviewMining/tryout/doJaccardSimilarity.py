__author__ = 'santhosh'


def readFileAndReturnResult(fil):
    result_Dict = dict()
    cnt_zero_time_stamps = 0
    with open(fil) as f:
        result = tuple()
        for line in f:
            content = 'result='
            content = content+line
            exec(content)
            bnss_key, time_window, changed_dims = result
            if len(changed_dims) > 0:
                result_Dict[(bnss_key, time_window)] = changed_dims
                cnt_zero_time_stamps += 1
    print cnt_zero_time_stamps
    return result_Dict

def jaccard(gar_file, lar_file):
    gar_dict = readFileAndReturnResult(gar_file)
    lar_dict = readFileAndReturnResult(lar_file)
    keys_in_gar_dict = set(gar_dict.keys())
    keys_in_lar_dict = set(lar_dict.keys())
    keys = keys_in_gar_dict.intersection(keys_in_lar_dict)
    print len(keys)
    jaccard_dict = dict()
    for key in keys:
        gar_set = gar_dict[key]
        lar_set = lar_dict[key]
        inter = gar_set.intersection(lar_set)
        uni = gar_set.union(lar_set)
        if len(inter) == 0 or len(uni) == 0:
            jaccard_dict[key] = 0.0
        else:
            jaccard_dict[key] = float(len(inter))/float(len(uni))
    return jaccard_dict


gar_file = '/media/santhosh/Data/workspace/datalab/data/stats/result_gar.txt'
lar_file = '/media/santhosh/Data/workspace/datalab/data/stats/result_lar.txt'
jaccard_dict = jaccard(gar_file, lar_file)
print jaccard_dict
simil_cnt_dict = {key:0.0 for key in jaccard_dict.values()}
for (bnss,time_window),simila in jaccard_dict.iteritems():
    simil_cnt_dict[simila] += 1

# vals = [(0.8, 5.0), (0.6, 17.0), (0.4, 19.0), (0.2, 32.0),
#         (0.75, 38.0), (0.25, 86.0), (0.6666666666666666, 91.0),
#         (0.0, 58.0), (0.3333333333333333, 164.0), (0.5, 177.0), (1.0, 362.0)]
# print vals
# import matplotlib.pyplot as plt
# plt.title("Jaccard Similarity")
# # ax.set_xticklabels([val[0] for val in vals])
# plt.bar([val[0] for val in vals], [val[1] for val in vals], width=0.05)
# plt.show()