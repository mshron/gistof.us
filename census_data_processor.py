#!/usr/bin/env python

import csv
import shelve
import sys
import numpy as np
import transforms_columns as cols

def addone(n):
    return int(n)+1

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

def educational_attainment_18plus(longtuple):
    # sum each educational level from each age group
    # results will be list: 
    # [<9th, some HS, HSgrad/GED, some college, assoc, bach, grad/professional]
    
    # this is probably bad - replaces NaN values in the data with 0
    # we should handle these some other way, I assume
    _attains = [int_0nan(x) for x in longtuple] 
    _attains_arr = np.asarray(_attains)

    lt9th_indices = [6,22,38,54,70,88,104,120,136,152]

    print len(longtuple)
    lt9 = sum([_attains_arr[x] for x in lt9th_indices])
    hs_no_degree = sum([_attains_arr[x+2] for x in lt9th_indices])
    hs_grad_or_equiv = sum([_attains_arr[x+4] for x in lt9th_indices])
    college_no_degree = sum([_attains_arr[x+6] for x in lt9th_indices])
    associates_degree = sum([_attains_arr[x+8] for x in lt9th_indices])
    bachelors_degree = sum([_attains_arr[x+10] for x in lt9th_indices])
    grad_or_professional_degree = sum([_attains_arr[x+12] for x in lt9th_indices])

    out = [lt9, hs_no_degree, hs_grad_or_equiv, college_no_degree,
            associates_degree, bachelors_degree, grad_or_professional_degree]

    return out

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

def home_language_distribution(longtuple):
    _languages = [int_0nan(x) for x in longtuple]  
    _languages_arr = np.asarray(_languages)

    total_pop_over_5 = _languages_arr[0]

    english_only = ratio((sum([_languages_arr[x] for x in [2,12,22]]), total_pop_over_5))
    spanish = ratio((sum([_languages_arr[x] for x in [4,14,24]]), total_pop_over_5))
    other_indo_european = ratio((sum([_languages_arr[x] for x in [6,16,26]]), total_pop_over_5))
    asian_or_pacific_island = ratio((sum([_languages_arr[x] for x in [8,18,28]]), total_pop_over_5))
    other = ratio((sum([_languages_arr[x] for x in [10,20,30]]), total_pop_over_5))
    
    out = [english_only, spanish, other_indo_european, 
            asian_or_pacific_island, other]


    return out
        

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
              ('sex','male',
                'Universe:  TOTAL POPULATION: Male (Estimate)',
                addone),
              ('sex', 'male_moe',
               'Universe:  TOTAL POPULATION: Male(Margin of Error (+/-))',
               id),
              ('sex','female',
                'Universe:  TOTAL POPULATION: Female (Estimate)',
                addone),
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
               ('Universe:  POPULATION IN THE UNITED STATES FOR WHOM POVERTY STATUS IS DETERMINED: 100 to 149 percent of the poverty level (Estimate)',
                'Universe:  POPULATION IN THE UNITED STATES FOR WHOM POVERTY STATUS IS DETERMINED: Total (Estimate)'),
               ratio),
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

              ('veteran_status', 'pct_veteran', cols.veteran_status, veteran_status),

              ('household_size', 'pct_live_alone', cols.household_size, pct_live_alone),

              ('language_spoken_at_home', 'distribution', 
                cols.language_at_home, home_language_distribution),

              ('loc', 'lat', 'INTPTLAT', id),
              ('loc', 'lon', 'INTPTLONG', id),
              ('loc', 'county', 'Geography', county_name),
              ('loc', 'state', 'Geography', state_name),
              ('loc', 'tract_number', 'Geography', tract_number),

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
    
