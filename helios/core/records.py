"""Record classes used by the SDK."""


class Record(object):
    """Base Record Class"""

    def __init__(self, query=None, data=None, error=None):
        self.query = query
        self.data = data
        self.error = error

    @property
    def ok(self):
        if self.error:
            return False
        else:
            return True


class ImageRecord(Record):
    """
    Base Record for media queries.

    Args:
        query (str): The API query.
        data (numpy.ndarray): Image data.
        error (exception): Exception that occurred.
        name (str): Image name.
        output_file (str): Full path to output file.
        ok (bool): Returns True if no errors occurred and False
            otherwise.

    """

    def __init__(self, query=None, data=None, error=None, name=None, output_file=None):
        super(ImageRecord, self).__init__(query=query, data=data, error=error)
        self.name = name
        self.output_file = output_file


class PreviewRecord(ImageRecord):
    """Record for preview queries."""


class ShowImageRecord(ImageRecord):
    """Record for show_image queries."""


class ShowRecord(Record):
    """
    Record for show queries.

    Args:
        query (str): The API query that occurred.
        data (dict): Attribute data.
        error (exception): Exception that occurred.
        ok (bool): Returns True if the query was successful and False
            otherwise.

    """

    def __init__(self, query=None, data=None, error=None):
        super(ShowRecord, self).__init__(query=query, data=data, error=error)
