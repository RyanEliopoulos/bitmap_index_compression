# returns the appropriate age bucket
# for a given age
def ageBucket(age):

    i = 0
    while True:
        assert(i < 10) # sanity check
        if (i * 10) + 1 <= int(age) <= (i * 10) + 10:
            return i
        i += 1

def bitString(col_dict):
    
    return ''.join(["1" if bucket in col_dict else "0" for bucket in buckets])
        

class BitMapper(object):
    
    buckets = ["cat", "dog", "turtle", "bird"                     # Animal Types
              , "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"  # Age buckets
              , "True", "False"]                                  # Adoption status


    def __init__(self, file_path):
        self.path = file_path
        self.sorted_bitmap = []   # This will be a list strings each representing 8 bits
        self.unsorted_bitmap = [] # This will be a list strings each representing 8 bits

    def intake(self):
       
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
    def writeFile(self):
        with open("RUSSIA_sorted.txt", "w+") as bitmap_file:
            for row in self.sorted_bitmap:
                bitmap_file.write(row)           
                bitmap_file.write("\n")

        with open("RUSSIA_unsorted.txt", "w+") as bitmap_file:
            for row in self.unsorted_bitmap:
                bitmap_file.write(row)
                bitmap_file.write("\n")

    # creates a bitmap from a list of tuples
    def createBitmap(self, lines):
    
        bit_string_list = []
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

    # creates a bitmap byte for a given row 
    def _bitString(self, col_dict):
        return ''.join(["1" if bucket in col_dict else "0" for bucket in BitMapper.buckets])


me = BitMapper("animals_test.txt") 
me.intake()
me.writeFile()

