"""Base data structures for the SDK."""


class RecordCollection(object):
    """
    Class for handling query records.
    Attributes:
        records (list of :class:`Record <helios.core.structure.Record>`):
            Raw record data for debugging purposes.
    """

    def __init__(self, records=None):
        self._records = records or []

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
        url (str): API URL.
        content: Returned content. To be defined by method.
        error (exception): Exception that occurred, if any.

    """

    def __init__(self, url=None, content=None, error=None):
        self.url = url
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
        url (str): API URL.
        content (PIL.Image.Image): Image data.
        error (exception): Exception that occurred, if any.
        name (str): Name of image.
        output_file (str): Full path to image file that was written.

    """

    def __init__(
        self, url=None, content=None, error=None, name=None, output_file=None
    ):
        super(ImageRecord, self).__init__(url=url, content=content, error=error)
        self.name = name
        self.output_file = output_file


class ImageCollection(object):
    """
    Stores all image content and associated metadata.

    Args:
        image_records (list of :class:`Record <helios.core.structure.ImageRecord>`

    """

    def __init__(self, image_records):
        self.image_records = image_records

    @property
    def output_files(self):
        """Full paths to all saved images."""
        return [x.output_file for x in self.image_records]

    @property
    def image_names(self):
        """Names of all images."""
        return [x.name for x in self.image_records]

    @property
    def images(self):
        """PIL images."""
        return [x.content for x in self.image_records]
