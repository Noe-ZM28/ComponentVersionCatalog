// DEMO DATA ONLY. Replace illustrative report examples and missing artifacts with verified files.
const demoVersion = (version, ticket, recordedDate, change, status = "Approved") => ({
  version,
  status,
  recordedDate,
  ticket,
  ticketUrl: `https://example.com/jira/${ticket}`,
  author: "Demo user",
  change
});

const pc1 = (id, project, name, fileName, content, date, ticket) => ({
  id,
  project,
  name,
  category: "PC1",
  carrier: "Compartido",
  status: "Approved",
  owner: "Equipo de configuración",
  lastUpdated: date,
  validation: "Ejemplo",
  scope: name,
  description: "PC1 de ejemplo en texto plano. El mapeo se mantiene dentro del propio archivo PC1.",
  sourceLabel: `Ejemplo ilustrativo (${fileName})`,
  example: { name: fileName, format: "Texto plano", content },
  versions: [demoVersion("1.0", ticket, date, "Ejemplo inicial de PC1 con mapeo incluido.")]
});

const report = (id, project, name, outputFormat, folder, reportFiles, exampleFiles, date, ticket) => ({
  id,
  project,
  name,
  category: "Reportes",
  reportFormat: outputFormat,
  carrier: "Compartido",
  status: "Approved",
  owner: "Operaciones",
  lastUpdated: date,
  validation: "Archivos de ejemplo disponibles",
  scope: name,
  description: `Archivos del reporte organizados en su carpeta, con una carpeta Example para la salida de muestra.`,
  reportFolder: folder,
  reportFiles,
  exampleFiles,
  sourceLabel: folder,
  versions: [demoVersion("1.0", ticket, date, `Registro de archivos del reporte ${outputFormat} y su ejemplo.`)]
});

const carrierPackage = (id, project, packageNumber, design, variants, date) => ({
  id,
  project,
  name: `Paquete ${packageNumber}`,
  category: "Carrier",
  carrier: `Design ${design}`,
  packageFile: `Carriers/${project}/Paquete ${packageNumber}/RichPDFPackage/Package_${packageNumber}.pkg3`,
  status: "Approved",
  owner: "Integración",
  lastUpdated: date,
  validation: "Paquete y ejemplos disponibles",
  scope: `Design ${design}`,
  description: "Cada paquete incluye el archivo PKG3 en RichPDFPackage y los PDF de muestra de sus variantes en Example.",
  sourceLabel: `Carriers/${project}/Paquete ${packageNumber}/`,
  variants: variants.map(variant => ({
    ...variant,
    file: `Carriers/${project}/Paquete ${packageNumber}/Example/${variant.fileName}`
  })),
  versions: [demoVersion("1.0", `DEMO-${id}`, date, `Paquete ${packageNumber}, Design ${design}, con ${variants.length} variantes PDF.`)]
});

