#!/usr/bin/env python

import csv
import shelve
import sys
import numpy as np
import transforms_columns as cols

def id(x):
    try:
        return int(x)
    except:
        return str(x)

def list_id(longtuple):
    list = [int(x) for x in longtuple if can_int(x)]
    return list

def ratio((a,b)):
    try:
        _r =  float(a)/float(b)
        return "%.04f"%_r
    except: return "***"

#Simpson Diversity Index
def simpson_raw_counts(longtuple):
    d = [int(x) for x in longtuple if can_int(x)]
    total = sum(d)
    #prevent division by zero
    if total == 0:
        return "-1"
    try:
        pcts = [float(x)/float(total) for x in d]
    except: return "***"
    return simpson_pcts(pcts)

def simpson_pcts(d):
    a = 1.0
    for i in range(len(d)):
        a = a - (d[i]**2)
    return "%.04f"%a

def int_0nan(x):
    if can_int(x):
        return int(x)
    else:
        return 0

def can_int(x):
    try: 
        int(x)
        return True
    except:
        return False
    
def sex_by_age(longtuple):
    _ages = [int(x) for x in longtuple if can_int(x)]
    _ages_arr = np.asarray(_ages)

    # five age categories
    out = [0]*8
    out[0] = _ages_arr[0:2].sum()
    out[1] = _ages_arr[3:5].sum()
    out[2] = _ages_arr[6:8].sum()
    out[3] = _ages_arr[9:11].sum()
    out[4] = _ages_arr[12:14].sum()
    out[5] = _ages_arr[15:17].sum()
    out[6] = _ages_arr[18:20].sum()
    out[7] = _ages_arr[21:23].sum()
    return out


def age_distribution(longtuple):
    _ages = [int(x) for x in longtuple if can_int(x)]
    _ages_arr = np.asarray(_ages)

    # collapse men and women together
    ages = _ages_arr[:23] + _ages_arr[23:]
    out = [0]*5
    out[0] = ages[0:6].sum()
    out[1] = ages[6:11].sum()
    out[2] = ages[11:15].sum()
    out[3] = ages[15:21].sum()
    out[4] = ages[21:23].sum()
    return out

def edu_sums(l):
    lt9th_indices = [6,22,38,54,70,88,104,120,136,152]

    lt9 = sum([l[x] for x in lt9th_indices])
    hs_no_degree = sum([l[x+2] for x in lt9th_indices])
    hs_grad_or_equiv = sum([l[x+4] for x in lt9th_indices])
    college_no_degree = sum([l[x+6] for x in lt9th_indices])
    associates_degree = sum([l[x+8] for x in lt9th_indices])
    bachelors_degree = sum([l[x+10] for x in lt9th_indices])
    grad_or_professional_degree = sum([l[x+12] for x in lt9th_indices])
    
    out = [lt9, hs_no_degree, hs_grad_or_equiv, college_no_degree,
            associates_degree, bachelors_degree, grad_or_professional_degree]
    return out

def educational_attainment_18plus(longtuple):
    # sum each educational level from each age group
    # results will be list: 
    # [<9th, some HS, HSgrad/GED, some college, assoc, bach, grad/professional]
    
    # this is probably bad - replaces NaN values in the data with 0
    # we should handle these some other way, I assume
    _attains = [int_0nan(x) for x in longtuple] 
    _attains_arr = np.asarray(_attains)

    total_18plus = _attains_arr[0]
    raw_counts = edu_sums(_attains_arr)

    return [ratio((x,total_18plus)) for x in raw_counts]

def educational_attainment_simpson(longtuple):

    _attains = [int_0nan(x) for x in longtuple] 
    _attains_arr = np.asarray(_attains)

    raw_counts = edu_sums(_attains_arr)
    return simpson_raw_counts(raw_counts)


def veteran_status(longtuple):
    _vets = [int_0nan(x) for x in longtuple]
    _vets_arr = np.asarray(_vets)

    total_civilian_pop = _vets_arr[0]

    if total_civilian_pop == 0:
        return 0
        
    vet_columns = [6, 12, 18, 24, 30, 38, 44, 50, 56, 62]
    total_veteran_pop = sum([_vets_arr[x] for x in vet_columns])

    return ratio((total_veteran_pop, total_civilian_pop)) 

def pct_live_alone(longtuple):
    _households = [int_0nan(x) for x in longtuple]
    _households_arr = np.asarray(_households)

    total_occupied_housing_units = _households_arr[0]
    if total_occupied_housing_units == 0:
        return 0

    total_live_alone = _households_arr[4] + _households_arr[20]
    
    return ratio((total_live_alone, total_occupied_housing_units))

