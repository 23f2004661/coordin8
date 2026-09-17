# Coordin8 Frontend Dashboard

Modern web dashboard and developer provenance inspector for the Coordin8 knowledge and retrieval system.

Conforms to Section 26 of `ProjectDetails.md`.

---

## Features

- **Executive Dashboard**: High-level metrics for indexed documents, chunks, vector points, and evaluation metrics.
- **Document Management**: View registered canonical documents, format badges, and summaries.
- **Upload & Ingestion Pipeline**: Ingestion dropzone visualizing the 7 pipeline stages (`REGISTERED` &rarr; `EXTRACTING` &rarr; `NORMALIZED` &rarr; `ENRICHING` &rarr; `CHUNKED` &rarr; `INDEXING` &rarr; `READY`).
- **Grounded Search & Answer**: Multi-turn grounded Q&A with inline provenance citation pills.
- **Developer Provenance Inspector**: Debug view displaying `document -> section -> chunk`, retriever type, dense/sparse scores, after-fusion rank, reranker score, and source provenance.

---

## Running

Simply open `index.html` in any web browser, or run a local static server:

```powershell
python -m http.server 3000
```

Access at `http://localhost:3000`. When the backend is running at `http://localhost:8000`, the frontend automatically connects to the live API endpoints.
