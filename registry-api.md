# TODO

* Events
* Properties
* Document filtering.

# Use cases

* Users must be able to submit new documents.
* Users must be able to revise existing documents, without losing prior revisions.
* Users must be able to list documents.
* Users must be able to list the revisions of a document.
* Users must be able to review the text of any revision of a document.

# The Agoran Deed Registry Service

A deed is a public message that has an effect on the game of Agora as a result of its publication, as defined by the Rules of Agora at the time of its publication.

This service provides a registry for deeds, allowing users to store and retrieve registered deeds.

## Documents & Revisions

An deed is a message from a public forum, or any other documentary evidence relevant to participants in Agora. An original deed may be filed with this service, becoming a filed deed.

A filed deed has at least one revision. When a new deed is filed with this registry service, the original deed becomes the first revision of the filed deed. New original deeds may be filed to revise an existing deed, to allow for correction of a deed filed improperly or incompletely. Once registered, deeds generally may not be removed from the registry.

Deeds are identified based on a document ID. As most deeds arrive by email, the document ID is generally the Message-ID of the original deed. It is not possible to revise a deed such that its document ID would change. This results in a new document, instead.

Deeds are arranged chronologically based on their date of publication. As most deeds arrive by email, the Date header of the email is generally the publication date of the submitted deed. Filing a revision that modifies the publication date will reorder this deed with respect to other deeds.

Documents other than public forum messages may be filed, but this is not recommended. Registry storage is not infinite, and in any case cluttering up the registry with casual chatter is not useful. Use discretion when filing discussion messages or out-of-list messages with this registry service.

* `POST /document`: file a new document or revision.

    The body of this request is the full content of the document (generally, an email blob). The document's ID, publication date, and other metadata will be extracted from the document.

    If no document exists with the extracted ID, then this will create a new document. The body of the request will be the document's initial revision. Otherwise, if a document exists with the extracted ID, the posted body will supercede the current revision unless it is identical to the current revision. If the posted body is identical to the current revision, the document is not modified.

    Will return:

    * 201 Created: New document, or new revision of existing document.
    * 200 Ok: Existing revision of existing document.
    * 400 Bad Request: Not a document we can file.
    * 401 Unauthorized: Bad credentials.
    * 403 Forbidden: No permission to file document or revision.

    Successful responses return a JSON object:

        {
            "document_url": "/document/URL-ENCODED-ID",
            "revision_url": "/document/URL-ENCODED-ID/REVISION-ID",
            "download_url": "/document/URL-ENCODED-ID/REVISION-ID/download"
        }

    Successful responses also include a `Location` header with the same information as the `document_url` property.

* `GET /document`: return a list of filed documents

    Will return:

    * 200 Ok: A list of filed documents, which may be empty.

    Sucessful responses return a JSON object:

        {
            "documents": [
                {
                    "url": "/document/URL-ENCODED-ID",
                    "download_url": "/document/URL-ENCODED-ID/REVISION-ID/download",
                    "document": "DOCUMENT-ID",
                    "revision": "REVISION_ID",
                    "publication_date": "2017-01-02T01:02:03Z",
                    "filing_date": "2017-01-02T01:02:03Z",
                    "filed_by": "o"
                }
            ]
        }

    Documents in the list are sorted chronologically, with the oldest documents first.

* `GET /document/DOCUMENT`: return metadata about a document

    Will return:

    * 200 Ok: Document found.
    * 404 Not Found: Document not found.

    Successful responses return a JSON object:

        {
            "download_url": "/document/URL-ENCODED-ID/REVISION-ID/download",
            "document": "DOCUMENT-ID",
            "revision": "REVISION_ID",
            "publication_date": "2017-01-02T01:02:03Z",
            "filing_date": "2017-01-02T01:02:03Z",
            "filed_by": "o",
            "revisions": [
                {
                    "url": "/document/URL-ENCODED-ID/REVISION-ID",
                    "download_url": "/document/URL-ENCODED-ID/REVISION-ID/download",
                    "revision": "REVISION_ID"
                    "publication_date": "2017-01-02T01:02:03Z",
                    "filing_date": "2017-01-02T01:02:03Z",
                    "filed_by": "o"
                }
            ]
        }

    The properties of the latest revision are embedded in the document itself.

* `GET /document/DOCUMENT/REVISION`: return metadata about a revision

    Will return:

    * 200 Ok: Document & revision exist.
    * 404 Not Found: Document or revision does not exist.

    Successful responses return a JSON object:

        {
            "download_url": "/document/URL-ENCODED-ID/REVISION-ID/download",
            "document": "DOCUMENT-ID",
            "revision": "REVISION-ID",
            "publication_date": "2017-01-02T01:02:03Z",
            "filing_date": "2017-01-02T01:02:03Z",
            "filed_by": "o"
        }

* `GET /document/DOCUMENT/REVISION/download`: download the raw document blob.

    Will return:

    * 200 Ok: Document & revision exist.
    * 404 Not Found: Document or revision does not exist.

    Successful responses will include the document blob, exactly as uploaded.
