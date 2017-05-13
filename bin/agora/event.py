import agora.datetime as adt
import agora.yaml as yaml
import collections as c
import datetime as dt
import os
import os.path
import sortedcontainers as sc

class Event(object):
    ID_FORMAT = '%Y-%m-%d-%H:%M:%S'

    """
    An Event is a chronological entry in an event collection (a
    directory) placing a specific Document in that collection.
    """

    @classmethod
    def from_filesystem(cls, collection, id):
        """
        Load an Event from a directory on disk.
        """
        entry_path = cls.path_for(collection, id)
        document = os.readlink(cls.document_path_for(entry_path))
        timestamp = dt.datetime.strptime(id, cls.ID_FORMAT)
        metadata = cls.read_metadata(cls.metadata_path_for(entry_path))

        return cls(collection, document, timestamp, metadata)

    @classmethod
    def read_metadata(cls, path):
        with open(path, 'r') as file:
            return yaml.load(file)

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
            diff=[
                c.OrderedDict(
                    op='replace',
                    path='/some/field',
                    value='new value',
                ),
            ],
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
        return self.timestamp.strftime(self.ID_FORMAT)

    @property
    def summary(self):
        return self.metadata['event']['summary']

    @classmethod
    def path_for(cls, collection, id):
        return os.path.join(collection, id)

    @property
    def path(self):
        return self.path_for(self.collection, self.id)

    @classmethod
    def document_path_for(cls, path):
        return os.path.join(path, 'document')

    @property
    def document_path(self):
        return self.document_path_for(self.path)

    @classmethod
    def metadata_path_for(cls, path):
        return os.path.join(path, 'event.yaml')

    @property
    def metadata_path(self):
        return self.metadata_path_for(self.path)

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

    def __repr__(self):
        return "Event(timestamp={0.timestamp})".format(self)

def load_collection(collection):
    """
    Given a collection directory, load every event in it and return
    them in a chronologically-sorted list.
    """
    def timestamp(event):
        return event.timestamp

    events = (Event.from_filesystem(collection, entry) for entry in os.listdir(collection))
    return sc.SortedListWithKey(events, key=timestamp)
