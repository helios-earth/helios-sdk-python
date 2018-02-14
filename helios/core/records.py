"""This module holds the container classes used by the SDK."""


class Record(object):
    """
    Base Record Class

    This class can be used instantiated or as a base for expanded containers.
    The purpose is to record various data when working with the SDK and to
    better handle exceptions in batch jobs.

    Attributes:
        query (str): The API query that occurred.
        data: The data that was fetched.
        error (exception): Exception that occurred.
        ok (bool): Returns True if the query was successful and False
            otherwise.

    """

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
    Container for queries involving images.

    Attributes:
        query (str): The API query that occurred.
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
    """Container for preview queries."""


class ShowImageRecord(ImageRecord):
    """Container for show_image queries."""
