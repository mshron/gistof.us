import csv
import shelve
import sys
import numpy as np
import transforms_columns as cols

def addone(n):
    return int(n)+1

def id(x):
    return x

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
    out = [0]*5
    out[0] = _ages_arr[0:6].sum()
    out[1] = _ages_arr[6:11].sum()
    out[2] = _ages_arr[11:15].sum()
    out[3] = _ages_arr[15:21].sum()
    out[4] = _ages_arr[21:23].sum()
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

              ('educational_attainment_18plus', 'distribution', 
               cols.educational_attainment_18plus, educational_attainment_18plus),
              
              ('educational_attainment_18plus', 'total',
               'Universe:  POPULATION 18 YEARS AND OVER: Total (Estimate)', id),

              ('veteran_status', 'pct_veteran', cols.veteran_status, veteran_status),

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
    for i,line in enumerate(csv.reader(sys.stdin,
            delimiter='|')):
        if i==0:
            continue
        if i==1:
            titles = line
            continue
        data = dict(zip(titles,line))
        out = transform(data,transforms)
        id = data['Geography Identifier']
        print {id: out}
        shelf[id] = out

        if (i!= 0) and ((i%100) == 0):
             shelf.sync()
    shelf.close()
         

if __name__=="__main__":
    main()
    
