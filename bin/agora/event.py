import collections as c
import agora.datetime as adt
import agora.yaml as yaml
import os.path

class Event(object):
    """
    An Event is a chronological entry in an event collection (a
    directory) placing a specific Document in that collection.
    """

    @classmethod
    def from_document(cls, collection, document, timestamp=None):
        """
        Create an in-memory Event from a Document. If the passed
        timestamp is None, the event's timestamp will be derived from
        the Document's; otherwise, it will be normalized and used as-is.
        """
        if timestamp is None:
            timestamp = document.timestamp

        metadata = cls.document_metadata(document)

        return cls(collection, document.path, timestamp, metadata)

    @classmethod
    def document_metadata(cls, document):
        return c.OrderedDict(
            event=dict(
                summary=document.summary,
            ),
            diff=dict(
                field='new value',
            ),
        )

    def __init__(self, collection, document, timestamp, metadata):
        self.collection = collection
        self.document = document
        self._timestamp = timestamp
        self.metadata = metadata

    @property
    @adt.naive
    def timestamp(self):
        return self._timestamp

    @property
    def id(self):
        return self.timestamp.isoformat('-', 'seconds')

    @property
    def path(self):
        return os.path.join(self.collection, self.id)

    @property
    def document_path(self):
        return os.path.join(self.path, 'document')

    @property
    def metadata_path(self):
        return os.path.join(self.path, 'event.yaml')

    def create(self):
        """
        Create the on-disk representation of this event, if it doesn't
        already exist.
        """
        self._create_event_directory()
        self._create_document_link()
        self._create_event_metadata()


    def _create_event_directory(self):
        os.mkdir(self.path)

    def _create_document_link(self):
        document_target = os.path.relpath(self.document, self.path)
        os.symlink(document_target, self.document_path)

    def _create_event_metadata(self):
        with open(self.metadata_path, 'w') as meta:
            yaml.dump(self.metadata, meta)
