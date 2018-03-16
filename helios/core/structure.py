"""Base data structures for the SDK."""


class ContentCollection(object):
    """
    Abstract base class for feature/data results, i.e. content.

    This is a general purpose iterable for content data from the SDK.
    Specific functionality will be defined in child classes.

    Content is a general term for return data from the various API calls
    implemented within the SDK.  For example, index queries return
    GeoJSON feature collections.  Therefore, content will be a list of
    all the returned features within the GeoJSON feature collection.

    Attributes:
        content (sequence): Content that will be the elements in the iterator.
        raw_data (sequence): Raw data for debugging.

    """

    def __init__(self, content, raw_data=None):
        self._content = content
        self._raw = raw_data

    def __delitem__(self, index):
        del self._content[index]

    def __getitem__(self, item):
        return self._content[item]

    def __iter__(self):
        self._idx = 0
        return self

    def __len__(self):
        return len(self._content)

    def __next__(self):
        if self._idx >= self.__len__():
            self._idx = 0
            raise StopIteration
        temp = self.__getitem__(self._idx)
        self._idx += 1
        return temp

    next = __next__  # For Python 2


class RecordCollection(ContentCollection):
    """
    Abstract base class for batch jobs dealing with Records.

    This class is a variation of the FeatureCollection class to work with
    Records. The content attribute will be extracted from each record.  Usage
    is the same as a ContentCollection, but the _raw attribute will give access
    to the underlying Records.

    Attributes:
        content (sequence): Content that will be the elements in the iterator.
        records (sequence of Records): Raw record data for debugging purposes.

    """

    def __init__(self, content, records):
        super(RecordCollection, self).__init__(content, raw_data=records)

    @property
    def failed(self):
        """Records for queries that failed."""
        return [x for x in self._raw if not x.ok]

    @property
    def succeeded(self):
        """Records for queries that succeeded."""
        return [x for x in self._raw if x.ok]

    @property
    def _message(self):
        """
        Messages that were passed to the worker.

        Messages include all the input parameters.

        """
        return [x.message for x in self._raw if x.ok]

    @property
    def _query(self):
        """API query strings that occurred."""
        return [x.query for x in self._raw if x.ok]


class Record(object):
    """
    Record class for general use.

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
