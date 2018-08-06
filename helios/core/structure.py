"""Base data structures for the SDK."""


class RecordCollection(object):
    """
    Class for handling query records.

    Attributes:
        records (list of :class:`Record <helios.core.structure.Record>`):
            Raw record data for debugging purposes.

    """

    def __init__(self, records):
        self._records = records

    @property
    def failed(self):
        """Records for queries that failed."""
        return [x for x in self._records if not x.ok]

    @property
    def succeeded(self):
        """Records for queries that succeeded."""
        return [x for x in self._records if x.ok]


class Record(object):
    """
    Individual query record.

    Args:
        message (tuple): Original message. This will be a namedtuple containing
            all the inputs for an individual call within a batch job.
        query (str): API query.
        content: Returned content. To be defined by method.
        error (exception): Exception that occurred, if any.

    """

    def __init__(self, message=None, query=None, content=None, error=None):
        self.message = message
        self.query = query
        self.content = content
        self.error = error

    @property
    def ok(self):
        """
        Check if failure occurred.

        Returns:
            bool: False if error occurred, and True otherwise.

        """
        if self.error:
            return False
        return True


class ImageRecord(Record):
    """
    Record class for images.

    Args:
        message (tuple): Original message. This will be a namedtuple containing
            all the inputs for an individual call within a batch job.
        query (str): API query.
        content (numpy.ndarray): Image as a Numpy ndarray.
        error (exception): Exception that occurred, if any.
        name (str): Name of image.
        output_file (str): Full path to image file that was written.

    """

    def __init__(self, message=None, query=None, content=None, error=None,
                 name=None, output_file=None):
        super(ImageRecord, self).__init__(message=message, query=query,
                                          content=content, error=error)
        self.name = name
        self.output_file = output_file


class ImageCollection(RecordCollection):
    """Stores all image content and associated metadata."""

    def __init__(self, content, records):
        super(ImageCollection, self).__init__(records)
        self.content = content

    @property
    def output_files(self):
        """Full paths to all saved images."""
        return [x.output_file for x in self._records if x.ok]

    @property
    def image_names(self):
        """Names of all images."""
        return [x.name for x in self._records if x.ok]
