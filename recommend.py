def reach(data, cat, vs, ps):
    d = data[cat]
    value = d[vs]
    percentile = d[ps]
    return float(value), float(percentile)

def prepare((s, values)):
    out =   {'sentence': values[0], 
            'name': values[1],
            'category': values[3],
    }
    return out


def poverty(data):
    cat = 'poverty'
    vs = 'pct_below_100pc'
    ps = 'pct_below_100pc_percentile'
    v, p = reach(data, cat, vs, ps)
    if p > 80:
        ss = '...many people are income-*poor* (%.02f%%)'%float(100*v)
    elif p < 20:
        ss = '...*few* people are income-poor (%.02f%%)'%float(100*v)
    else:
        ss = '...people are not unusually poor (%.02f%%)'%float(100*v)
    return (v,(ss, vs, ps, cat))

def hispanic(data):
    cat = 'hispanic_or_latino'
    vs = 'pct_hispanic_or_latino'
    ps = 'pct_hispanic_or_latino_percentile'
    v, p = reach(data, cat, vs, ps)
    if p > 80:
        ss = '...a large portion of the population is hispanic/latino (%.02f%%)'%float(100*v)
    elif p < 20:
        ss = '...a relatively *small portion* of the population is hispanic/latino (%.02f%%)'%float(100*v)
    else:
        ss = '...the population is not particularly hispanic/latino (%.02f%%)'%float(100*v)
    return (v,(ss, vs, ps, cat))

def veteran(data):
    cat = 'veteran_status'
    vs = 'pct_veteran'
    ps = 'pct_veteran_percentile'
    v, p = reach(data, cat, vs, ps)
    if p > 80:
        ss = "...many people are *veterans* (%.02f%%)"%float(100*v)
    if p < 20:
        ss = "...few people are *veterans* (%.02f%%)"%float(100*v)
    else:
        ss = "...there are not an especially high concentration of veterans (%.02f%%)"%float(100*v)
    return (v,(ss, vs, ps, cat))


transforms = [poverty, hispanic, veteran]

sortfcn = lambda x: float(abs(x[0]-50))

def parse(data):
    out = []
    for t in transforms:
        out.append(t(data))
    return map(prepare,sorted(out, key=sortfcn))
        
