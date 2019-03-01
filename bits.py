FILL = "fill"
LIT = "literal"
NSA_MODE = True


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

        # data tracking
        # these are used and reset for each sorted/word size
        self.literals = 0
        self.fills = 0
        self.fills_one = 0
        self.fills_zero = 0


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
   
    # acts like a main function
    def go(self):

        # read in data and build initial bitmaps
        self.intake()

        # write uncompressed bitmaps to file
        self.writeFile("animals_bitmap.txt", self.unsorted_bitmap)
        self.writeFile("animals_bitmap_sorted.txt", self.sorted_bitmap)

        # create 32-bit compressed bitmaps  
        # unsorted up first
        c32 = self.compress(self.unsorted_bitmap, 32)
        self.writeFile("animals_compressed_32.txt", c32)
        self.writeMetadata("animals_compressed_32")

        # now sorted
        c32_sorted = self.compress(self.sorted_bitmap, 32)
        self.writeFile("animals_compressed_sorted_32.txt", c32_sorted)
        self.writeMetadata("animals_compressed_sorted_32")

        ### Onto 64-bit words
        c64 = self.compress(self.unsorted_bitmap, 64)
        self.writeFile("animals_compressed_64.txt", c64)
        self.writeMetadata("animals_compressed_64")

        c64_sorted = self.compress(self.sorted_bitmap, 64)
        self.writeFile("animals_compressed_sorted_64.txt", c64_sorted)
        self.writeMetadata("animals_compressed_sorted_64")
            

    # creates and returns the compressed version of the given bitmap 
    def compress(self, bitmap, word_size):

        compressed_columns = [] 
        # turn  columns into strings and compress 
        for i in range(len(bitmap[0])):
            # first get the column
            column = ''.join([bitmap[j][i] for j in range(len(bitmap))])
            # then compress and save for later
            compressed_columns.append(self.compress_column(column, word_size)) 
        
        return compressed_columns

    # writes bitmap to specified file
    # bitmap here is a list of bit strings 
    def writeFile(self, path, bitmap):

        with open(path, "w+") as new_file:
            for line in bitmap:
                new_file.write(line)
                new_file.write("\n")

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


    # write the metadata to the designated file
    # then reset the metadata variables
    def writeMetadata(self, title):

        # if metadata collection isn't turn off, turn back
        if not NSA_MODE:
            return

        with open("meta_data.txt", "a+") as meta_file:
            meta_file.write(title + "\n")
            meta_file.write("\tfills:{}\n\t\tof 1:{}\n\t\tof 0:{}\n\tliterals:{}\n"
                            .format(self.fills, self.fills_one, self.fills_zero, self.literals))
        self.fills = 0
        self.fills_one = 0
        self.fills_zero = 0
        self.literals = 0 


    # create a WAH encoded string of the given column
    def compress_column(self, column_string, word_size):
        """
            column_string: a string representing the bits of
                           an attribute column            
            word_size: as it sounds, e.g. 32 for 32-bit 

        """

        # initialize loop variables
        run_of = None       # of 0's or 1's? Will be None if not currently counting runs
        run_count = 0       # how many runs so far?

        # variables to help us recognize when a run occurs
        run_string_zero = "0" * (word_size - 1)
        run_string_one = "1" * (word_size - 1)
        
        compressed_string = '' # constructed piecemeal by the below logic

        # loop while there are enough bits remaining
        # to require a full word encoding
        while len(column_string) >= word_size - 1: 
             
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
                        # adjust fill/literal tracking variables
                        self.updateMetadata(FILL, run_count, run_of)

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
                    self.updateMetadata(FILL, run_count, run_of)
                
                # then zero out the run trackers
                run_of = None
                run_count = 0
                # add the literal
                compressed_string += "0" + candidate_word[:word_size-1] 
                # and excise compressed bits from the bit string
                column_string = column_string[word_size-1:]  # WAH literals hold word_size-1 bits
                self.updateMetadata(LIT, 1)

        ### The column string is nearly or completely exhausted 
        ### do some final housekeeping and return 

        # write any runs that were accumulating                   
        if run_of is not None:
            compressed_string += BitMapper._runs(run_of, run_count, word_size)
            self.updateMetadata(FILL, run_count, run_of)

        # check for a final literal that would need padding
        if column_string:
            last_string = "0" + column_string 
            compressed_string += last_string
            self.updateMetadata(LIT, 1)

        return compressed_string
   
    def updateMetadata(self, kind, count, run_of=None):
        
        # fill update logic
        if kind == FILL:
            assert(run_of is not None)
            self.fills += count
            if run_of == "1":
                self.fills_one += count
            elif run_of == "0":
                self.fills_zero += count
        # literal update
        elif kind == LIT:
            self.literals += count

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
                print("Got a run count that doesn't fit in a single word!")
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

    # creates a bitmap byte for a given row of file data
    def _bitString(self, col_dict):
        """
            col_dict: A dictionary whose keys reflect the values of the 
                      three attribute columns in the file. 

            Each column value is checked agains the dictionary, where
            the column's presence results in a 1 bit and its absence a 0
        """

        return ''.join(["1" if bucket in col_dict else "0" for bucket in BitMapper.buckets])



if __name__ == "__main__":
    me = BitMapper("animals_test.txt") 
    me.go()

