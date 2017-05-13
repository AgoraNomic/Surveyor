import agora.datetime as adt
import email
import os
import os.path as path

class EmailDocument(object):
    """
    A Document representing an email file on disk. The metadata is
    drawn from the MIME headers of the email.
    """
    @classmethod
    def parse(cls, path):
        with open(path, 'r') as file:
            message = email.message_from_file(file)
        return cls(path, message)

    def __init__(self, path, message):
        self.path = path
        self.message = message

    @property
    def id(self):
        message_id = self.message['Message-ID']
        if message_id.startswith('<'):
            message_id = message_id[1:]
        if message_id.endswith('>'):
            message_id = message_id[:-1]
        return message_id

    @property
    def summary(self):
        return self.message['Subject']

    @property
    @adt.utc
    def timestamp(self):
        message_date = self.message['Date']
        return email.utils.parsedate_to_datetime(message_date)

    @property
    def canonical_path(self):
        dirname = path.dirname(self.path)
        filename = '{0.id}.eml'.format(self)
        return path.join(dirname, filename)

    def file_canonically(self):
        """
        Move the underlying file to its canonical path, if that path is
        empty and if the document is not already at its canonical path.

        Returns a new Document representing the canonicalized location.
        The receiver may no longer represent a file on disk after
        calling this method.
        """
        original = self.path
        canonical = self.canonical_path
        if original != canonical:
            # Avoid overwriting existing files that have the canonical name
            with open(canonical, 'x'):
                # If we created it successfully, we own it now. Rename the original over it.
                try:
                    os.rename(original, canonical)
                except FileNotFoundError:
                    # No original! Un-create the temporary file we created.
                    os.unlink(canonical)
                    raise
        return type(self)(canonical, self.message)

parsers = {
    '.eml': EmailDocument.parse,
}

class UnknownDocumentType(Exception):
    pass

def parse_document(path):
    """
    Parse the file or directory tree at path, and construct (if
    possible) a Document from it. The type of document will be
    determined by looking at the suffix of the filename.
    """
    for suffix, parser in parsers.items():
        if path.endswith(suffix):
            return parser(path)
    raise UnknownDocumentType
