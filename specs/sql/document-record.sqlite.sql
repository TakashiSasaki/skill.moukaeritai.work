CREATE TABLE document_record (
    id TEXT NOT NULL PRIMARY KEY CHECK (length(id) > 0),
    title TEXT NOT NULL CHECK (length(title) > 0),
    created_at TEXT NOT NULL
);

CREATE TABLE document_record_tag (
    document_id TEXT NOT NULL,
    tag TEXT NOT NULL CHECK (length(tag) > 0),
    PRIMARY KEY (document_id, tag),
    FOREIGN KEY(document_id) REFERENCES document_record(id)
);