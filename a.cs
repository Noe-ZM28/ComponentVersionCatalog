
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

		List<Data> exists = f.ExecuteSPGetReturnCode<Data>("usp_ReceiveRCP_Dummy");
		
		_outputRecordset.SaveAs(Path.Combine(p.WorkDirectory, p.OutputFile), true);
	}

}
