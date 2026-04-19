$Headers = @{ 'Authorization' = 'Bearer ntn_y92174488152E4krTdPhDePKZFRNslEmaAZHuS96vSN7sm'; 'Notion-Version' = '2022-06-28'; 'Content-Type' = 'application/json' }

Write-Host '1. Fetching Schema...'
$schema = Invoke-RestMethod -Uri 'https://api.notion.com/v1/databases/31f22567-1b6f-8190-b3a8-dc4f8422f01b' -Headers $Headers -Method GET
$schema | ConvertTo-Json -Depth 10 | Out-File -FilePath temp_schema.json -Encoding utf8

Write-Host '2. Fetching Candidates...'
$q_payload = '{"filter": {"property": "Functional Patterns", "multi_select": {"is_empty": true}}, "page_size": 100}'
$cands = Invoke-RestMethod -Uri 'https://api.notion.com/v1/databases/31f22567-1b6f-8190-b3a8-dc4f8422f01b/query' -Headers $Headers -Method POST -Body $q_payload
$cands | ConvertTo-Json -Depth 10 | Out-File -FilePath temp_candidates.json -Encoding utf8

