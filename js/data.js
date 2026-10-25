// DEMO DATA ONLY. Replace illustrative report examples and missing artifacts with verified files.
const demoVersion = (version, ticket, recordedDate, change, snapshot, status = "Approved", author = "Demo user", notes = "", previewBefore = "", previewAfter = "") => ({
  version,
  status,
  ticketStatus: status,
  recordedDate,
  ticket,
  ticketType: "Tarea",
  ticketName: change,
  ticketUrl: `https://example.com/jira/${ticket}`,
  author,
  change,
  snapshot,
  previewBefore,
  previewAfter,
  notes
});

const randomSample = items => {
  const shuffled = [...items];
  for (let index = shuffled.length - 1; index > 0; index--) {
    const randomIndex = Math.floor(Math.random() * (index + 1));
    [shuffled[index], shuffled[randomIndex]] = [shuffled[randomIndex], shuffled[index]];
  }
  return shuffled.slice(0, 1 + Math.floor(Math.random() * shuffled.length));
};

let demoHistorySequence = 0;
const demoHistory = (ticket, approvedDate, change, currentVersion = "1.0", example = "Ejemplo ilustrativo del elemento.", previews = {}) => {
  const historyLength = 4 + demoHistorySequence++;
  const [major, minor] = currentVersion.split(".").map(Number);
  const previousVersion = minor > 0 ? `${major}.${minor - 1}` : `${Math.max(0, major - 1)}.9`;
  const previousDate = new Date(`${approvedDate}T12:00:00Z`);
  previousDate.setUTCDate(previousDate.getUTCDate() - 30);
  const previousRecordedDate = previousDate.toISOString().slice(0, 10);
  const snapshotFor = version => example.replace(/\bVERSION=\d+\.\d+\b/, `VERSION=${version}`);
  const previousExample = previews.before || example;
  const currentExample = previews.current || example;
  const proposedExample = previews.proposed || example;
  const currentChange = previews.currentChange || change;
  const proposedChange = previews.proposedChange || change;
  const previewBefore = sample => Object.keys(previews).length ? sample : "";
  const olderChanges = [
    "Se normalizaron nombres y valores de campos para el ejemplo.",
    "Se incorporaron campos adicionales al registro de demostración.",
    "Se creó la primera versión del ejemplo estructurado.",
    "Se ajustó el formato del archivo de muestra.",
    "Se actualizaron campos opcionales del registro.",
    "Se revisó la estructura para mantener compatibilidad."
  ];
  const olderVersions = Array.from({ length: historyLength - 3 }, (_, index) => {
    const olderVersion = `0.${String(Math.max(0, 9 - index)).padStart(2, "0")}`;
    const olderDate = new Date(`${previousRecordedDate}T12:00:00Z`);
    olderDate.setUTCDate(olderDate.getUTCDate() - (30 * (index + 1)));
    const olderChange = olderChanges[index % olderChanges.length];

    return demoVersion(
      olderVersion,
      `${ticket}-HIST-${index + 1}`,
      olderDate.toISOString().slice(0, 10),
      olderChange,
      snapshotFor(olderVersion),
      "Deprecated",
      "Historial de demostración"
    );
  });

  return [
    demoVersion(`${major}.${minor + 1}`, `${ticket}-REV`, "2026-10-19", `Propuesta: ${proposedChange}`, snapshotFor(`${major}.${minor + 1}`), "In Review", "Equipo de cambios", "", previewBefore(currentExample), previewBefore(proposedExample)),
    demoVersion(currentVersion, ticket, approvedDate, currentChange, snapshotFor(currentVersion), "Approved",  "", previewBefore(previousExample), previewBefore(currentExample)),
    demoVersion(previousVersion, `${ticket}-PREV`, previousRecordedDate, "Versión anterior conservada para consulta histórica.", snapshotFor(previousVersion), "Deprecated", "Historial de demostración", "", previewBefore(previousExample)),
    ...olderVersions
  ];
};

const pc1RecordExample = recordNumber => {
  const paddedNumber = String(recordNumber).padStart(3, "0");
  const record = {
    PAN: `1234 XXXX XX${String(recordNumber).padStart(2, "0")} 1234`,
    RecordId: `DUMMY-RECORD-${paddedNumber}`,
    CardHolderName: `DUMMY CARDHOLDER ${paddedNumber}`,
    AddressLine1: `DUMMY ADDRESS LINE 1-${paddedNumber}`,
    AddressLine2: `DUMMY ADDRESS LINE 2-${paddedNumber}`,
    AddressLine3: `DUMMY CITY ${paddedNumber}`,
    AddressLine4: `DUMMY STATE ${paddedNumber}`,
    AddressLine5: `DUMMY POSTAL CODE ${paddedNumber}`,
    AddressLine6: "DUMMY COUNTRY",
    ChipData: `DUMMY_CHIP_${paddedNumber};CHIP-DUMMY-${paddedNumber}`,
    Track: `TRACK-DUMMY-${paddedNumber}`
  };

  for (let index = 1; index <= 20; index++) {
    record[`Data${String(index).padStart(2, "0")}`] = `DATA-DUMMY-${paddedNumber}-${String(index).padStart(2, "0")}`;
  }

  return Object.entries(record).map(([field, value]) => `<${field}>${value}</${field}>`).join("\r\n");
};