def pct_below_150pc(longtuple):
    _poverty = [int_0nan(x) for x in longtuple]
    _poverty_arr = np.asarray(_poverty)

    people_below_150 = _poverty_arr[0] + _poverty_arr[1]
    total_people = _poverty_arr[2]

    return ratio((people_below_150, total_people))
    

def home_language_distribution(longtuple):
    _languages = [int_0nan(x) for x in longtuple]  
    _languages_arr = np.asarray(_languages)

    over_5 = _languages_arr[0]
    distribution = _languages_arr[1:]
    pct_distribution = map(lambda x: ratio((x,over_5)), distribution)

    return pct_distribution

def pct_linguistic_isolation(longtuple):
    _lingiso = [int_0nan(x) for x in longtuple]  
    _lingiso_arr = np.asarray(_lingiso)

    total_households = _lingiso_arr[0]
    isolated_households = sum(_lingiso_arr[1:]) 

    return ratio((isolated_households, total_households))
 
def linguistic_isolation_distribution(longtuple):
    _lingiso = [int_0nan(x) for x in longtuple]  
    _lingiso_arr = np.asarray(_lingiso)
    
    # spanish, other indo-european, asian/pac island, other
    return list(_lingiso_arr[1:])


def county_name(geostring):
    return geostring.split(',')[1].strip()    

def state_name(geostring):
    return geostring.split(',')[2].strip()

def tract_number(geostring):
    return geostring.split(',')[0].split()[2].strip() 

  
