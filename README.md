# Component Version Catalog — Prototype v0.1

## What this is
A static, browser-based prototype for consulting project PC1 configurations, report layouts and examples, carrier packages and their PDF variants, and version history.

**All records, version numbers, ticket keys, people, and URLs are fictitious examples. Do not use them as operational references.**

## Run locally
1. Keep the `css` and `js` folders next to `index.html`.
2. Open `index.html` in a modern browser.
3. Filter by project or category, open an item, and switch between its detail and history views.
4. Use the header button to switch between light and dark mode. The selected mode is saved in the browser; when no preference is saved, the system color preference is used.

No build tools, external libraries, server, or database are required for this prototype.

## Files
- `index.html`: UI structure.
- `css/styles.css`: page styles.
- `js/app.js`: filtering and detail/history rendering.
- `js/data.js`: catalog data. Edit this file to replace example records and artifact references with verified files.
- `Carriers/`: each package has its `.pkg3` file under `RichPDFPackage/` and its variant PDF examples under `Example/`.
- `Reports/`: report source files and output examples, grouped by project and report.

PC1 examples use the tagged-record layout shown in `dummy_card_records_50.txt` (`PAN`, `RecordId`, address fields, `ChipData`, `Track`, and `Data01`–`Data20`) with synthetic, masked values. Carrier variant labels show the bank variant name.

## File previews
- PDF files can be previewed inline in the browser; text, SQL, C# and RCP files show an excerpt alongside their links.
- `.rpt` and `.pkg3` package files are intentionally excluded from previews.
- Detail files use the same individual expandable list as history. Expanded text previews are not clipped; files with excerpt-only data are labeled partial and can be opened in a new tab.

Change histories include fictitious examples of a proposed revision in review, the current approved version, and a different number of prior deprecated versions per catalog item. Every history entry includes previews of its associated example files: text samples are shown inline and PDFs are embedded. Selected PC1 and production-report entries also show before/after previews derived from the supplied examples. These previews may use current catalog examples rather than versioned historical snapshots; they are demonstrations, not verified historical records, and the original files are not overwritten. Replace the demo tickets, dates, authors, descriptions, and snapshots with verified history before operational use.

## Manual update workflow (proposed)
1. Identify the change ticket in Jira.
2. Confirm the original source artifact/object and the actual version.
3. Keep each report's source files in `Reports/<Proyecto>/<Reporte>/` and its output sample in the `Example` subfolder. Register both folders and file paths in `js/data.js`.
4. For PDF reports, include the Crystal Reports `.rpt` definition. For text or other formats, include the output-generating script named by its RefID. Add the `.sql` query/SP file when the report uses one.
5. Add version entries with ticket, date, author, change summary, and status to track changes over time.
6. Mark a version `Approved` only after the responsible person confirms its approval.
7. Keep prior version entries for history.
8. Review the page in a browser and submit the change through the team's approved Bitbucket workflow.
9. Do not put credentials, secrets, sensitive production data, or restricted attachments in this static catalog.

The report list reflects the files present under `Reports/`. The available `MontlyReport.rpt` is empty (0 bytes), and is marked as such. The SQL and generator files and report examples link to their supplied files. Carrier entries link to each package's `.pkg3` file and variant PDFs using the `RichPDFPackage/` and `Example/` folders.

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
