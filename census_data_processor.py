import csv
import shelve
import sys

def addone(n):
    return int(n)+1

def id(x):
    return x

transforms = [('population','value',
               'Universe:  TOTAL POPULATION: Total (Estimate)',
                addone),
              ('population','moe',
               'Universe:  TOTAL POPULATION: Total(Margin of Error (+/-))', 
               id),
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
    
