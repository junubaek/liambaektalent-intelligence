$ErrorActionPreference = 'Stop'
$secrets = Get-Content 'secrets.json' | ConvertFrom-Json
$h = @{
    'Authorization' = 'Bearer ' + $secrets.NOTION_API_KEY
    'Notion-Version' = '2022-06-28'
}
$b = @"
{
    "properties": {
        "Functional Patterns": {
            "multi_select": [
                {
                    "name": "General Professional Experience"
                }
            ]
        }
    }
}
"@

try {
  $response = Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/31f22567-1b6f-8134-ac17-e6273507f5b1' -Headers $h -Method PATCH -ContentType 'application/json' -Body $b
  $response.properties.'Functional Patterns' | ConvertTo-Json -Depth 5
} catch {
  Write-Host "Error Code:" $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host "Raw JSON Response:"
  Write-Host $reader.ReadToEnd()
}
