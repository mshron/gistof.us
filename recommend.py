race_categories = ['White alone', 'Black alone', 'American Indian or Alaska Native alone', 'Asian alone', 'Native Hawaiian or Pacific Islander alone', 'Some other race alone', 'Two or more races']

def reach(data, cat, vs, ps):
    d = data[cat]
    value = d[vs]
    percentile = d[ps]
    return float(value), float(percentile)

def prepare(values):
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
    return (ss, vs, ps, cat)

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
    return (ss, vs, ps, cat)

def white_not_latino(data):
    cat = 'race'
    vs = 'pct_white_not_latino'
    ps = 'pct_white_not_latino_percentile'
    v, p = reach(data, cat, vs, ps)
    if p > 80:
        ss = '...people are *mostly White* (and not Latino) (%.02f%%)'%float(100*v)
    #This should say what there are
    if p < 20:
        ss = '...there are few White people (%.02f%%)'%float(100*v)
    else:
        ss = '...there is not a particular concentration or lack of White non-Latino people here (%.02f%%)'%float(100*v)
    return (v, (ss,vs,ps,cat))

def linguistic_isolation(data):
    cat = 'language'
    vs = 'pct_linguistic_isolation'
    ps = 'pct_linguistic_isolation_percentile'
    v, p = reach(data, cat, vs, ps)
    if p > 80:
        ss = '...many households speak no English (%.02f%%)'%float(100*v)
    if p < 20:
        ss = '...very few households lack an English speaking member (%.02f%%)'%float(100*v)
    else:
        ss = '...neither many nor few households are linguistically isolated (%.02f%%)'%float(100*v)
    return (v, (ss,vs,ps,cat))

def live_alone(data):
    cat = 'household_size'
    vs = 'pct_live_alone'
    ps = 'pct_live_alone_percentile'
    v, p = reach(data, cat, vs, ps)
    if p > 80:
        ss = '...*many* people *live alone* (%.02f%%)'%float(100*v)
    if p < 20:
        ss = '...*most* households contain more than just one person (%.02f%%)'%float(100*v)
    else:
        ss = '...a not unusual number of people live alone (%.02f%%)'%float(100*v)
    return (v, (ss,vs,ps,cat))
    

def veteran(data):
    cat = 'veteran_status'
    vs = 'pct_veteran'
    ps = 'pct_veteran_percentile'
    v, p = reach(data, cat, vs, ps)
    if p > 80:
        ss = "...*many* people are *veterans* (%.02f%%)"%float(100*v)
    if p < 20:
        ss = "...*few* people are *veterans* (%.02f%%)"%float(100*v)
    else:
        ss = "...there are not an especially high concentration of veterans (%.02f%%)"%float(100*v)
    return (ss, vs, ps, cat)

def population_density(data):
    cat = 'population'
    vs = 'population_density'
    ps = 'population_density_percentile'
    v, p = reach(data, cat, vs, ps)

    if v > 20000 and v < 30000:
        ss = "...the population density is similar to that of New York, NY (%.02f/sq. mi.)"%float(v)
    elif v > 100000:
        ss = "... the population density is similar to that of Manila, Phillipines, the densest city on earth (%.02f/sq. mi.)"%float(v)
    elif p > 80:
        ss = "...the *population* is *very dense* (%.02f/sq. mi.)"%float(v)
    elif p < 20:
        ss = "...the *population* is *very sparse* (%.02f/sq. mi.)"%float(v)
    else:
        ss = "...population density is not unusually high or low (%.02f/sq. mi.)"%float(v)
    return (ss,vs,ps,cat)



transforms = [poverty, hispanic, veteran, population_density,  
           live_alone, white_not_latino, linguistic_isolation]

sortfcn = lambda x: float(abs(x[0]-50))

def parse(data):
    out = []
    for t in transforms:
        out.append(t(data))
    return map(prepare,out)
        
