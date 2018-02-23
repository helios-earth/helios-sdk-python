"""Base data structures for the SDK."""
import abc

import six


@six.add_metaclass(abc.ABCMeta)
class FeatureCollection(object):
    """
    Abstract base class for feature/data results.

    Features can be from GeoJSON feature collections or generic feature
    results.

    """

    def __init__(self, data):
        self._raw = data
        self._build()

    @abc.abstractmethod
    def _build(self):
        """
        Combine data into a list.

        _build must be implemented in children.

        For GeoJSON all 'feature' sections will be merged and for Collections
        index results, 'results' will be merged.

        """
        self.features = []
        for _ in self._raw:
            self.features.append([])

    def __delitem__(self, index):
        del self.features[index]

    def __getitem__(self, item):
        return self.features[item]

    def __iter__(self):
        self._idx = 0
        return self

    def __len__(self):
        return len(self.features)

    def __next__(self):
        if self._idx >= self.__len__():
            self._idx = 0
            raise StopIteration
        temp = self.features[self._idx]
        self._idx += 1
        return temp

    next = __next__  # For Python 2


@six.add_metaclass(abc.ABCMeta)
class RecordCollection(object):
    """
    Abstract base class for batch jobs.

    This class is a variation of the FeatureCollection class to work with
    Records.

    """

    def __init__(self, records):
        self.raw_records = records
        self.failed = [x for x in records if not x.ok]
        self.succeeded = [x for x in records if x.ok]
        self.content = [x.content for x in records if x.ok]

    @property
    def message(self):
        return [x.message for x in self.raw_records if x.ok]

    @property
    def query(self):
        return [x.query for x in self.raw_records if x.ok]

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
        temp = self.__getitem__[self._idx]
        self._idx += 1
        return temp

    next = __next__  # For Python 2


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
