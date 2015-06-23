__author__ = 'santhosh'


def readFileAndReturnResult(fil):
    result_Dict = dict()
    with open(fil) as f:
        result = tuple()
        for line in f:
            content = 'result'
            content = content+f.readline()
            exec(content)
            bnss_key, time_window, changed_dims = content
            result_Dict[(bnss_key, time_window)] = changed_dims

def jaccard(gar_file, lar_file):
    gar_dict = readFileAndReturnResult(gar_file)
    lar_dict = readFileAndReturnResult(lar_file)
    jaccard_dict = dict()
    for key in gar_dict.keys():
        gar_set = gar_dict[key]
        lar_set = lar_dict[key]
        inter = gar_set.intersection(lar_set)
        uni = gar_set.union(lar_set)
        jaccard_dict[key] = float(len(inter))/float(len(uni))
    print jaccard_dict



