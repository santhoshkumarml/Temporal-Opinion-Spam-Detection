__author__ = 'santhosh'


def readFileAndReturnResult(fil):
    result_Dict = dict()
    with open(fil) as f:
        result = tuple()
        for line in f:
            content = 'result='
            content = content+line
            exec(content)
            bnss_key, time_window, changed_dims = result
            result_Dict[(bnss_key, time_window)] = changed_dims
    return result_Dict

def jaccard(gar_file, lar_file):
    gar_dict = readFileAndReturnResult(gar_file)
    lar_dict = readFileAndReturnResult(lar_file)
    jaccard_dict = dict()
    for key in gar_dict.keys():
        gar_set = gar_dict[key]
        lar_set = lar_dict[key]
        inter = gar_set.intersection(lar_set)
        uni = gar_set.union(lar_set)
        if len(inter) == 0 or len(uni) == 0:
            jaccard_dict[key] = 0.0
        else:
            jaccard_dict[key] = float(len(inter))/float(len(uni))
    print sorted(jaccard_dict.items(), key=lambda item:item[1], reverse=True)


gar_file = '/media/santhosh/Data/workspace/datalab/data/stats/result_gar.txt'
lar_file = '/media/santhosh/Data/workspace/datalab/data/stats/result_lar.txt'
jaccard(gar_file, lar_file)