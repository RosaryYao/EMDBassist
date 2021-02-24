class TableBase:
    """Read data from the given table file"""

    def __init__(self, fn, args):
        self.fn = fn
        self._args = args
        self.col_data = list()
        self.cols, self.rows, self.col_data = self._get_data()

    def _get_data(self):
        raise NotImplementedError
