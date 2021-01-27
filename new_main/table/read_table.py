"""Read table into data. col_data is the one with all the info"""

class Data:
    """Read data from the given table file"""

    def __init__(self, fn):
        self.fn = fn
        self.cols, self.rows, self.col_data = self._get_data(fn)

    def _get_data(self, fn):
        with open(fn, "r") as f:
            row_data = f.readlines()
            if fn.endswith(".csv"):
                col_data = [row.strip().split(",") for row in row_data]
            if fn.endswith(".tbl"):
                col_data = [row.strip().split(" ") for row in row_data]
            try:
                length_row = [len(row) for row in col_data]
                assert sum(length_row) / len(length_row) == length_row[0]
            except AssertionError:
                raise ValueError("Number of columns are not equal on all rows!")
        return len(col_data[0]), len(row_data), col_data

    def __getitem__(self, index):
        return self.col_data[index]



