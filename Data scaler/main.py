# Different numbers mean different things.
# This program takes in a file with numeric values,
# and transforms it into another file with its numeric values scaled.
# It can be applied, for instance, to get blood tests with scaled values from 0 to 1.
# This is very helpful because once you have all the values scaled on the same scale,
# it becomes much easier to perform further analysis.

# Written in vanilla Python by Giuseppe Tavella

# This is what you need to do.

# STEPS
# Please note that all these files need to be created in the same folder as this program.
# For this program, the source files need to be in the same folder as this program,
# and the target files will be saved in the same folder as this program.
# 1) Move the source data that you want to scale in the same folder as this program.
# 2) Create a file called "ref_scale.csv".
#    You can create it with excel and then download it, for easier writing.
#    In this file, create three columns: comp,min,max
#    comp: the column names (also known as features, attributes)
#    min: the minimum value that the values in this colum can take
#    max: the maximum value that the values in this column can take
# 3) Create a file "components_ignore.csv".
#    This file contains a comma-separated list of column names to be ignored in the analysis.
#    Thus, they will not be outputted.

# Note: Make sure to get the spaces around the column names right, as spacing matters.

# WHAT YOU GET as output
# A) You'll get a new file with the scaled values, without the ignored columns.


# Written by Giuseppe Tavella






def create_matrix(n,m,v,header=False):
    ret = []
    for i in range(n):
        row = [v] * m
        ret.append(row)
    if header:
        ret[0]=header
    return ret


def create_zero_matrix(n,m,header=False):
    return create_matrix(n,m,0,header)





# scale value x from x range (starting range) to y range (desired range)
# it answers this question: given a range from x_min to x_max that x can have,
# how much is x in another range y_min, y_max? This gives us y
def get_scaled(x,x_range,y_range=(0,1), round_to=5):
    x_min, x_max = x_range
    y_min, y_max = y_range
    x_coeff = (x_max - x_min) / (y_max - y_min)
    y_diff = (x - x_min) / x_coeff
    y = y_min + y_diff
    return round(y, round_to)





def get_ref_scale_from_file(file_name):
    ret={}

    with open(file_name,'r') as file:
        # read the first line which is the header (column names)
        header=file.readline()
        # read every line (the values)
        lines=file.readlines()

        for line in lines:
            line_split=line.split(',')
            # if len(line_split)<4:
            #     break

            comp=line_split[0]
            min_val=float(line_split[1])
            max_val=float(line_split[2])

            ret[comp]={
                'min':min_val,
                'max':max_val
            }

    return ret



# Returns a list with all components to ignore = the column names not to analyze.
def get_components_ignore_from_file(file_name):
    ret=[]

    with open(file_name,'r') as file:
        lines=file.readlines()

        for line in lines:
            line_split=line.split(',')
            ret+=line_split

    return ret



def clean_column_labels(columns_str):
    return columns_str.strip().split(',')



# Tranforms a file with values into a matrix.
def load_data(file_name):
    ret=[]

    with open(file_name,'r') as file:
        columns_str=file.readline()
        columns_cleaned=clean_column_labels(columns_str)
        ret.append(columns_cleaned)

        lines=file.readlines()
        for line in lines:
            line_split=line.split(',')
            ret.append(line_split)

    return ret




def clean_data(M,components_ignore,target_range):
    # FILTER A: remove unwanted columns
    columns_indexes=[]

    # collect all columns indexes to be removed
    # lower case all other column names
    for i in range(len(M[0])):
        column=M[0][i]
        if column in components_ignore:
            columns_indexes.append(i)
        else:
            M[0][i]=M[0][i].lower()

    # sort every index column you need to remove in ascending order
    # so you are sure that the next index to remove the columns element at will always be forward
    columns_indexes.sort()
    # remove all elements at those column indexes
    # you use a sort of "index counter" because every time you remove a column in ascending order,
    # the next index column to remove will always be forward (because you've sorted the columns indexes list)
    # thus you need this index counter because every time you remove a column, the next index column will be at
    # its previous minus how many columns you've already removed
    # Example: I want to remove columns with indexes 1, 7 and 12
    # The first time I itearate on the column with index 1, since it's the first time, I need to remove 0,
    # thus the column index I need to remove is 1-0=1
    # After removing this column, the index column that was previously 7 is now 7-1=6,
    # thus I need to remove the column at index 6 (because I'm working on the same object in memory)
    # If I previously said I wanted to remove the column at index 12, since I already removed two columns,
    # I will now have to remove the column at index 12-2=10 and so on
    k=0
    for j in columns_indexes:
        for i in range(len(M)):
            del M[i][j-k]
        k+=1

    # FILTER B: cast all other columns values to float
    for row in M[1:]:
        for j in range(len(M[0])):
            # assumption - replacing empty strings with mid of target range
            if row[j].strip()=='':
                row[j]=(target_range[0]+target_range[1])/2
            # cast to float every value
            else:
                row[j]=float(row[j])




# Given a generic matrix, returns a new scaled matrix with the values of each column scaled
# according to the min and max values given in the reference scale.
def scale_matrix(M_input,ref_scale,target_range):
    # create a copy of the given matrix
    n_rows=len(M_input)
    n_cols=len(M_input[0])
    columns_lables=M_input[0]
    M_c=create_zero_matrix(n_rows,n_cols,columns_lables)

    # for each column, find the min and max based linked to that column name
    # iterate for each column
    for j in range(len(M_input[0])):
        # the specific column name
        col_name = columns_lables[j]
        # min and max values for that column
        min_val=ref_scale[col_name]['min']
        max_val=ref_scale[col_name]['max']

        # iterate for each element of each column except the first row
        for i in range(1, len(M_input)):
            # set each column element to be its scaled
            scaled_val=get_scaled(M_input[i][j], (min_val, max_val), target_range, 3)
            M_c[i][j]=scaled_val

    return M_c




def save_output_matrix_to_file(output_matrix,file_name):
    with open(file_name,'w') as file:
        for row in output_matrix:
            # convert all elements to strings
            line_list_str=map(lambda x: str(x),row)
            line_str=','.join(list(line_list_str))
            file.write(line_str)
            file.write('\n')





def main():
    # CUSTOMIZE HERE
    # in what new range do I want the new values scaled in?
    min_range=float(input('Insert min range:'))
    max_range=float(input('Insert max range:'))
    target_range=(min_range,max_range)
    # what's the file name that contains the reference scale?
    ref_scale_file_name='ref_scale.csv'
    # what's the file name that contains the column names to be ignored?
    components_ignore_file_name= 'components_ignore.csv'
    # what's the name of the file that contains the input data to work with?
    file_name_without_ext=input('Insert the file name you want to analyze (without .csv):')
    data_input_file_name= file_name_without_ext+'.csv'
    # how do you want the new file with output values to be called?
    data_output_file_name= file_name_without_ext+'_output.csv'
    # this dictionary is the reference scale {component: min,max,measure}
    ref_scale=get_ref_scale_from_file(ref_scale_file_name)
    # this is the list of column names to be ignored (they must not be analyzed)
    components_ignore=get_components_ignore_from_file(components_ignore_file_name)
    # # this is the matrix (list of lists) with values to analyze
    data_input_matrix=load_data(data_input_file_name)
    # modify the original input matrix to get exactly the matrix you want to work with
    clean_data(data_input_matrix,components_ignore,target_range)
    # scaled matrix with target range, for example (0,1)
    data_output_matrix=scale_matrix(data_input_matrix,ref_scale,target_range)
    # # save scaled matrix to a new file
    save_output_matrix_to_file(data_output_matrix,data_output_file_name)

    print('Done.')

main()
