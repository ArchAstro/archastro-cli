---
name: manage-knowledge
description: Add, refresh, search, and maintain ArchAstro agent knowledge from files, websites, and connected providers; diagnose sources, ingestions, items, and document updates.
---

# Manage ArchAstro knowledge

Install or upgrade `archastro` if missing, and run `archastro auth login` if not authenticated.

## Choose the source and owner

The pipeline is connection → source → ingestion → searchable items/documents.
An agent installation attaches capabilities to an agent. Creating a source under
another owner does not demonstrate that the intended agent can retrieve it.

Identify the target agent, owner, and exact collection or URL to ingest. Inspect
existing installations and discover supported source kinds and payload requirements:

```bash
archastro list agentinstallations --agent <agent-id> --json
archastro list knowledgesourcekinds
archastro create knowledgesource --help
archastro create agentinstallationsource --help
```

Use the existing integration/installation for connected provider knowledge. Resolve
pending authorization first with `archastro help integrations`. Do not widen the
source scope or ingest unrelated material to compensate for missing results.

## Add knowledge to an installation

For an existing installation, use its supported source type and payload:

```bash
archastro create agentinstallationsource --installation <installation-id> --type <source-type> --payload '<type-specific-json>' --wait
```

This triggers ingestion. Inspect the returned result and record the source and
ingestion IDs. If a standalone source is required, use `create knowledgesource`
with the appropriate `--agent`, `--team`, `--user`, or system-owner `--org` scope.
Use current kind definitions instead of guessing the payload from a similar kind.

## Ingest and refresh

Read the ingestion contract; uploaded file IDs and local paths are different:

```bash
archastro ingest knowledgesource --help
```

1. For a `knowledge/documents` source, push local content:

   ```bash
   archastro ingest knowledgesource <source-id> --content @./document.md --wait
   ```

2. `--file` takes an already-uploaded `fil_...` ID, not a filesystem path.
   Use `archastro create file --help` when a separate file upload is needed.
3. For a supported pull source, refresh its configured data:

   ```bash
   archastro ingest knowledgesource <source-id> --pull --wait
   ```

Do not combine `--pull` with `--file` or `--content`. A wait that ends before success
is not evidence of ingestion completion; inspect the returned ingestion ID.

## Prove retrieval

```bash
archastro list knowledgeingestions --source <source-id> --json
archastro list knowledgeitems --source <source-id> --json
archastro search knowledgesource <source-id> --query '<specific fact in the source>'
archastro list knowledgedocuments --agent <agent-id> --json
```

Check ingestion status, the actual resulting records, and a representative search.
For failures use `archastro describe knowledgeingestion <ingestion-id>`; distinguish
authorization, ingestion, and retrieval failures before changing anything.
For a requested agent setup, verify its installation and agent-visible documents
as well as source search. A successful source search alone does not prove an agent
session can use that source; use a scoped session check when authorized.

## Maintain documents

```bash
archastro export knowledgedocument --help
archastro update knowledgedocument --help
archastro delete knowledgedocument --help
```

Export returns full text or a bounded slice and supports `--out` for a local file.
Update preserves the document ID and starts a replacement ingestion:

```bash
archastro update knowledgedocument <document-id> --content @./revised.md --wait
```

Verify that exact update ingestion and search for the changed content afterward.
Use source/document/item deletion only for the user's intended target; deleting a
source or normalized item is not interchangeable with replacing one document.

Report the owner, source/installation identifiers, ingestion state, and retrieval
evidence. Never claim usable agent knowledge solely because an upload succeeded.
