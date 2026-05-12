CREATE TABLE document_record (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL CHECK (length(title) > 0),
    created_at TEXT NOT NULL
);

CREATE TABLE document_record_tag (
    document_id TEXT NOT NULL,
    tag TEXT NOT NULL CHECK (length(tag) > 0),
    FOREIGN KEY(document_id) REFERENCES document_record(id)
);