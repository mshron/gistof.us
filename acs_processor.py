def call_fns_on_data(in_file=None, cols_to_fn_map={}, out_file=None):

    #open the file as a CSV with delimiter '|'
    
    #store the first row as the column names
    #store the second row as the column human-readable names
    
    #until the end of the file, for each row...
        #rewrite the row as a dict (key = column, value = value)
        #transform the rowdict, getting back a transformed dict
        #jsonify, hexify, and write out the transformed dict
    

def transform_row(row_dict, cols_to_fns_map):
    for cols in cols_to_fns_map:     #cols is a tuple of col names
        
    #for each k/vs of cols_to_fns_map
        #if all cols are available, call the corresponding fn on the corresponding data and add the returned k/v pair to the output dict
        #if they are not, error!
        
    #return output dict
    
    
#transforming rows
#row transform takes in 1. row as dict, 2. cols->fn map
#for each element of the map, either call fn or throw error
#for each successfully called map fn, add the returned k/v pair to the output hash
#return the hash


#map fns
#take in a tuple of values, output key/value pair
#key is ultimate JSON name of doom, value is uJSON value od

