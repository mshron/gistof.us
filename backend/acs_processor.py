import csv
import shelve

def addone(n):
    return {'population': int(n[0])+1}
default_cols_to_fns = {('B01003_1_EST',): addone}

def process_acs_file(acs_file='test_acs.txt', cols_to_fns_map=default_cols_to_fns, shelf_file='test.shelf'):

    #open the file as a CSV with delimiter '|'
    csvfile = csv.reader(open(acs_file, 'rb'), delimiter='|')    
    
    #open the shelf
    shelf = shelve.open(shelf_file)
    
    #store the first row as the column names
    machine_names = csvfile.next()
    
    #store the second row as the column human-readable names
    human_names = csvfile.next()
        
    #until the end of the file, for each row...
    for i, row in enumerate(csvfile):

        #rewrite the row as a dict (key = column, value = value)
        row_dict = {}
        for i, name in enumerate(machine_names):
            row_dict[name] = row[i]
                    
        #transform the rowdict, getting back a transformed dict
        transformed_row = transform_row(row_dict, cols_to_fns_map)
                
        #shelve it        
        id = row_dict['GEO_ID2']
        shelf[id] = transformed_row
        
        if (i != 0) and ((i%100) == 0):
            shelf.sync()
            
    shelf.close()
    

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
        

if __name__=='__main__':
    process_acs_file()