const CATALOG = [
  pc1("PC1-PAY-001", "Proyecto 1", "PC1 de pagos", "PC1-Pagos.txt",
    "PC1_ID=PC1-PAY-001\r\nVERSION=1.0\r\nPROJECT=Proyecto 1\r\n\r\n[MAPPING]\r\nSOURCE=PAYMENT_REFERENCE\r\nTARGET=Payment.Reference\r\nTYPE=STRING\r\nREQUIRED=YES\r\n\r\nSOURCE=SETTLEMENT_DATE\r\nTARGET=Payment.SettlementDate\r\nTYPE=DATE\r\nFORMAT=yyyy-MM-dd",
    "2026-10-01", "DEMO-101"),
  pc1("PC1-SET-002", "Proyecto 1", "PC1 de liquidación", "PC1-Liquidacion.txt",
    "PC1_ID=PC1-SET-002\r\nVERSION=1.1\r\nPROJECT=Proyecto 1\r\n\r\n[MAPPING]\r\nSOURCE=SETTLEMENT_ID\r\nTARGET=Settlement.Id\r\nTYPE=STRING\r\nREQUIRED=YES\r\n\r\nSOURCE=NET_AMOUNT\r\nTARGET=Settlement.NetAmount\r\nTYPE=DECIMAL\r\nCURRENCY=USD",
    "2026-10-02", "DEMO-102"),
  pc1("PC1-CLI-001", "Proyecto 2", "PC1 de clientes", "PC1-Clientes.txt",
    "PC1_ID=PC1-CLI-001\r\nVERSION=1.0\r\nPROJECT=Proyecto 2\r\n\r\n[MAPPING]\r\nSOURCE=CUSTOMER_NUMBER\r\nTARGET=Customer.Number\r\nTYPE=STRING\r\nREQUIRED=YES\r\n\r\nSOURCE=BIRTH_DATE\r\nTARGET=Customer.BirthDate\r\nTYPE=DATE\r\nFORMAT=yyyy-MM-dd",
    "2026-10-08", "DEMO-201"),

  report("RPT-P1-001", "Proyecto 1", "Reporte mensual de producción", "PDF",
    "Reports/Proyecto 1/Reporte 1",
    [
      { label: "Crystal Reports (.rpt)", name: "MontlyReport.rpt", path: "Reports/Proyecto 1/Reporte 1/MontlyReport.rpt", sizeBytes: 0 },
      { label: "Consulta / procedimiento SQL", name: "MontlyReport.sql", path: "Reports/Proyecto 1/Reporte 1/MontlyReport.sql", sizeBytes: 2569 }
    ],
    [{ label: "Ejemplo PDF", name: "July2026.pdf", path: "Reports/Proyecto 1/Reporte 1/Example/July2026.pdf", sizeBytes: 28767 }],
    "2026-10-19", "DEMO-P1-RPT1"),
  report("RPT-P1-002", "Proyecto 1", "Reporte RCP", "Archivo RCP",
    "Reports/Proyecto 1/Reporte 2",
    [
      { label: "Generador · RefID SCRXXX000001", name: "SCRXXX000001.cs", path: "Reports/Proyecto 1/Reporte 2/SCRXXX000001.cs", sizeBytes: 1727 },
      { label: "SP / consulta SQL", name: "RCPReport.sql", path: "Reports/Proyecto 1/Reporte 2/RCPReport.sql", sizeBytes: 1324 }
    ],
    [{ label: "Ejemplo RCP", name: "20261019.RCP", path: "Reports/Proyecto 1/Reporte 2/Example/20261019.RCP", sizeBytes: 100 }],
    "2026-10-19", "DEMO-P1-RPT2"),
  report("RPT-P2-001", "Proyecto 2", "Reporte de producción", "Archivo de texto",
    "Reports/Proyecto 2/Reporte 1",
    [{ label: "Generador · RefID SCRYYY000001", name: "SCRYYY000001.cs", path: "Reports/Proyecto 2/Reporte 1/SCRYYY000001.cs", sizeBytes: 3405 }],
    [{ label: "Ejemplo de salida", name: "Production20261019.txt", path: "Reports/Proyecto 2/Reporte 1/Example/Production20261019.txt", sizeBytes: 5098 }],
    "2026-10-19", "DEMO-P2-RPT1"),

  carrierPackage("CAR-P1-P1", "Proyecto 1", "1", "1", [
    { name: "Variante 1 · Asterion Mobility GmbH", fileName: "01_Asterion_Mobility_GmbH_Design1_Variant1.pdf" }
  ], "2026-10-14"),
  carrierPackage("CAR-P2-P1", "Proyecto 2", "1", "4", [
    { name: "Variante 1 · Golden Maple Card Services", fileName: "07_Golden_Maple_Card_Services_Design4_Variant1.pdf" },
    { name: "Variante 2 · Helios Network Operations BV", fileName: "08_Helios_Network_Operations_BV_Design4_Variant2.pdf" },
    { name: "Variante 3 · Indigo Orchard Technologies Pte Ltd", fileName: "09_Indigo_Orchard_Technologies_Pte__Ltd_Design4_Variant3.pdf" },
    { name: "Variante 4 · Juniper Stone Processing S r l", fileName: "10_Juniper_Stone_Processing_S_r_l_Design4_Variant4.pdf" }
  ], "2026-10-15"),
  carrierPackage("CAR-P2-P2", "Proyecto 2", "2", "2", [
    { name: "Variante 1 · Blue Harbor Logistics Ltd", fileName: "02_Blue_Harbor_Logistics_Ltd_Design2_Variant1.pdf" },
    { name: "Variante 2 · Cedar Peak Financial Services", fileName: "03_Cedar_Peak_Financial_Services_Design2_Variant2.pdf" },
    { name: "Variante 3 · Delta Crescent Payments S A", fileName: "04_Delta_Crescent_Payments_S_A_Design2_Variant3.pdf" }
  ], "2026-10-16"),
  carrierPackage("CAR-P2-P3", "Proyecto 2", "3", "3", [
    { name: "Variante 1 · Evergreen Transit Solutions Inc", fileName: "05_Evergreen_Transit_Solutions_Inc_Design3_Variant1.pdf" },
    { name: "Variante 2 · Fjordline Commerce AS", fileName: "06_Fjordline_Commerce_AS_Design3_Variant2.pdf" }
  ], "2026-10-17")
];
