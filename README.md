# Bitmap Compression

Converts a CSV "animals.txt" into a bitmap in order to evaluate the effectiveness of different compression techniques,
including 32-bit and 64-bit WAH encoding. "writeup.txt" offers commentary on their performance.
<br>

Setting the NSA_MODE bit adds an extra output file "meta_data.txt" provides additional insight into
how the different approaches are transforming the data.


<br>
The following 6 files are created in the working directory:
<br>

    Uncompressed
    "animals_bitmap.txt" The 1:1 bitmap translation of the original data 
    "animals_bitmap_sorted" 1:1 bitmap translation, but sorted lexicographically

    Compressed
    "animals_compressed_32.txt" 32-bit WAH encoded version of unsorted bitmap
    "animals_compressed_64.txt" 64-bit WAH encoded version of the unsorted bitmap
    "animals_compressed_sorted_32.txt" 32-bit WAH encoded version of the sorted bitmap
    "animals_compressed_sorted_64.txt" 64-bit WAH encoded version of the sorted bitmap


The compression algorithms can be repurposed by: 
<br>

    - Updating the "buckets" list to reflect the possible values of the new data
    - Updating the createBitmap function to specify the bit mapping of the new data
    - Updating BitMapper's init param with the file path to the new data