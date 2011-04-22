def reach(data, cat, vs, ps):
    d = data[cat]
    value = d[vs]
    percentile = d[ps]
    return float(value), float(percentile)

def prepare((s, values)):
    out =   {'sentence': values[0], 
            'category': values[1],
            'name': values[2]}
    return out


def poverty(data):
    vs = 'pct_below_100pc'
    ps = 'pct_below_100pc_percentile'
    v, p = reach(data, 'poverty', vs, ps)
    if p > 80:
        ss = '...many people are income-*poor* (%.02f%%)'%float(100*v)
    elif p < 20:
        ss = '...*few* people are income-poor (%.02f%%)'%float(100*v)
    else:
        ss = '...people are not unusually poor (%.02f%%)'%float(100*v)
    return (v,(ss, vs, ps))

transforms = [poverty]

def parse(data):
    out = []
    for t in transforms:
        out.append(t(data))
    return map(prepare,sorted(out, key=lambda x: float(x[0])))
        
