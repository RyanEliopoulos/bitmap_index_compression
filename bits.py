# returns the appropriate age bucket
# for a given age
def ageBucket(age):

    i = 0
    while True:
        assert(i < 10) # sanity check
        if (i * 10) + 1 <= int(age) <= (i * 10) + 10:
            return i
        i += 1


# provides majority of the logic for processing the given
# files into the specified bitmaps
class BitMapper(object):
    
    buckets = ["cat", "dog", "turtle", "bird"                     # Animal Types
              , "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"  # Age buckets
              , "True", "False"]                                  # Adoption status


    def __init__(self, file_path):
        self.path = file_path
        self.sorted_bitmap = []   # This will be a list strings each representing 8 bits
        self.unsorted_bitmap = [] # This will be a list strings each representing 8 bits

    def intake(self):
        
        """
            This method reads each row from the filepath
            given during object creation and stores the data
            as a list of tuples, where each tuple is attribute
            data, and creates sorted and unsorted bitmaps
        """   

        # first turn each line into a 'tuple'
        # and create a list from the 'tuples'
        file_lines = [] 

        with open(self.path, "r") as data_file:
            lines = data_file.readlines()
            for line in lines:
                line_tuple = line.rstrip().split(",")
                file_lines.append(line_tuple)            

        # create the unordered bitmap     
        unsorted_bitmap = self.createBitmap(file_lines)
        self.unsorted_bitmap = unsorted_bitmap

        # create the ordered bitmap
        sorted_bitmap = self.createBitmap(sorted(file_lines))
        self.sorted_bitmap = sorted_bitmap
    
    # currently this is just testing the intake method is working correctly
    # i.e. sorted and unsorted bitmaps are good
    def writeFile(self):
        with open("RUSSIA_sorted.txt", "w+") as bitmap_file:
            for row in self.sorted_bitmap:
                bitmap_file.write(row)           
                bitmap_file.write("\n")

        with open("RUSSIA_unsorted.txt", "w+") as bitmap_file:
            for row in self.unsorted_bitmap:
                bitmap_file.write(row)
                bitmap_file.write("\n")

    # creates a bitmap from a list of line tuples
    def createBitmap(self, lines):
        """
            lines: a list of lists. Each element is a list of strings
                   where each string is an attribute value from the provided
                   database file. 

            A dictionary is populated with the strings acting as keys,
            then the dictionary is queried with each attribute column
            so and its presence of lack thereof informs the placement
            of the 0s and 1s 
        """    

        bit_string_list = []  # holds a character representation of a byte
        
        # create a 'byte' for each tuple of attribute information
        for line in lines: 
            temp_dict = {}

            # note this row's type and adoption
            for col in line[::2]:
                temp_dict[col] = 1

            # now bin the age value
            temp_dict[str(ageBucket(line[1]))] = "1"
           
            # then create a bitmap for the row
            # and append it to the running list
            bit_string_list.append(self._bitString(temp_dict))

        return bit_string_list


    # create a WAH encoded string of the bitmaps
    # utilizing the given word size
    # incomplete so far 
    @staticmethod
    def compress_columns(column_string, word_size):
        """
            bit_strings: A list of strings where each string is a character representation
                         of a byte value for a database tuple AKA a list of 8-bit bitmaps

        """
        # create a singular string of all the bits
        # by column!
        # combine columns into their own strings, then combine into a single string
        #bit_string = ''.join([bit_strings[i][j] for j in range(len(bit_strings[0])) for i in range(len(bit_strings))])
       
        # now process the string of bits 

        # initialize loop variables
        #run = False         # Currently tracking a chuck of runs?
        run_of = None       # of 0's or 1's? Will be None if not currently counting runs
        run_count = 0       # how many runs so far?

        # to recognize what a run is
        run_string_zero = "0" * (word_size - 1)
        run_string_one = "1" * (word_size - 1)
        
        compressed_string = '' # constructed piecemeal by the below logic

        # loop while there are enough bits remaining
        # to qualify as a run
        while len(column_string) >= word_size:
             
            # first check if there is a run
            candidate_word = column_string[:word_size-1]  
            if candidate_word in (run_string_zero, run_string_one): 

                # check if its a run already in progress or a new one                 
                if candidate_word[0] == run_of:
                    run_count += 1

                # or if its a run that's just beginning
                else:

                    # so check if this is concluding a previous set of runs 
                    # and adjust compressed_string appropriately
                    if run_of is not None:
                        compressed_string += BitMapper._runs(run_of, run_count, word_size)

                    # then track new run
                    run_of = candidate_word[0]
                    run_count = 1

                # adjust the uncompressed string to reflect 
                # what has just been processed
                column_string = column_string[word_size-1:]  

            # otherwise its a literal            
            else:
                # check if its concluding a set of runs
                if run_of is not None:
                    compressed_string += BitMapper._runs(run_of, run_count, word_size)

                # then zero out the run trackers
                run_of = None
                run_count = 0
                # add the literal
                compressed_string += "0" + candidate_word[:word_size-1] 
                # and excise compressed bits from the bit string
                column_string = column_string[word_size-1:]  # WAH literals hold word_size-1 bits

        # write any runs that were accumulating                   
        if run_of is not None:
            compressed_string += BitMapper._runs(run_of, run_count, word_size)

        # Now need the logic to append the final literal
        # and add any necessary padding
        #zero_pad = (word_size - 1) - len(column_string)
        last_string = "0" + column_string #+ "0" * zero_pad
        compressed_string += last_string

        return compressed_string
    
    # untested
    @staticmethod
    def _runs(run_of, run_count, word_size):

        """
            calculates the proper string encoding for a WAH
            compressed run with the given values
        """
        
        # prepare in case run_count exceeds capacity of (word_size - 1) bits 
        compressed_strings = []  

        while True:
            
            # check if run_count exceeds the capacity for a single byte to track it
            if run_count > (2 ** (word_size - 2)) - 1: 

                # build max run word
                temp_string = "1" + run_of + "1" * (word_size - 2)
                compressed_strings.append(temp_string)

                # and adjust run_count
                run_count -= (2 ** (word_size - 2)) - 1
            
            # run_count will fit in a single run word
            else:

                # get bit representation of the number of runs
                run_count_bits = format(run_count, "b")
            
                # figure out how many zeros need to preced those
                zero_pad = (word_size - 2) - len(run_count_bits)

                # then build the string
                temp_string = "1" + run_of + "0" * zero_pad + run_count_bits
                compressed_strings.append(temp_string)                

                # and break because we all runs have been encoded
                break

        # return a single string of the compressed data
        return ''.join(compressed_strings)

    @staticmethod
    def columns_to_row(bit_strings):
        bit_string = ''.join([bit_strings[i][j] for j in range(len(bit_strings[0])) for i in range(len(bit_strings))])
        return bit_string
        #print(bit_string)

    # creates a bitmap byte for a given row of file data
    def _bitString(self, col_dict):
        """
            col_dict: A dictionary whose keys reflect the values of the 
                      three attribute columns in the file. 

            Each column value is checked agains the dictionary, where
            the column's presence results in a 1 bit and its absence a 0
        """

        return ''.join(["1" if bucket in col_dict else "0" for bucket in BitMapper.buckets])


me = BitMapper("animals_test.txt") 
me.intake()


# we want a single column
#for i in range(len(me.sorted_bitmap)):
bitmap = me.sorted_bitmap

columns = []

for i in range(len(bitmap[0])):
    column = ''.join([bitmap[i]
column = ''.join([bitmap[i][1:2] for i in range(len(bitmap))])
#print(len(column))
compressed_column = me.compress_columns(column, 32)
print(compressed_column)



#me.writeFile()

#ret = me._runs("1", 15, 5)
#print(ret)
#print(len(ret.compress))

# testing the columns to row technique  seems to check out
#bit_string = me.columns_to_row(me.sorted_bitmap)
#print(bit_string)


"""
with open("animals_test_bitmap_sorted.txt", "r") as test_file:
    lines = test_file.readlines()
    line_tuples = []
    for line in lines:
        line_tuples.append(line.rstrip())
        
    print(BitMapper.columns_to_row(line_tuples))
 """  


# testing the compression algorithm now
"""
compressed = me.compress(me.sorted_bitmap, 32)
i = 0
for char in compressed:
    print(char, end="")
    i += 1
    if i == 169:
        print()
        i = 0
"""
