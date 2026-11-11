using System;
using System.IO;
using ScriptLib;
using System.Collections.Generic;
using System.Linq;
using System.Text;

public partial class Script
{
    protected override void Initialize()
    {
        string filePath = Path.Combine(p.WorkDirectory, p.JobId);

        List<Data> exists =
            f.ExecuteSPGetReturnCode<Data>("usp_ReceiveRCP_Dummy");

        // Crear el archivo de reporte RCP
        string reportPath = Path.Combine(
            p.WorkDirectory,
            p.OutputFile
        );

        using (StreamWriter writer = new StreamWriter(
            reportPath, false, Encoding.ASCII))
        {
            foreach (Data record in exists)
            {
                string line =
                    (record.RecordType ?? "").PadRight(3).Substring(0, 3) +
                    (record.FileId ?? "").PadRight(10).Substring(0, 10) +
                    (record.RecordCount ?? "").PadRight(7).Substring(0, 7) +
                    (record.FileDate ?? "").PadRight(8).Substring(0, 8) +
                    (record.FileName ?? "").PadRight(72).Substring(0, 72);

                if (line.Length != 100)
                    throw new Exception("El registro RCP no tiene 100 caracteres.");

                writer.Write(line);
                writer.Write("\r\n");
            }
        }

        // Guardar también el recordset de salida de ScriptLib
        _outputRecordset.SaveAs(reportPath, true);
    }

    public class Data
{
    public string RecordType { get; set; }
    public string FileId { get; set; }
    public string RecordCount { get; set; }
    public string FileDate { get; set; }
    public string FileName { get; set; }
}
}