const pc1 = (id, project, name, fileName, recordNumber, date, ticket, version = "1.0") => {
  const content = pc1RecordExample(recordNumber);
  return {
    id,
    project,
    name,
    category: "PC1",
    chain: { name: "PRD", step: 12 },
    carrier: "Compartido",
    status: "Approved",
    owner: "Equipo de configuración",
    lastUpdated: date,
    validation: "Ejemplo",
    scope: name,
    description: "Ejemplo PC1 de texto plano con campos delimitados por etiquetas, siguiendo la estructura de los registros dummy.",
    sourceLabel: `Ejemplo ilustrativo (${fileName})`,
    example: { name: fileName, format: "Texto plano", content },
    versions: demoHistory(ticket, date, "Actualización de estructura del registro PC1.", version, content, id === "PC1-PAY-001" ? {
      before: content.replace("DUMMY CITY 001", "DUMMY CITY PREVIOUS 001"),
      proposed: content.replace("DUMMY CARDHOLDER 001", "DUMMY CARDHOLDER PROPOSED 001"),
      currentChange: "Se actualizó el dato de ciudad manteniendo la estructura de campos PC1.",
      proposedChange: "Se propone actualizar el nombre de ejemplo del titular."
    } : {}).map(version => ({
      ...version,
      ticketType: "PC1",
      historyFiles: [{
        label: "Ejemplo PC1",
        name: fileName,
        preview: version.snapshot,
        previewTruncated: false
      }]
    }))
  };
};

const report = (id, project, name, outputFormat, folder, reportFiles, exampleFiles, date, ticket, chain) => ({
  id,
  project,
  name,
  category: "Reporte",
  chain,
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
  versions: demoHistory(ticket, date, `Actualización de archivos y ejemplo del reporte ${outputFormat}.`, "1.0", exampleFiles.map(file => `${file.label}: ${file.name}${file.preview ? `\n${file.preview}` : ""}`).join("\n\n"), id === "RPT-P2-001" ? {
    before: exampleFiles[0].preview.replace(/APPROVED/g, "ACCEPTED").replace(/REJECTED/g, "DECLINED"),
    proposed: exampleFiles[0].preview.replace("APPROVED", "VALIDATED"),
    currentChange: "Se normalizaron los estados ACCEPTED y DECLINED a APPROVED y REJECTED.",
    proposedChange: "Se propone mostrar VALIDATED para los registros aprobados."
  } : {}).map(version => ({
    ...version,
    ticketType: "Reporte",
    historyFiles: [...reportFiles, ...exampleFiles]
  }))
});

const carrierPackage = (id, project, packageNumber, design, variants, date) => {
  const namedVariants = variants.map(variant => ({
    ...variant,
    name: variant.name.replace(/^Variante \d+ · /, "")
  }));

  return {
    id,
    project,
    name: `Paquete ${packageNumber}`,
    category: "Carrier",
    chain: { name: "CPP", step: 10 },
    carrier: `Design ${design}`,
    packageFile: `Carriers/${project}/Paquete ${packageNumber}/RichPDFPackage/Package_${packageNumber}.pkg3`,
    status: "Approved",
    owner: "Integración",
    lastUpdated: date,
    validation: "Paquete y ejemplos disponibles",
    scope: `Design ${design}`,
    description: "Cada paquete incluye el archivo PKG3 en RichPDFPackage y los PDF de muestra de sus variantes en Example.",
    sourceLabel: `Carriers/${project}/Paquete ${packageNumber}/`,
    variants: namedVariants.map(variant => ({
      ...variant,
      file: `Carriers/${project}/Paquete ${packageNumber}/Example/${variant.fileName}`
    })),
    versions: demoHistory(`DEMO-${id}`, date, `Actualización de variantes del paquete ${packageNumber}.`, "1.0", namedVariants.map(variant => `${variant.name}\nArchivo: ${variant.fileName}`).join("\n\n")).map(version => ({
      ...version,
      ticketType: "Carrier",
      historyFiles: randomSample(namedVariants).map(variant => ({
        label: variant.name,
        name: variant.fileName,
        path: `Carriers/${project}/Paquete ${packageNumber}/Example/${variant.fileName}`,
        sizeBytes: variant.sizeBytes
      }))
    }))
  };
};

