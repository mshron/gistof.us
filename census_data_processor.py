import csv
import shelve
import sys
import numpy as np

def addone(n):
    return int(n)+1

def id(x):
    return x

def ratio((a,b)):
  try:
        _r =  float(a)/float(b)
        return "%.04f"%_r
  except: return "***"

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

def list_id(longtuple):
    list = [int(x) for x in longtuple if can_int(x)]

    return list

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
              ('age', 'distribution',
                ('Universe:  TOTAL POPULATION: Male; Under 5 years (Estimate)',
                'Universe:  TOTAL POPULATION: Male; 5 to 9 years (Estimate)',
                'Universe:  TOTAL POPULATION: Male; 10 to 14 years (Estimate)',
                'Universe:  TOTAL POPULATION: Male; 15 to 17 years (Estimate)',
                'Universe:  TOTAL POPULATION: Male; 18 and 19 years (Estimate)',
                'Universe:  TOTAL POPULATION: Male; 20 years (Estimate)',
                'Universe:  TOTAL POPULATION: Male; 21 years (Estimate)',
                'Universe:  TOTAL POPULATION: Male; 22 to 24 years (Estimate)',
                'Universe:  TOTAL POPULATION: Male; 25 to 29 years (Estimate)',
                'Universe:  TOTAL POPULATION: Male; 30 to 34 years (Estimate)',
                'Universe:  TOTAL POPULATION: Male; 35 to 39 years (Estimate)',
                'Universe:  TOTAL POPULATION: Male; 40 to 44 years (Estimate)',
                'Universe:  TOTAL POPULATION: Male; 45 to 49 years (Estimate)',
                'Universe:  TOTAL POPULATION: Male; 50 to 54 years (Estimate)',
                'Universe:  TOTAL POPULATION: Male; 55 to 59 years (Estimate)',
                'Universe:  TOTAL POPULATION: Male; 60 and 61 years (Estimate)',
                'Universe:  TOTAL POPULATION: Male; 62 to 64 years (Estimate)',
                'Universe:  TOTAL POPULATION: Male; 65 and 66 years (Estimate)',
                'Universe:  TOTAL POPULATION: Male; 67 to 69 years (Estimate)',
                'Universe:  TOTAL POPULATION: Male; 70 to 74 years (Estimate)',
                'Universe:  TOTAL POPULATION: Male; 75 to 79 years (Estimate)',
                'Universe:  TOTAL POPULATION: Male; 80 to 84 years (Estimate)',
                'Universe:  TOTAL POPULATION: Male; 85 years and over (Estimate)',
                'Universe:  TOTAL POPULATION: Female; Under 5 years (Estimate)',
                'Universe:  TOTAL POPULATION: Female; 5 to 9 years (Estimate)',
                'Universe:  TOTAL POPULATION: Female; 10 to 14 years (Estimate)',
                'Universe:  TOTAL POPULATION: Female; 15 to 17 years (Estimate)',
                'Universe:  TOTAL POPULATION: Female; 18 and 19 years (Estimate)',
                'Universe:  TOTAL POPULATION: Female; 20 years (Estimate)',
                'Universe:  TOTAL POPULATION: Female; 21 years (Estimate)',
                'Universe:  TOTAL POPULATION: Female; 22 to 24 years (Estimate)',
                'Universe:  TOTAL POPULATION: Female; 25 to 29 years (Estimate)',
                'Universe:  TOTAL POPULATION: Female; 30 to 34 years (Estimate)',
                'Universe:  TOTAL POPULATION: Female; 35 to 39 years (Estimate)',
                'Universe:  TOTAL POPULATION: Female; 40 to 44 years (Estimate)',
                'Universe:  TOTAL POPULATION: Female; 45 to 49 years (Estimate)',
                'Universe:  TOTAL POPULATION: Female; 50 to 54 years (Estimate)',
                'Universe:  TOTAL POPULATION: Female; 55 to 59 years (Estimate)',
                'Universe:  TOTAL POPULATION: Female; 60 and 61 years (Estimate)',
                'Universe:  TOTAL POPULATION: Female; 62 to 64 years (Estimate)',
                'Universe:  TOTAL POPULATION: Female; 65 and 66 years (Estimate)',
                'Universe:  TOTAL POPULATION: Female; 67 to 69 years (Estimate)',
                'Universe:  TOTAL POPULATION: Female; 70 to 74 years (Estimate)',
                'Universe:  TOTAL POPULATION: Female; 75 to 79 years (Estimate)',
                'Universe:  TOTAL POPULATION: Female; 80 to 84 years (Estimate)',
                'Universe:  TOTAL POPULATION: Female; 85 years and over (Estimate)'),
                age_distribution),

              ('sex_by_age', 'male',
                ('Universe:  TOTAL POPULATION: Male; Under 5 years (Estimate)',
                'Universe:  TOTAL POPULATION: Male; 5 to 9 years (Estimate)',
                'Universe:  TOTAL POPULATION: Male; 10 to 14 years (Estimate)',
                'Universe:  TOTAL POPULATION: Male; 15 to 17 years (Estimate)',
                'Universe:  TOTAL POPULATION: Male; 18 and 19 years (Estimate)',
                'Universe:  TOTAL POPULATION: Male; 20 years (Estimate)',
                'Universe:  TOTAL POPULATION: Male; 21 years (Estimate)',
                'Universe:  TOTAL POPULATION: Male; 22 to 24 years (Estimate)',
                'Universe:  TOTAL POPULATION: Male; 25 to 29 years (Estimate)',
                'Universe:  TOTAL POPULATION: Male; 30 to 34 years (Estimate)',
                'Universe:  TOTAL POPULATION: Male; 35 to 39 years (Estimate)',
                'Universe:  TOTAL POPULATION: Male; 40 to 44 years (Estimate)',
                'Universe:  TOTAL POPULATION: Male; 45 to 49 years (Estimate)',
                'Universe:  TOTAL POPULATION: Male; 50 to 54 years (Estimate)',
                'Universe:  TOTAL POPULATION: Male; 55 to 59 years (Estimate)',
                'Universe:  TOTAL POPULATION: Male; 60 and 61 years (Estimate)',
                'Universe:  TOTAL POPULATION: Male; 62 to 64 years (Estimate)',
                'Universe:  TOTAL POPULATION: Male; 65 and 66 years (Estimate)',
                'Universe:  TOTAL POPULATION: Male; 67 to 69 years (Estimate)',
                'Universe:  TOTAL POPULATION: Male; 70 to 74 years (Estimate)',
                'Universe:  TOTAL POPULATION: Male; 75 to 79 years (Estimate)',
                'Universe:  TOTAL POPULATION: Male; 80 to 84 years (Estimate)',
                'Universe:  TOTAL POPULATION: Male; 85 years and over (Estimate)'),
                sex_by_age),

              ('sex_by_age', 'female',
                ('Universe:  TOTAL POPULATION: Female; Under 5 years (Estimate)',
                'Universe:  TOTAL POPULATION: Female; 5 to 9 years (Estimate)',
                'Universe:  TOTAL POPULATION: Female; 10 to 14 years (Estimate)',
                'Universe:  TOTAL POPULATION: Female; 15 to 17 years (Estimate)',
                'Universe:  TOTAL POPULATION: Female; 18 and 19 years (Estimate)',
                'Universe:  TOTAL POPULATION: Female; 20 years (Estimate)',
                'Universe:  TOTAL POPULATION: Female; 21 years (Estimate)',
                'Universe:  TOTAL POPULATION: Female; 22 to 24 years (Estimate)',
                'Universe:  TOTAL POPULATION: Female; 25 to 29 years (Estimate)',
                'Universe:  TOTAL POPULATION: Female; 30 to 34 years (Estimate)',
                'Universe:  TOTAL POPULATION: Female; 35 to 39 years (Estimate)',
                'Universe:  TOTAL POPULATION: Female; 40 to 44 years (Estimate)',
                'Universe:  TOTAL POPULATION: Female; 45 to 49 years (Estimate)',
                'Universe:  TOTAL POPULATION: Female; 50 to 54 years (Estimate)',
                'Universe:  TOTAL POPULATION: Female; 55 to 59 years (Estimate)',
                'Universe:  TOTAL POPULATION: Female; 60 and 61 years (Estimate)',
                'Universe:  TOTAL POPULATION: Female; 62 to 64 years (Estimate)',
                'Universe:  TOTAL POPULATION: Female; 65 and 66 years (Estimate)',
                'Universe:  TOTAL POPULATION: Female; 67 to 69 years (Estimate)',
                'Universe:  TOTAL POPULATION: Female; 70 to 74 years (Estimate)',
                'Universe:  TOTAL POPULATION: Female; 75 to 79 years (Estimate)',
                'Universe:  TOTAL POPULATION: Female; 80 to 84 years (Estimate)',
                'Universe:  TOTAL POPULATION: Female; 85 years and over (Estimate)'),
                sex_by_age),

              ('hispanic_or_latino', 'pct_hispanic_or_latino',
                ('Universe:  TOTAL POPULATION: Hispanic or Latino (Estimate)',
                 'Universe:  TOTAL POPULATION: Total (Estimate)'),
                ratio),

              ('race', 'totals',
                ('Universe:  TOTAL POPULATION: White alone (Estimate)',
                'Universe:  TOTAL POPULATION: Black or African American alone (Estimate)',
                'Universe:  TOTAL POPULATION: American Indian and Alaska Native alone (Estimate)',
                'Universe:  TOTAL POPULATION: Asian alone (Estimate)',
                'Universe:  TOTAL POPULATION: Native Hawaiian and Other Pacific Islander alone (Estimate)',
                'Universe:  TOTAL POPULATION: Some other race alone (Estimate)',
                'Universe:  TOTAL POPULATION: Two or more races (Estimate)'),
                list_id),
              
              ('race', 'totals_moe',
                ('Universe:  TOTAL POPULATION: White alone(Margin of Error (+/-))',
                'Universe:  TOTAL POPULATION: Black or African American alone(Margin of Error (+/-))',
                'Universe:  TOTAL POPULATION: American Indian and Alaska Native alone(Margin of Error (+/-))',
                'Universe:  TOTAL POPULATION: Asian alone(Margin of Error (+/-))',
                'Universe:  TOTAL POPULATION: Native Hawaiian and Other Pacific Islander alone(Margin of Error (+/-))',
                'Universe:  TOTAL POPULATION: Some other race alone(Margin of Error (+/-))',
                'Universe:  TOTAL POPULATION: Two or more races(Margin of Error (+/-))'),
list_id),

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
    
