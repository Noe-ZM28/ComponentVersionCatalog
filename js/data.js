// DEMO DATA ONLY. Replace with verified records before internal use.
// Keep one component record per component and one version record per change/version.
const CATALOG = [
  {
    id:"RPT-001", name:"Daily Settlement Report Layout", category:"Report Layout", carrier:"Northstar Payments",
    status:"Approved", owner:"Payments Operations", lastUpdated:"2026-09-18", validation:"Validated",
    scope:"Production reporting", description:"Example report layout used to produce the daily settlement output. Confirm the approved file in its source location before using this record operationally.",
    sourceLabel:"Shared folder / Reporting / Northstar / DailySettlementLayout.xlsx (example path)",
    sourceUrl:"https://example.com/source/report-layout", ticketUrl:"https://example.com/jira/PROJ-1042",
    versions:[
      {version:"2.3",status:"Approved",recordedDate:"2026-09-18",ticket:"PROJ-1042",ticketUrl:"https://example.com/jira/PROJ-1042",author:"A. Example",change:"Added settlement reference and clarified amount formatting.",notes:"Illustrative approval record."},
      {version:"2.4",status:"In Review",recordedDate:"2026-10-02",ticket:"PROJ-1188",ticketUrl:"https://example.com/jira/PROJ-1188",author:"B. Example",change:"Proposed additional reconciliation field.",notes:"Newer version is not approved yet."},
      {version:"2.2",status:"Deprecated",recordedDate:"2026-07-11",ticket:"PROJ-0970",ticketUrl:"https://example.com/jira/PROJ-0970",author:"A. Example",change:"Previous layout before reference field update."}
    ]
  },
  {
    id:"PC1-004", name:"PC1 Product Configuration", category:"PC1", carrier:"Shared / Multi-carrier",
    status:"Approved", owner:"Configuration Team", lastUpdated:"2026-09-29", validation:"Validated",
    scope:"Shared configuration", description:"Illustrative PC1 configuration entry. The catalog points to the original configuration and records version metadata; it does not replace the source artifact.",
    sourceLabel:"Configuration share / PC1 / ProductConfig.xml (example path)",
    sourceUrl:"https://example.com/source/pc1", ticketUrl:"https://example.com/jira/PROJ-1125",
    versions:[
      {version:"1.8",status:"Approved",recordedDate:"2026-09-29",ticket:"PROJ-1125",ticketUrl:"https://example.com/jira/PROJ-1125",author:"C. Example",change:"Approved configuration for new product group.",notes:"Illustrative record."},
      {version:"1.7",status:"Deprecated",recordedDate:"2026-08-12",ticket:"PROJ-1051",ticketUrl:"https://example.com/jira/PROJ-1051",author:"C. Example",change:"Previous product group mapping."}
    ]
  },
  {
    id:"MAP-012", name:"Customer Data Mapping", category:"Mapping", carrier:"Northstar Payments",
    status:"In Review", owner:"Data Integration", lastUpdated:"2026-10-05", validation:"Pending validation",
    scope:"ETL / customer records", description:"Example mapping definition with source-to-target field rules. Review conditional mappings and default values in the source artifact.",
    sourceLabel:"Jira attachment / PROJ-1201 / customer_mapping.xlsx (example)",
    sourceUrl:"https://example.com/source/mapping", ticketUrl:"https://example.com/jira/PROJ-1201",
    versions:[
      {version:"1.4",status:"Approved",recordedDate:"2026-08-30",ticket:"PROJ-1098",ticketUrl:"https://example.com/jira/PROJ-1098",author:"D. Example",change:"Current approved mapping for customer records."},
      {version:"1.5",status:"In Review",recordedDate:"2026-10-05",ticket:"PROJ-1201",ticketUrl:"https://example.com/jira/PROJ-1201",author:"D. Example",change:"Proposed revised handling of customer reference values.",notes:"Not approved; continue using the approved version until validation is complete."}
    ]
  },
  {
    id:"CAR-007", name:"Northstar Carrier Package", category:"Carrier Package", carrier:"Northstar Payments",
    status:"Approved", owner:"Carrier Integration", lastUpdated:"2026-09-21", validation:"Validated",
    scope:"Carrier onboarding / production", description:"Example carrier delivery package. Package contents, checksum and deployment target should be recorded when available.",
    sourceLabel:"Shared folder / Carriers / Northstar / Package_4.1.zip (example path)",
    sourceUrl:"https://example.com/source/carrier-package", ticketUrl:"https://example.com/jira/PROJ-1150",
    versions:[
      {version:"4.1",status:"Approved",recordedDate:"2026-09-21",ticket:"PROJ-1150",ticketUrl:"https://example.com/jira/PROJ-1150",author:"E. Example",change:"Approved package following carrier validation."},
      {version:"4.0",status:"Deprecated",recordedDate:"2026-08-01",ticket:"PROJ-1012",ticketUrl:"https://example.com/jira/PROJ-1012",author:"E. Example",change:"Previous carrier package."}
    ]
  },
  {
    id:"SQL-023", name:"SP_UpdateCustomerProfile", category:"SQL Script", carrier:"Shared / Multi-carrier",
    status:"Pending verification", owner:"Database Team", lastUpdated:"2026-10-07", validation:"Not confirmed",
    scope:"SQL Server / CDSPLUSP (example)", description:"Example stored procedure tracked as a database object rather than a downloadable file. Version cannot be considered approved until the object definition and change ticket are verified.",
    sourceLabel:"SQL Server / CDSPLUSP.dbo.SP_UpdateCustomerProfile (example object reference)",
    sourceUrl:"https://example.com/source/sql-object", ticketUrl:"https://example.com/jira/PROJ-1210",
    versions:[
      {version:"Recorded 2026-10-07",status:"Pending verification",recordedDate:"2026-10-07",ticket:"PROJ-1210",ticketUrl:"https://example.com/jira/PROJ-1210",author:"F. Example",change:"Catalog entry created from a change reference; definition and approval not yet verified.",notes:"Do not treat this record as proof of the production version."},
      {version:"1.1 (historical)",status:"Approved",recordedDate:"2026-06-20",ticket:"PROJ-0891",ticketUrl:"https://example.com/jira/PROJ-0891",author:"F. Example",change:"Historical approved definition, subject to confirmation against current database state."}
    ]
  },
  {
    id:"MAP-019", name:"Transaction Code Mapping", category:"Mapping", carrier:"Eastwind Bank",
    status:"Draft", owner:"Data Integration", lastUpdated:"2026-10-10", validation:"Not started",
    scope:"ETL / transaction processing", description:"New mapping catalog record awaiting review and confirmation of the canonical source location.",
    sourceLabel:"Unconfirmed — source location to be added",
    sourceUrl:"https://example.com/source/to-be-confirmed", ticketUrl:"https://example.com/jira/PROJ-1224",
    versions:[
      {version:"0.1",status:"Draft",recordedDate:"2026-10-10",ticket:"PROJ-1224",ticketUrl:"https://example.com/jira/PROJ-1224",author:"G. Example",change:"Initial draft entry; mapping and source still need validation."}
    ]
  }
];