transforms = [('population','total',
               'Universe:  TOTAL POPULATION: Total (Estimate)',
                id),
              ('population','total_moe',
               'Universe:  TOTAL POPULATION: Total(Margin of Error (+/-))', 
                id),

              ('population', 'population_density',
               ('Universe:  TOTAL POPULATION: Total (Estimate)', 
                'Land Area (Square Miles)'),
               ratio),

              ('sex','male',
                'Universe:  TOTAL POPULATION: Male (Estimate)',
                id),
              ('sex', 'male_moe',
               'Universe:  TOTAL POPULATION: Male(Margin of Error (+/-))',
               id),
              ('sex','female',
                'Universe:  TOTAL POPULATION: Female (Estimate)',
                id),
              ('sex', 'female_moe',
               'Universe:  TOTAL POPULATION: Female(Margin of Error (+/-))',
               id),
#poverty from table B06012
              ('poverty', 'below_100pc',
               'Universe:  POPULATION IN THE UNITED STATES FOR WHOM POVERTY STATUS IS DETERMINED: Below 100 percent of the poverty level (Estimate)',
               id),
              ('poverty', 'below_100pc_moe',
               'Universe:  POPULATION IN THE UNITED STATES FOR WHOM POVERTY STATUS IS DETERMINED: Below 100 percent of the poverty level(Margin of Error (+/-))',
               id),
              ('poverty', 'above100pc_below_150pc',
               'Universe:  POPULATION IN THE UNITED STATES FOR WHOM POVERTY STATUS IS DETERMINED: 100 to 149 percent of the poverty level (Estimate)',
               id),
              ('poverty', 'above100pc_below_150pc_moe',
               'Universe:  POPULATION IN THE UNITED STATES FOR WHOM POVERTY STATUS IS DETERMINED: 100 to 149 percent of the poverty level(Margin of Error (+/-))',
               id),
              ('poverty', 'above150pc',
               'Universe:  POPULATION IN THE UNITED STATES FOR WHOM POVERTY STATUS IS DETERMINED: At or above 150 percent of the poverty level (Estimate)',
               id),
              ('poverty', 'above150pc_moe',
               'Universe:  POPULATION IN THE UNITED STATES FOR WHOM POVERTY STATUS IS DETERMINED: At or above 150 percent of the poverty level(Margin of Error (+/-))',
               id),
              ('poverty', 'pct_below_100pc',
               ('Universe:  POPULATION IN THE UNITED STATES FOR WHOM POVERTY STATUS IS DETERMINED: Below 100 percent of the poverty level (Estimate)',
                'Universe:  POPULATION IN THE UNITED STATES FOR WHOM POVERTY STATUS IS DETERMINED: Total (Estimate)'),
               ratio),

              ('poverty', 'pct_below_150pc',
                ('Universe:  POPULATION IN THE UNITED STATES FOR WHOM POVERTY STATUS IS DETERMINED: 100 to 149 percent of the poverty level (Estimate)',
                'Universe:  POPULATION IN THE UNITED STATES FOR WHOM POVERTY STATUS IS DETERMINED: Below 100 percent of the poverty level (Estimate)',
                'Universe:  POPULATION IN THE UNITED STATES FOR WHOM POVERTY STATUS IS DETERMINED: Total (Estimate)'), 
                pct_below_150pc),
               
              ('born', 'pct_foreign',
               ('Universe:  POPULATION IN THE UNITED STATES FOR WHOM POVERTY STATUS IS DETERMINED: Foreign born (Estimate)',
                'Universe:  POPULATION IN THE UNITED STATES FOR WHOM POVERTY STATUS IS DETERMINED: Total (Estimate)'),
               ratio),
              ('age', 'distribution', cols.age_distribution, age_distribution),

              ('sex_by_age', 'male', cols.age_distribution[:23], sex_by_age),

              ('sex_by_age', 'female', cols.age_distribution[23:], sex_by_age),

              ('hispanic_or_latino', 'pct_hispanic_or_latino',
                ('Universe:  TOTAL POPULATION: Hispanic or Latino (Estimate)',
                 'Universe:  TOTAL POPULATION: Total (Estimate)'),
                ratio),

              ('race', 'distribution', cols.race_distribution, list_id),
              
              ('race', 'distribution_moe', cols.race_distribution_moe, list_id),

              ('race', 'distribution_simpson', cols.race_distribution, simpson_raw_counts),

              ('race', 'white_not_latino', 
               'Universe:  TOTAL POPULATION: Not Hispanic or Latino; White alone (Estimate)',
               id),

              ('race', 'pct_white_not_latino',
              ('Universe:  TOTAL POPULATION: Not Hispanic or Latino; White alone (Estimate)',
               'Universe:  TOTAL POPULATION: Total (Estimate)'), ratio),

              ('educational_attainment_18plus', 'distribution', 
               cols.educational_attainment_18plus, educational_attainment_18plus),
              
              ('educational_attainment_18plus', 'total',
               'Universe:  POPULATION 18 YEARS AND OVER: Total (Estimate)', id),

              ('educational_attainment_18plus', 'distribution_simpson',
               cols.educational_attainment_18plus, educational_attainment_simpson),

              ('veteran_status', 'pct_veteran', cols.veteran_status, veteran_status),

              ('household_size', 'pct_live_alone', 
               ('Universe:  HOUSEHOLDS: Nonfamily households; 1-person household (Estimate)','Universe:  TOTAL POPULATION: Total (Estimate)'), ratio),

              ('language', 'spoken_at_home_distribution', 
                cols.language_spoken_at_home, home_language_distribution),

              ('language', 'spoken_at_home_distribution_simpson',
                cols.language_spoken_at_home, simpson_raw_counts),

              ('language', 'total_population_over_5',
                'B16001_1_EST', id),

              ('language', 'pct_linguistic_isolation',
                cols.linguistic_isolation, pct_linguistic_isolation),
              ('language', 'linguistic_isolation_distribution',
                cols.linguistic_isolation, linguistic_isolation_distribution),

              ('loc', 'lat', 'INTPTLAT', id),
              ('loc', 'lon', 'INTPTLONG', id),
              ('loc', 'county', 'Geography', county_name),
              ('loc', 'state', 'Geography', state_name),
              ('loc', 'tract_number', 'Geography', tract_number),
              ('loc', 'land_area', 'Land Area (Square Miles)', id),
              ('loc', 'water_area', 'Water Area (Square Miles)', id),
              ('population','nonexistant', 'FOOO', id)]

def setup_shelf(shelf_file):
    shelf = shelve.open(shelf_file)
    return shelf

def transform(data, transforms):
    out = {}
    for _di,_k,_t,_fn in transforms:
        if isinstance(_t,tuple):
            try:
                _dat = tuple(data[t] for t in _t)  
            except:
               continue 
        else:
            try:
                _dat = data[_t]
            except:
                continue
        out.setdefault(_di,{})[_k] = _fn(_dat)
    return out


def main():
    shelf = setup_shelf(sys.argv[1])
    for i,line in enumerate(csv.reader(sys.stdin, delimiter='|')):
        if i==0:
            continue

        line = map(lambda l: l.decode('ISO-8859-1'), line)
        
        if i==1:
            titles = line
            continue
        data = dict(zip(titles,line))
        out = transform(data,transforms)
        id = str(data['Geography Identifier'])
        print {id: out}
        shelf[id] = out

        if (i!= 0) and ((i%100) == 0):
             shelf.sync()
    shelf.close()
         

if __name__=="__main__":
    main()
    
