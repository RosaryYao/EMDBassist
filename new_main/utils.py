import base64
import struct


class Read_table:
    """Read data from the given table file"""

    def __init__(self, fn):
        self.fn = fn
        self.cols, self.rows, self.col_data = self._get_data()
        # called self.col_data because this class extracts each row
        # from the file as an element and store them in a list

    def _get_data(self):
        """
        with open(fn, "r") as f:
            row_data = f.readlines()
            if fn.endswith(".em"):  # dealing with Briggs' motl table
                col_data = [row.strip().split(",") for row in row_data]
            if fn.endswith(".tbl"):
                col_data = [row.strip().split(" ") for row in row_data]
            try:
                length_row = [len(row) for row in col_data]
                assert sum(length_row) / len(length_row) == length_row[0]
            except AssertionError:
                raise ValueError("Number of columns are not equal on all rows!")
        return len(col_data[0]), len(row_data), col_data
        """

        # global col_data # todo: look at the result between global and local
        if self.fn.endswith(".em"):  # Briggs' motl table format
            print("Reading Briggs' motl table file...")
            with open(self.fn, "rb") as motl:
                header = struct.unpack("128i", motl.read(128 * 4))
                raw_data = motl.read()
                length = len(raw_data) / 4
                raw_values = struct.unpack("%df" % length, raw_data)
                # mode = int(hex(header[0])[2])

            col_data = []
            for i, each in enumerate(raw_values[0:len(raw_values):20]):
                flag = 20 * i
                row = []
                for value in raw_values[flag:(flag + 20)]:
                    row.append(value)
                col_data.append(row)

        elif self.fn.endswith(".tbl"):  # Dynamo table format
            print("Reading Dynamo table file...")
            with open(self.fn, "r") as f:
                row_data = f.readlines()
            col_data = [row.strip().split(" ") for row in row_data]

        elif self.fn.endswith(".mod"):  # Peet table format
            pass  # todo: run peet STA

        try:
            length_row = [len(row) for row in col_data]
            assert sum(length_row) / len(length_row) == length_row[0]
        except AssertionError:
            raise ValueError("Number of columns are not equal on all rows!")

        return len(col_data[0]), len(col_data), col_data

    def __getitem__(self, index):
        return self.col_data[index]
