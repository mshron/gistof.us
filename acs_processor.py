import csv

def addone(n):
    return {1: int(n[0])+1}
default_cols_to_fns = {('B01003_1_EST',): addone}

def process_acs_file(acs_file='test_acs.txt', cols_to_fns_map=default_cols_to_fns, shelf='test.shelf'):

    #open the file as a CSV with delimiter '|'
    csvfile = csv.reader(open(acs_file, 'rb'), delimiter='|')    
    
    #store the first row as the column names
    machine_names = csvfile.next()
    
    #store the second row as the column human-readable names
    human_names = csvfile.next()
        
    #until the end of the file, for each row...
    for row in csvfile:

        #rewrite the row as a dict (key = column, value = value)
        row_dict = {}
        for i, name in enumerate(machine_names):
            row_dict[name] = row[i]
                    
        #transform the rowdict, getting back a transformed dict
        transformed_row = transform_row(row_dict, cols_to_fns_map)
        
        print transformed_row
        #shelve it
    

def transform_row(row_dict, cols_to_fns_map):
    row_transformation = {}
    
    #for each transformation we need to do per row
    for cols in cols_to_fns_map:     #cols is a tuple of col names
        
        #check if this is actually a function?
        fn = cols_to_fns_map[cols]
                       
        #check if each column is in the data
        #if so, add it to cols_values
        cols_values = []  #cols_values is the arguments to fn
        for col in cols:
            if not col in row_dict:
                raise IndexError('No column %s in the data' % col)
            else:
                cols_values.append(row_dict[col])
        
        row_transformation.update(fn(cols_values))
    
    #return the row transformation
    return row_transformation
    
    
#transforming rows
#row transform takes in 1. row as dict, 2. cols->fn map
#for each element of the map, either call fn or throw error
#for each successfully called map fn, add the returned k/v pair to the output hash
#return the hash


#map fns
#take in a tuple of values, output key/value pair
#key is ultimate JSON name of doom, value is uJSON value od



def addtwo(n):
    return {2: n[0]+2}
    
def sum(n):
    return {'s': n[0]+n[1]}

cols_to_fns_map = {('first',): addone, 
                   ('second',): addtwo,
                   ('first','second'): sum}
row_dict = {'first': 10, 'second': 20, 'third': 50}

