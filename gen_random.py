import numpy as np

def gen_random_array(rows, columns, filename, verbose=False):
    with open(filename, "w+") as outputfile:
        for i in range(rows):
            if i%1000 == 0 and verbose is True:
                print i

            data = np.random.rand(columns)
            row = " ".join(map(str, data))
            outputfile.write(row + "\n")
