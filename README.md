# Component Version Catalog — Prototype v0.1

## What this is
A static, browser-based prototype for manually consulting component versions, approval status, change history, and Jira/source references.

**All records, version numbers, ticket keys, people, and URLs are fictitious examples. Do not use them as operational references.**

## Run locally
1. Keep the `css` and `js` folders next to `index.html`.
2. Open `index.html` in a modern browser.
3. Search, filter by category/status, open a component, and inspect its history.

No build tools, external libraries, server, or database are required for this prototype.

## Files
- `index.html`: UI structure.
- `css/styles.css`: page styles.
- `js/app.js`: filtering and detail/history rendering.
- `js/data.js`: sample catalog data. Edit this file to replace demo entries with verified records.

## Manual update workflow (proposed)
1. Identify the change ticket in Jira.
2. Confirm the original source artifact/object and the actual version.
3. Add a version entry in `js/data.js` with ticket, date, author, change summary, and status.
4. Mark a version `Approved` only after the responsible person confirms its approval.
5. Keep prior version entries for history.
6. Review the page in a browser and submit the change through the team's approved Bitbucket workflow.
7. Do not put credentials, secrets, sensitive production data, or restricted attachments in this static catalog.

## Important data model distinction
- `approvedVersion`: newest version entry whose status is `Approved`.
- `latestRecorded`: newest entry by `recordedDate`, irrespective of approval.
- Component-level `status`: overall state of the catalog entry; use `Pending verification` when the real current version/source has not been confirmed.

The current demo treats the latest recorded entry as the one with the newest `recordedDate`. For production, consider adding a separate unique `versionId` and a verified approval timestamp, and define how to compare versions that do not follow semantic numbering.

## Production considerations
- Confirm whether the company uses Bitbucket Cloud or Data Center and which internal hosting options are approved.
- Ensure the site is restricted to the intended team if the catalog exposes internal component names or source links.
- The prototype does not connect to Jira, databases, file shares, Confluence, or authentication. Example links point to `example.com` and must be replaced.
- The page is static and does not itself enforce approval permissions; the manual process and repository access controls must do so.
"# ComponentVersionCatalog" 
