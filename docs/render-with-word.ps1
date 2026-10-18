$taskRoot = (Get-Location).Path
$taskWord = New-Object -ComObject Word.Application
$taskWord.Visible = $false
$taskWord.DisplayAlerts = 0
try {
  $taskDoc = $taskWord.Documents.Open("$taskRoot/docs/LinkGuardian_Project_Documentation.docx", $false, $true)
  $taskDoc.Repaginate()
  $taskDoc.ExportAsFixedFormat("$taskRoot/docs/qa/LinkGuardian_Project_Documentation.pdf", 17)
  $taskDoc.Close(0)
} finally {
  $taskWord.Quit()
  [System.Runtime.InteropServices.Marshal]::ReleaseComObject($taskWord) | Out-Null
}
