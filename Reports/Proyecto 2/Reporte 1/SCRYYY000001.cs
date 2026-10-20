using System;
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
    public string BatchReference { get; set; }
    public string ProductionSite { get; set; }
}

public partial class Script
{
    protected override void Initialize()
    {
        string date = DateTime.Now.ToString("yyyyMMdd");

        string fileName = "Production" + date + ".txt";
        string filePath = Path.Combine(
            p.WorkDirectory,
            fileName
        );

        List<ProductionData> records =
            GenerateDummyProduction(date);

        List<string> lines = new List<string>();

        foreach (ProductionData record in records)
        {
            string line =
                FormatField(record.RecordType, 3) +
                FormatField(record.CardId, 20) +
                FormatField(record.ProductionDate, 8) +
                FormatField(record.CardProduct, 20) +
                FormatField(record.Status, 10) +
                FormatField(record.BatchReference, 20) +
                FormatField(record.ProductionSite, 19);

            if (line.Length != 100)
            {
                throw new Exception(
                    "El registro no tiene 100 caracteres."
                );
            }

            lines.Add(line);
        }

        File.WriteAllLines(
            filePath,
            lines,
            Encoding.ASCII
        );
    }

    private string FormatField(string value, int length)
    {
        value = value ?? "";

        if (value.Length > length)
            value = value.Substring(0, length);

        return value.PadRight(length);
    }

    private List<ProductionData> GenerateDummyProduction(
        string currentDate)
    {
        List<ProductionData> records =
            new List<ProductionData>();

        string[] products = {
            "DEBIT_CLASSIC",
            "CREDIT_GOLD",
            "PREPAID",
            "DEBIT_PLATINUM",
            "CREDIT_CLASSIC"
        };

        string[] sites = {
            "PLANT_MX_01",
            "PLANT_MX_02",
            "PLANT_MX_03"
        };

        for (int i = 1; i <= 50; i++)
        {
            DateTime productionDate =
                DateTime.Now.Date.AddDays(-((i - 1) % 28));

            ProductionData record = new ProductionData();

            record.RecordType = "PRD";

            record.CardId = "CARD" +
                currentDate +
                i.ToString("D8");

            record.ProductionDate =
                productionDate.ToString("yyyyMMdd");

            record.CardProduct =
                products[(i - 1) % products.Length];

            record.Status =
                (i % 4 == 0) ? "REJECTED" : "APPROVED";

            record.BatchReference = "BATCH" +
                productionDate.ToString("yyyyMMdd") +
                (((i - 1) / 10) + 1).ToString("D3");

            record.ProductionSite =
                sites[(i - 1) % sites.Length];

            records.Add(record);
        }

        return records;
    }
}