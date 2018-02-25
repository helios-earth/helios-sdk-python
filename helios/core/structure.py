"""Base data structures for the SDK."""
import abc

import six


@six.add_metaclass(abc.ABCMeta)
class ContentCollection(object):
    """
    Abstract base class for feature/data results, i.e. content.

    This is a general purpose iterable for content data from the SDK.
    Specific functionality will be defined in child classes.

    Content is a general term for return data from the various API calls
    implemented within the SDK.  For example, index queries return
    GeoJSON feature collections.  Therefore, content will be a list of
    all the returned features within the GeoJSON feature collection.

    """

    def __init__(self, data):
        self._raw = data
        self._build()

    @abc.abstractmethod
    def _build(self):
        """
        Combine content/data into a list.

        _build must be implemented in children.

        For example, all GeoJSON 'feature' sections can be merged and for
        Collections index results, 'results' can be merged.  The 'features'
        and 'results' data are the important content that will be iterated
        over.  Customized access to this data can be defined in child classes.

        """
        self.content = []
        for _ in self._raw:
            self.content.append([])

    def __delitem__(self, index):
        del self.content[index]

    def __getitem__(self, item):
        return self.content[item]

    def __iter__(self):
        self._idx = 0
        return self

    def __len__(self):
        return len(self.content)

    def __next__(self):
        if self._idx >= self.__len__():
            self._idx = 0
            raise StopIteration
        temp = self.__getitem__(self._idx)
        self._idx += 1
        return temp

    next = __next__  # For Python 2


@six.add_metaclass(abc.ABCMeta)
class RecordCollection(ContentCollection):
    """
    Abstract base class for batch jobs dealing with Records.

    This class is a variation of the FeatureCollection class to work with
    Records. The content attribute will be extracted from each record.  Usage
    is the same as a ContentCollection, but the _raw attribute will give access
    to the underlying Records.

    All Record instances contain a 'content' attribute.  This attribute will
    be combined in _build.

    """

    def __init__(self, records):
        super(RecordCollection, self).__init__(records)

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
