
# animal type, age buckets 1-10, 11-20, .. , and adoption status



buckets = ["cat", "dog", "turtle", "bird"  # Animal Types
            , "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"  # Age buckets
            , "True", "False"]  # Adoption status



line_dicts = []

#def bitString(data_tuple):

    #char_list = ["1" for 


# returns the age bin corresponding to age
def ageBucket(age):

    i = 0
    while True:
        if (i * 10) + 1 <= int(age) <= (i * 10) + 10:
            return i
        i += 1


# takes a dict filled with line items
# and creates the bitmap
def bitString(col_dict):


    pieces = ["1" if bucket in col_dict else "0" for bucket in buckets] 
    return ''.join(pieces)

bit_strings = []
with open("./animals_test.txt") as test_file: 
    lines = test_file.readlines()
    for line in lines:
        # Create default dictionary
        temp_dict = {}

        line_tuple = line.rstrip().split(",") 

        # note the type and adoption status
        for col in line_tuple[::2]:
            temp_dict[col] = 1
       
        # bin the age values 
        temp_dict[str(ageBucket(line_tuple[1]))] = "1"

        bit_string = bitString(temp_dict)
        bit_strings.append(bit_string) 

with open("test_bitmap.txt", "w+") as bit_file:
    for string in bit_strings:
        bit_file.write(string)
        bit_file.write("\n")