const CATALOG = [
  pc1("PC1-PAY-001", "Proyecto 1", "PC1 - Banco 1", "PC1 - Banco 1",
    1,
    "2026-10-01", "DEMO-101"),
  pc1("PC1-SET-002", "Proyecto 1", "PC1 - Banco 2", "PC1 - Banco 2",
    2,
    "2026-10-02", "DEMO-102", "1.1"),
  pc1("PC1-CLI-001", "Proyecto 2", "PC1 - Banco 3", "PC1 - Banco 3",
    3,
    "2026-10-08", "DEMO-201"),

  report("RPT-P1-001", "Proyecto 1", "Reporte mensual de producción", "PDF",
    "Reports/Proyecto 1/Reporte 1",
    [
      { label: "Crystal Reports (.rpt)", name: "MontlyReport.rpt", path: "Reports/Proyecto 1/Reporte 1/MontlyReport.rpt", sizeBytes: 0 },
      { label: "Consulta / procedimiento SQL", name: "MontlyReport.sql", path: "Reports/Proyecto 1/Reporte 1/MontlyReport.sql", sizeBytes: 2569, preview: `SET NOCOUNT ON;
GO

CREATE PROCEDURE dbo.usp_Report_MonthlyCardProduction
    @Year  INT,
    @Month INT
AS
BEGIN
    SET NOCOUNT ON;

    IF @Year < 2000 OR @Year > 2100
    BEGIN
        RAISERROR('The year must be between 2000 and 2100.', 16, 1);
        RETURN;
    END;`, previewTruncated: true }
    ],
    [{ label: "Ejemplo PDF", name: "July2026.pdf", path: "Reports/Proyecto 1/Reporte 1/Example/July2026.pdf", sizeBytes: 28767 }],
    "2026-10-19", "DEMO-P1-RPT1", { name: "R01", step: 1 }),
  report("RPT-P1-002", "Proyecto 1", "Reporte RCP", "Archivo RCP",
    "Reports/Proyecto 1/Reporte 2",
    [
      { label: "Generador · RefID SCRXXX000001", name: "SCRXXX000001.cs", path: "Reports/Proyecto 1/Reporte 2/SCRXXX000001.cs", sizeBytes: 1727, preview: `using System;
using System.IO;
using ScriptLib;
using System.Collections.Generic;
using System.Linq;
using System.Text;

public partial class Script
{
    protected override void Initialize()
    {
        List<Data> exists =
            f.ExecuteSPGetReturnCode<Data>("usp_ReceiveRCP_Dummy");`, previewTruncated: true },
      { label: "SP / consulta SQL", name: "RCPReport.sql", path: "Reports/Proyecto 1/Reporte 2/RCPReport.sql", sizeBytes: 1324, preview: `CREATE OR ALTER PROCEDURE dbo.usp_ReceiveRCP_Dummy
    @RecordType  CHAR(3),
    @FileId      CHAR(10),
    @RecordCount CHAR(7),
    @FileDate    CHAR(8),
    @FileName    CHAR(72)
AS
BEGIN
    SET NOCOUNT ON;

    IF LTRIM(RTRIM(@RecordType)) = ''
    BEGIN
        RAISERROR('RecordType es obligatorio.', 16, 1);
        RETURN;
    END;`, previewTruncated: true }
    ],
    [{ label: "Ejemplo RCP", name: "20261019.RCP", path: "Reports/Proyecto 1/Reporte 2/Example/20261019.RCP", sizeBytes: 100, preview: "RCPFILE000001000000120261019CARD_PRODUCTION_20261019.RCP" }],
    "2026-10-19", "DEMO-P1-RPT2", { name: "R02", step: 2 }),
  report("RPT-P2-001", "Proyecto 2", "Reporte de producción", "Archivo de texto",
    "Reports/Proyecto 2/Reporte 1",
    [{ label: "Generador · RefID SCRYYY000001", name: "SCRYYY000001.cs", path: "Reports/Proyecto 2/Reporte 1/SCRYYY000001.cs", sizeBytes: 3405, preview: `using System;
using System.IO;
using System.Collections.Generic;
using System.Text;
using ScriptLib;

public class ProductionData
{
    public string RecordType { get; set; }
    public string CardId { get; set; }
    public string ProductionDate { get; set; }
    public string CardProduct { get; set; }
    public string Status { get; set; }
}

public partial class Script
{
    protected override void Initialize()
    {
        string date = DateTime.Now.ToString("yyyyMMdd");`, previewTruncated: true }],
    [{ label: "Ejemplo de salida", name: "Production20261019.txt", path: "Reports/Proyecto 2/Reporte 1/Example/Production20261019.txt", sizeBytes: 5098, preview: `PRDCARD202610190000000120261019DEBIT_CLASSIC       APPROVED  BATCH20261019001    PLANT_MX_01
PRDCARD202610190000000220261018CREDIT_GOLD         APPROVED  BATCH20261018001    PLANT_MX_02
PRDCARD202610190000000320261017PREPAID             APPROVED  BATCH20261017001    PLANT_MX_03`, previewTruncated: true }],
    "2026-10-19", "DEMO-P2-RPT1", { name: "R03", step: 3 }),

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
