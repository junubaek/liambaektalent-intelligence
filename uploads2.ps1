$Headers = @{ 'Authorization' = 'Bearer ntn_y92174488152E4krTdPhDePKZFRNslEmaAZHuS96vSN7sm'; 'Notion-Version' = '2022-06-28' }

$ErrorActionPreference = 'Stop'

Write-Host 'Updating 32022567-1b6f-8114-9122-fee5c551a609'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = '경영 전략 및 기획 업무 총괄' }, @{ name = 'Implemented and managed CI/CD pipelines' }, @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8114-9122-fee5c551a609' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8114-9122-fee5c551a609:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8114-9d27-c1bbac66ce3a'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = '공정 설계 (Designed processes)' }, @{ name = '경영 전략 및 기획 업무 총괄' }, @{ name = 'General Professional Experience' }, @{ name = 'Managed SysOps team' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8114-9d27-c1bbac66ce3a' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8114-9d27-c1bbac66ce3a:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8114-bf51-da8096cd5a36'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'Built and managed crawling engine' }, @{ name = 'Automated installation processes' }, @{ name = 'General Professional Experience' }, @{ name = 'Managed datacenter devices' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8114-bf51-da8096cd5a36' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8114-bf51-da8096cd5a36:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8115-aa2a-e523baccbb4f'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = '경영 전략 및 기획 업무 총괄' }, @{ name = 'Built and managed crawling engine' }, @{ name = 'Managed SysOps team' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8115-aa2a-e523baccbb4f' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8115-aa2a-e523baccbb4f:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8116-87fc-cf77c4720a24'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = '경영 전략 및 기획 업무 총괄' }, @{ name = '공정 설계 (Designed processes)' }, @{ name = 'Test Pattern Update' }, @{ name = 'Managed SysOps team' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8116-87fc-cf77c4720a24' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8116-87fc-cf77c4720a24:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8116-9363-fa276721f1ad'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8116-9363-fa276721f1ad' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8116-9363-fa276721f1ad:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8116-a6e4-e2718a5f3c9c'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' }, @{ name = 'Built and managed crawling engine' }, @{ name = 'Led iOS app development' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8116-a6e4-e2718a5f3c9c' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8116-a6e4-e2718a5f3c9c:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8117-baa9-e48f7b0fb68f'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8117-baa9-e48f7b0fb68f' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8117-baa9-e48f7b0fb68f:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8117-bcc7-e59214ecd66d'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'Implemented and optimized prediction algorithms' }, @{ name = 'Led iOS app development' }, @{ name = 'Designed and planned service MVP' }, @{ name = 'Automated installation processes' }, @{ name = 'Managed 16 angel investment matching funds totaling approximately 192 billion KRW.' }, @{ name = 'Test Pattern Update' }, @{ name = '신사업 프로젝트 리딩 (Led new business projects)' }, @{ name = 'Converted development environments' }, @{ name = 'Developed software' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8117-bcc7-e59214ecd66d' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8117-bcc7-e59214ecd66d:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8118-a1ce-c4bdb79e4b59'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8118-a1ce-c4bdb79e4b59' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8118-a1ce-c4bdb79e4b59:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-811a-bb9b-e9e6d118e051'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = '주도 및 관리했습니다 제품 개발 프로세스' }, @{ name = '캠페인 관리' }, @{ name = '출원 상표권 등록 업무' }, @{ name = '마케팅 데이터 분석' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-811a-bb9b-e9e6d118e051' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-811a-bb9b-e9e6d118e051:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-811a-bd21-ec4826dca687'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-811a-bd21-ec4826dca687' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-811a-bd21-ec4826dca687:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-811b-8ca6-cc39b90f0600'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'Designed and implemented 3D fully convolutional networks' }, @{ name = 'Built and managed crawling engine' }, @{ name = 'Managed datacenter devices' }, @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-811b-8ca6-cc39b90f0600' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-811b-8ca6-cc39b90f0600:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-811b-96c5-fdd9e640e01c'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-811b-96c5-fdd9e640e01c' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-811b-96c5-fdd9e640e01c:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-811b-9bf0-dbe0bf9e58f1'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-811b-9bf0-dbe0bf9e58f1' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-811b-9bf0-dbe0bf9e58f1:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-811b-bb50-f750abca1226'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-811b-bb50-f750abca1226' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-811b-bb50-f750abca1226:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-811c-80c1-db80bbeff246'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-811c-80c1-db80bbeff246' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-811c-80c1-db80bbeff246:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-811c-8332-f119fc46c9df'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-811c-8332-f119fc46c9df' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-811c-8332-f119fc46c9df:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-811c-8969-db4f8b912b98'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-811c-8969-db4f8b912b98' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-811c-8969-db4f8b912b98:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-811c-a263-d1ae967cb555'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-811c-a263-d1ae967cb555' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-811c-a263-d1ae967cb555:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-811d-80fc-c979e4f5e091'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-811d-80fc-c979e4f5e091' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-811d-80fc-c979e4f5e091:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-811e-9074-f4a404e27ca7'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-811e-9074-f4a404e27ca7' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-811e-9074-f4a404e27ca7:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-811e-9267-ffbc873014d6'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-811e-9267-ffbc873014d6' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-811e-9267-ffbc873014d6:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-811e-976e-e75af66703a0'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-811e-976e-e75af66703a0' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-811e-976e-e75af66703a0:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-811e-a78a-e705a334fa23'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-811e-a78a-e705a334fa23' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-811e-a78a-e705a334fa23:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-811e-bc5a-f8ea3448d526'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-811e-bc5a-f8ea3448d526' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-811e-bc5a-f8ea3448d526:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-811f-842d-d481e186a26d'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-811f-842d-d481e186a26d' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-811f-842d-d481e186a26d:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-811f-85f1-d77f6589e94d'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-811f-85f1-d77f6589e94d' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-811f-85f1-d77f6589e94d:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-811f-97fc-f2083f6e65ea'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-811f-97fc-f2083f6e65ea' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-811f-97fc-f2083f6e65ea:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-811f-a387-c1dc0d34e230'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-811f-a387-c1dc0d34e230' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-811f-a387-c1dc0d34e230:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-811f-adcb-c49efc412e91'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-811f-adcb-c49efc412e91' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-811f-adcb-c49efc412e91:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8120-8367-d197c7fc4cbd'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8120-8367-d197c7fc4cbd' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8120-8367-d197c7fc4cbd:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8120-a179-d4e4d1b06e57'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8120-a179-d4e4d1b06e57' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8120-a179-d4e4d1b06e57:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8120-a7f3-e6aae4eab8b8'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8120-a7f3-e6aae4eab8b8' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8120-a7f3-e6aae4eab8b8:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8120-b802-c9e6d7f6af70'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8120-b802-c9e6d7f6af70' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8120-b802-c9e6d7f6af70:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8120-bc79-ee10685d7e8d'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8120-bc79-ee10685d7e8d' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8120-bc79-ee10685d7e8d:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8121-81a0-cb68bf10df89'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8121-81a0-cb68bf10df89' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8121-81a0-cb68bf10df89:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8121-b3b4-dac79d7ece90'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8121-b3b4-dac79d7ece90' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8121-b3b4-dac79d7ece90:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8122-a997-fa427985a965'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8122-a997-fa427985a965' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8122-a997-fa427985a965:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8122-ba8b-ce8f371ab1db'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8122-ba8b-ce8f371ab1db' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8122-ba8b-ce8f371ab1db:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8122-bd16-db952530b9fe'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8122-bd16-db952530b9fe' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8122-bd16-db952530b9fe:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8122-bed2-d9c1c06b37c0'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8122-bed2-d9c1c06b37c0' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8122-bed2-d9c1c06b37c0:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8123-a40b-ec5e7d46ba17'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8123-a40b-ec5e7d46ba17' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8123-a40b-ec5e7d46ba17:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8123-a9a4-eaa5116ac821'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8123-a9a4-eaa5116ac821' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8123-a9a4-eaa5116ac821:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8123-af67-f5748cb948c2'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8123-af67-f5748cb948c2' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8123-af67-f5748cb948c2:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8123-b8fd-f47bff4055a2'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8123-b8fd-f47bff4055a2' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8123-b8fd-f47bff4055a2:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8124-9bab-d4c77c14ecc7'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8124-9bab-d4c77c14ecc7' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8124-9bab-d4c77c14ecc7:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8124-a0f0-ddbf18f8ef6d'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8124-a0f0-ddbf18f8ef6d' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8124-a0f0-ddbf18f8ef6d:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8125-8799-dd223956fa07'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8125-8799-dd223956fa07' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8125-8799-dd223956fa07:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8125-9490-d04744b2006d'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8125-9490-d04744b2006d' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8125-9490-d04744b2006d:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8125-b557-f8e9c56216b5'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8125-b557-f8e9c56216b5' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8125-b557-f8e9c56216b5:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8126-9167-cefec6f30f29'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8126-9167-cefec6f30f29' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8126-9167-cefec6f30f29:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8126-a723-f07a0fe0d713'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8126-a723-f07a0fe0d713' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8126-a723-f07a0fe0d713:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8126-b174-c6645541e3e6'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8126-b174-c6645541e3e6' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8126-b174-c6645541e3e6:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8126-bd2b-efe5afe5b274'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8126-bd2b-efe5afe5b274' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8126-bd2b-efe5afe5b274:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8127-b76a-c8ddde021dc3'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8127-b76a-c8ddde021dc3' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8127-b76a-c8ddde021dc3:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8128-8b6e-cb018d743249'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8128-8b6e-cb018d743249' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8128-8b6e-cb018d743249:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8128-ac6e-f5fc195c66db'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8128-ac6e-f5fc195c66db' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8128-ac6e-f5fc195c66db:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-812a-ac39-dd91d6183f2b'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-812a-ac39-dd91d6183f2b' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-812a-ac39-dd91d6183f2b:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-812b-8b36-c97777dae9d7'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-812b-8b36-c97777dae9d7' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-812b-8b36-c97777dae9d7:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-812b-b7ce-f838672de47e'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-812b-b7ce-f838672de47e' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-812b-b7ce-f838672de47e:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-812d-ac3a-c21ed63b7004'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-812d-ac3a-c21ed63b7004' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-812d-ac3a-c21ed63b7004:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-812e-8b5f-d348eb444d89'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-812e-8b5f-d348eb444d89' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-812e-8b5f-d348eb444d89:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-812e-93c3-fd068971085d'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-812e-93c3-fd068971085d' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-812e-93c3-fd068971085d:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-812e-94a5-fce58dcbfbd7'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-812e-94a5-fce58dcbfbd7' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-812e-94a5-fce58dcbfbd7:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-812e-9e09-c9a564c0545d'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-812e-9e09-c9a564c0545d' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-812e-9e09-c9a564c0545d:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-812e-9ecd-d7e6f504c5dd'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-812e-9ecd-d7e6f504c5dd' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-812e-9ecd-d7e6f504c5dd:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-812e-ae32-e48274943c81'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-812e-ae32-e48274943c81' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-812e-ae32-e48274943c81:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-812e-b8a5-c5847ef63cfa'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-812e-b8a5-c5847ef63cfa' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-812e-b8a5-c5847ef63cfa:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-812f-8aa8-c8cba80eb948'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-812f-8aa8-c8cba80eb948' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-812f-8aa8-c8cba80eb948:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-812f-92ca-d027829dbbfe'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-812f-92ca-d027829dbbfe' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-812f-92ca-d027829dbbfe:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-812f-9a02-c4fa81c11173'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-812f-9a02-c4fa81c11173' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-812f-9a02-c4fa81c11173:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-812f-aa8e-f93541c1da9f'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-812f-aa8e-f93541c1da9f' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-812f-aa8e-f93541c1da9f:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-812f-bba0-e2ff702280c7'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-812f-bba0-e2ff702280c7' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-812f-bba0-e2ff702280c7:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8130-9e00-df3b033cd0e1'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8130-9e00-df3b033cd0e1' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8130-9e00-df3b033cd0e1:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8130-bf40-e2a8616f4ab0'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8130-bf40-e2a8616f4ab0' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8130-bf40-e2a8616f4ab0:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8131-b56d-d93152309eee'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8131-b56d-d93152309eee' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8131-b56d-d93152309eee:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8132-9d25-f8c6ffee6863'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8132-9d25-f8c6ffee6863' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8132-9d25-f8c6ffee6863:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8132-9eab-eba137af9310'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8132-9eab-eba137af9310' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8132-9eab-eba137af9310:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8133-a0b3-f3e92d910409'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8133-a0b3-f3e92d910409' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8133-a0b3-f3e92d910409:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8133-b446-cf286a9811c5'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8133-b446-cf286a9811c5' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8133-b446-cf286a9811c5:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8134-b883-ee629507e49a'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8134-b883-ee629507e49a' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8134-b883-ee629507e49a:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8135-9f12-f03a20e69679'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8135-9f12-f03a20e69679' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8135-9f12-f03a20e69679:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8137-8764-f6e99ebd6461'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8137-8764-f6e99ebd6461' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8137-8764-f6e99ebd6461:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8137-b2de-f1841cadf5da'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8137-b2de-f1841cadf5da' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8137-b2de-f1841cadf5da:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8137-bb54-e62783149764'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8137-bb54-e62783149764' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8137-bb54-e62783149764:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8138-85d8-f2d535af003c'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8138-85d8-f2d535af003c' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8138-85d8-f2d535af003c:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8138-a066-c8c30c83a27a'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8138-a066-c8c30c83a27a' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8138-a066-c8c30c83a27a:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8139-b3fc-ef8330fc9287'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8139-b3fc-ef8330fc9287' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8139-b3fc-ef8330fc9287:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-813a-9a37-c71f032dc1c4'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-813a-9a37-c71f032dc1c4' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-813a-9a37-c71f032dc1c4:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-813a-a0f7-f3ecb6cb11cc'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-813a-a0f7-f3ecb6cb11cc' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-813a-a0f7-f3ecb6cb11cc:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-813a-becf-d5d742cc0845'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-813a-becf-d5d742cc0845' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-813a-becf-d5d742cc0845:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-813b-8b19-f7c50b1efa63'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-813b-8b19-f7c50b1efa63' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-813b-8b19-f7c50b1efa63:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-813b-a1d6-f83d7f68767a'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-813b-a1d6-f83d7f68767a' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-813b-a1d6-f83d7f68767a:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-813b-b172-dcde21627114'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-813b-b172-dcde21627114' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-813b-b172-dcde21627114:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-813c-9a72-fc093719d49b'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-813c-9a72-fc093719d49b' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-813c-9a72-fc093719d49b:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-813c-9d1f-c5cecc281859'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-813c-9d1f-c5cecc281859' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-813c-9d1f-c5cecc281859:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-813c-a865-e31c353bffe1'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-813c-a865-e31c353bffe1' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-813c-a865-e31c353bffe1:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-813c-a8c6-cb4280f7b8a6'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-813c-a8c6-cb4280f7b8a6' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-813c-a8c6-cb4280f7b8a6:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-813c-b290-c0bb79c63ed5'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-813c-b290-c0bb79c63ed5' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-813c-b290-c0bb79c63ed5:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8120-a179-d4e4d1b06e57'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8120-a179-d4e4d1b06e57' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8120-a179-d4e4d1b06e57:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8120-a7f3-e6aae4eab8b8'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8120-a7f3-e6aae4eab8b8' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8120-a7f3-e6aae4eab8b8:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8120-b802-c9e6d7f6af70'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8120-b802-c9e6d7f6af70' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8120-b802-c9e6d7f6af70:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8120-bc79-ee10685d7e8d'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8120-bc79-ee10685d7e8d' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8120-bc79-ee10685d7e8d:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8121-81a0-cb68bf10df89'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8121-81a0-cb68bf10df89' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8121-81a0-cb68bf10df89:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8121-b3b4-dac79d7ece90'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8121-b3b4-dac79d7ece90' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8121-b3b4-dac79d7ece90:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8122-a997-fa427985a965'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8122-a997-fa427985a965' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8122-a997-fa427985a965:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8122-ba8b-ce8f371ab1db'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8122-ba8b-ce8f371ab1db' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8122-ba8b-ce8f371ab1db:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8122-bd16-db952530b9fe'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8122-bd16-db952530b9fe' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8122-bd16-db952530b9fe:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8122-bed2-d9c1c06b37c0'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8122-bed2-d9c1c06b37c0' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8122-bed2-d9c1c06b37c0:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8123-a40b-ec5e7d46ba17'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8123-a40b-ec5e7d46ba17' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8123-a40b-ec5e7d46ba17:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8123-a9a4-eaa5116ac821'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8123-a9a4-eaa5116ac821' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8123-a9a4-eaa5116ac821:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8123-af67-f5748cb948c2'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8123-af67-f5748cb948c2' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8123-af67-f5748cb948c2:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8123-b8fd-f47bff4055a2'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8123-b8fd-f47bff4055a2' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8123-b8fd-f47bff4055a2:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8124-9bab-d4c77c14ecc7'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8124-9bab-d4c77c14ecc7' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8124-9bab-d4c77c14ecc7:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8124-a0f0-ddbf18f8ef6d'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8124-a0f0-ddbf18f8ef6d' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8124-a0f0-ddbf18f8ef6d:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8125-8799-dd223956fa07'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8125-8799-dd223956fa07' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8125-8799-dd223956fa07:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8125-9490-d04744b2006d'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8125-9490-d04744b2006d' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8125-9490-d04744b2006d:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8125-b557-f8e9c56216b5'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8125-b557-f8e9c56216b5' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8125-b557-f8e9c56216b5:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8126-9167-cefec6f30f29'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8126-9167-cefec6f30f29' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8126-9167-cefec6f30f29:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8126-a723-f07a0fe0d713'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8126-a723-f07a0fe0d713' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8126-a723-f07a0fe0d713:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-813d-9b17-e9086b744be4'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'Built and managed crawling engine' }, @{ name = '경영 전략 및 기획 업무 총괄' }, @{ name = 'General Professional Experience' }, @{ name = 'Reconstructed server clusters' }, @{ name = '공정 설계 (Designed processes)' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-813d-9b17-e9086b744be4' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-813d-9b17-e9086b744be4:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-813e-bc57-c811ea13ea4b'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'Managed datacenter devices' }, @{ name = '경영 전략 및 기획 업무 총괄' }, @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-813e-bc57-c811ea13ea4b' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-813e-bc57-c811ea13ea4b:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-813e-bd26-f6aef4ede9cb'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-813e-bd26-f6aef4ede9cb' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-813e-bd26-f6aef4ede9cb:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-813f-80af-ce3537b7d93c'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-813f-80af-ce3537b7d93c' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-813f-80af-ce3537b7d93c:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-813f-8484-d9035745f21d'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = '캠페인 관리' }, @{ name = '경영 전략 및 기획 업무 총괄' }, @{ name = '마케팅 데이터 분석' }, @{ name = '캠페인 기획' }, @{ name = '지원 IP 보호 및 활용' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-813f-8484-d9035745f21d' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-813f-8484-d9035745f21d:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-813f-866c-c145c86cf76d'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-813f-866c-c145c86cf76d' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-813f-866c-c145c86cf76d:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-813f-a3cd-cfa6f8042542'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-813f-a3cd-cfa6f8042542' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-813f-a3cd-cfa6f8042542:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8140-9d49-f3f038b20c5f'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = '시운전 수행 (Conducted commissioning) 플랜트 공사 관련' }, @{ name = 'Converted development environments' }, @{ name = 'Managed Kubernetes clusters' }, @{ name = 'Managed datacenter devices' }, @{ name = '기계설계 수행 (Performed mechanical design) MDF 신규 공장 및 환경설비' }, @{ name = 'Managed SysOps team' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8140-9d49-f3f038b20c5f' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8140-9d49-f3f038b20c5f:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8140-abaf-f910dd391ae4'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8140-abaf-f910dd391ae4' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8140-abaf-f910dd391ae4:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8140-b696-f1e1a6e43000'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = '시운전 수행 (Conducted commissioning) 플랜트 공사 관련' }, @{ name = 'General Professional Experience' }, @{ name = 'Built and managed crawling engine' }, @{ name = '경영 전략 및 기획 업무 총괄' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8140-b696-f1e1a6e43000' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8140-b696-f1e1a6e43000:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8141-8c08-e4abdb6c3347'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8141-8c08-e4abdb6c3347' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8141-8c08-e4abdb6c3347:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

Write-Host 'Updating 32022567-1b6f-8141-a6d1-ed8af5962858'
$p = @{ properties = @{ 'Functional Patterns' = @{ multi_select = @( @{ name = 'General Professional Experience' } ) } } } | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Uri 'https://api.notion.com/v1/pages/32022567-1b6f-8141-a6d1-ed8af5962858' -Headers $Headers -Method PATCH -ContentType 'application/json' -Body $p | Out-Null
} catch {
  Write-Host 'Error on 32022567-1b6f-8141-a6d1-ed8af5962858:' $_.Exception.Response.StatusCode.value__
  $stream = $_.Exception.Response.GetResponseStream()
  $reader = New-Object System.IO.StreamReader($stream)
  Write-Host $reader.ReadToEnd()
}

