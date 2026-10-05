param([switch]$PrepareOnly, [switch]$ResumeDraft)

$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$Package = Get-Content -LiteralPath (Join-Path $Root 'vscode-extension\package.json') -Raw | ConvertFrom-Json
if ($Package.version -notmatch '^\d+\.\d+\.\d+$' -or $Package.name -notmatch '^[a-z0-9-]+$') { throw 'Invalid package version/name.' }
if ($Package.repository.url -notmatch '^https://github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)\.git$') { throw 'Expected a GitHub HTTPS repository URL.' }
$Repository = $Matches[1]
$Version = $Package.version
$Tag = "v$Version"
$Title = "TokenWise $Version - Windows Beta"
$ArtifactName = "$($Package.name)-$Version.vsix"
$Artifacts = Join-Path $Root 'releases'
$Release = Join-Path $Artifacts "TokenWise-$Version"
$ArchiveName = "TokenWise-$Version.zip"
$ArchivePath = Join-Path $Artifacts $ArchiveName
$PublicChecksums = Join-Path $Artifacts "SHA256SUMS-$Version.txt"
$ExpectedFiles = @($ArtifactName, 'README.md', 'LICENSE', 'THIRD-PARTY-NOTICES.md', 'CHANGELOG.md', 'RELEASE-NOTES.md',
    'demonstation.md', 'docs/ANTIGRAVITY.md', 'docs/PROJECT-EVALUATION.md', 'docs/DEVELOPMENT.md', 'docs/PUBLISHING.md', 'docs/THIRD-PARTY-NOTICES.md')

function Get-ReleaseFile([string]$Relative) {
    $Full = [System.IO.Path]::GetFullPath((Join-Path $Release $Relative))
    if (-not $Full.StartsWith($Release + [System.IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) { throw 'Release path escapes its folder.' }
    $Item = Get-Item -LiteralPath $Full
    if ($Item.PSIsContainer) { throw "Expected a file: $Relative" }
    while ($Item.FullName -ne $Artifacts) {
        if ($Item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) { throw 'Release paths cannot use symbolic links/junctions.' }
        $Item = Get-Item -LiteralPath ([System.IO.Path]::GetDirectoryName($Item.FullName))
    }
    return $Full
}

function Get-Sha256([string]$Path) { return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant() }

function Get-GitOutput([string[]]$Arguments) {
    $Output = & git @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Git operation failed: $($Arguments[0])" }
    return ($Output -join "`n").Trim()
}

function Invoke-GitHub([string]$Method, [string]$Uri, $Body = $null) {
    if (([Uri]$Uri).Host -ne 'api.github.com' -or ([Uri]$Uri).Scheme -ne 'https') { throw 'Invalid GitHub API destination.' }
    $Parameters = @{ Method = $Method; Uri = $Uri; Headers = $Headers; TimeoutSec = 60; MaximumRedirection = 0 }
    if ($null -ne $Body) {
        $Parameters.Body = [System.Text.Encoding]::UTF8.GetBytes(($Body | ConvertTo-Json -Depth 10))
        $Parameters.ContentType = 'application/json; charset=utf-8'
    }
    return Invoke-RestMethod @Parameters
}

# Archive only verified, explicitly allowlisted artifacts, never an entire worktree.
Push-Location $Root
try {
    $DemoSource = Get-GitOutput -Arguments @('ls-files', '--', 'demonstration')
    if (-not $DemoSource) { throw 'Tracked demonstration source is missing.' }
    $ExcludedDemoPaths = 0
    foreach ($Relative in ($DemoSource -split "`n")) {
        $Parts = $Relative -split '/'
        if (@($Parts | Where-Object { $_ -in @('results', '__pycache__', '.agents', '.tokenwise') }).Count -or
            $Parts[-1] -in @('.gitignore', '.gitattributes')) {
            $ExcludedDemoPaths++
            continue
        }
        if ($Relative -notmatch '^demonstration/[A-Za-z0-9_./-]+\.(py|json|md)$' -or
            '..' -in $Parts) {
            throw "Unexpected tracked demonstration path: $Relative"
        }
        $ExpectedFiles += $Relative
    }
    if ($ExcludedDemoPaths) { Write-Host "Excluded $ExcludedDemoPaths tracked runtime/metadata paths; checkout files are unchanged." }
} finally { Pop-Location }
$Checksums = @{}
foreach ($Line in Get-Content -LiteralPath (Get-ReleaseFile 'SHA256SUMS.txt')) {
    if ($Line -notmatch '^([a-f0-9]{64})  (.+)$') { throw 'Malformed release checksums. Re-run npm run package.' }
    $Hash = $Matches[1]
    $Relative = $Matches[2]
    if ($Relative -notin $ExpectedFiles -or $Checksums.ContainsKey($Relative)) { throw "Unexpected/duplicate release file: $Relative" }
    if ((Get-Sha256 (Get-ReleaseFile $Relative)) -ne $Hash) { throw "Checksum failed: $Relative" }
    $Checksums[$Relative] = $Hash
}
if ($Checksums.Count -ne $ExpectedFiles.Count) { throw 'Release is incomplete. Re-run npm run package.' }
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem
$TemporaryArchive = Join-Path $Artifacts (".TokenWise-$Version-" + [Guid]::NewGuid().ToString('N') + '.zip')
try {
    $Zip = [System.IO.Compression.ZipFile]::Open($TemporaryArchive, [System.IO.Compression.ZipArchiveMode]::Create)
    try {
        foreach ($Relative in @($ExpectedFiles) + @('SHA256SUMS.txt')) {
            [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($Zip, (Get-ReleaseFile $Relative), $Relative, [System.IO.Compression.CompressionLevel]::Optimal) | Out-Null
        }
    } finally { $Zip.Dispose() }
    Move-Item -LiteralPath $TemporaryArchive -Destination $ArchivePath -Force
} finally { if (Test-Path -LiteralPath $TemporaryArchive) { Remove-Item -LiteralPath $TemporaryArchive } }
$ArchiveHash = Get-Sha256 $ArchivePath
$ChecksumText = "$($Checksums[$ArtifactName])  $ArtifactName`n$ArchiveHash  $ArchiveName`n"
[System.IO.File]::WriteAllText($PublicChecksums, $ChecksumText, (New-Object System.Text.UTF8Encoding($false)))
Write-Host "Verified $($Checksums.Count) release files; prepared $ArchiveName."
if ($PrepareOnly) { return }

$Headers = @{}
$Credential = @{}
$CredentialLines = $null
Push-Location $Root
try {
    $ReleaseStatus = Get-GitOutput -Arguments @('status', '--porcelain', '--', '.',
        ':(glob,exclude)demonstration/**/.agents/**', ':(glob,exclude)demonstration/**/.tokenwise/**',
        ':(glob,exclude)demonstration/**/__pycache__/**', ':(glob,exclude)demonstration/**/results/**',
        ':(glob,exclude)demonstration/**/.gitignore', ':(glob,exclude)demonstration/**/.gitattributes')
    if ($ReleaseStatus) { throw 'Commit/review all release source and documentation changes before publishing.' }
    if ((Get-GitOutput -Arguments @('branch', '--show-current')) -ne 'main') { throw 'Publish from the main branch.' }
    if ((Get-GitOutput -Arguments @('remote', 'get-url', 'origin')) -ne $Package.repository.url) { throw 'Git origin and package repository disagree.' }
    $Head = Get-GitOutput -Arguments @('rev-parse', 'HEAD')
    if ((Get-GitOutput -Arguments @('cat-file', '-t', $Tag)) -ne 'tag') { throw 'Create and push an annotated version tag first.' }
    if ((Get-GitOutput -Arguments @('rev-parse', "$Tag^{commit}")) -ne $Head) { throw 'The version tag must point to the current release commit.' }

    $env:GIT_TERMINAL_PROMPT = '0'
    $env:GCM_INTERACTIVE = 'never'
    $CredentialLines = "protocol=https`nhost=github.com`npath=$Repository.git`n`n" | git -c credential.interactive=never credential fill
    if ($LASTEXITCODE -ne 0) { throw 'Sign in through Git Credential Manager, then retry. Do not put credentials in files or chat.' }
    foreach ($Line in $CredentialLines) {
        $Parts = $Line -split '=', 2
        if ($Parts.Count -eq 2) { $Credential[$Parts[0]] = $Parts[1] }
    }
    if (-not $Credential.password) { throw 'GitHub authentication is unavailable.' }
    $Headers = @{ Authorization = 'Bearer ' + $Credential.password; Accept = 'application/vnd.github+json'; 'X-GitHub-Api-Version' = '2022-11-28'; 'User-Agent' = 'TokenWise-Release' }
    $Api = "https://api.github.com/repos/$Repository"
    $User = Invoke-GitHub 'Get' 'https://api.github.com/user'
    $Repo = Invoke-GitHub 'Get' $Api
    if (-not $Repo.permissions.push -or $Repo.private) { throw 'This workflow requires write access to the public project repository.' }
    if ((Invoke-GitHub 'Get' "$Api/git/ref/heads/main").object.sha -ne $Head) { throw 'Push the exact main commit before publishing.' }
    $TagObject = (Invoke-GitHub 'Get' "$Api/git/ref/tags/$Tag").object
    if ($TagObject.type -eq 'tag') { $TagObject = (Invoke-GitHub 'Get' "$Api/git/tags/$($TagObject.sha)").object }
    if ($TagObject.type -ne 'commit' -or $TagObject.sha -ne $Head) { throw 'The remote tag does not match the release commit.' }

    $Existing = @()
    for ($Page = 1; ; $Page++) {
        $Items = @(Invoke-GitHub 'Get' "$Api/releases?per_page=100&page=$Page")
        $Existing = @($Items | Where-Object { $_.tag_name -eq $Tag })
        if ($Existing.Count -or $Items.Count -lt 100) { break }
    }
    $Body = Get-Content -LiteralPath (Get-ReleaseFile 'RELEASE-NOTES.md') -Raw -Encoding UTF8
    $DigestSection = "### Published Asset Checksums`n`n" + '```text' + "`n$ChecksumText" + '```'
    $Body = $Body.Replace('<!-- TOKENWISE_ASSET_CHECKSUMS -->', $DigestSection)
    if ($Existing.Count) {
        $Draft = $Existing[0]
        if (-not $ResumeDraft -or -not $Draft.draft -or $Draft.name -ne $Title -or $Draft.target_commitish -ne $Head -or $Draft.author.login -ne $User.login) {
            throw 'A release already exists. Do not overwrite published releases or unrelated drafts.'
        }
    } else {
        $Draft = Invoke-GitHub 'Post' "$Api/releases" @{ tag_name = $Tag; target_commitish = $Head; name = $Title; body = $Body; draft = $true; prerelease = $true; make_latest = 'false' }
    }
    Write-Host "Uploading verified assets to draft $($Draft.id) in $Repository."
    $Assets = @(
        @{ Name = $ArtifactName; Path = (Get-ReleaseFile $ArtifactName); Hash = $Checksums[$ArtifactName]; Type = 'application/octet-stream'; Label = 'Install in Antigravity (recommended)' },
        @{ Name = $ArchiveName; Path = $ArchivePath; Hash = $ArchiveHash; Type = 'application/zip'; Label = 'Installer, demo projects, presentation guide, and licenses' },
        @{ Name = 'SHA256SUMS.txt'; Path = $PublicChecksums; Hash = (Get-Sha256 $PublicChecksums); Type = 'text/plain'; Label = 'SHA-256 download checksums' }
    )
    foreach ($File in $Assets) {
        $Uploaded = @($Draft.assets | Where-Object { $_.name -eq $File.Name })
        if ($Uploaded.Count) { $Asset = $Uploaded[0] }
        else {
            $Upload = "https://uploads.github.com/repos/$Repository/releases/$($Draft.id)/assets?name=$([Uri]::EscapeDataString($File.Name))&label=$([Uri]::EscapeDataString($File.Label))"
            $Asset = Invoke-RestMethod -Method Post -Uri $Upload -Headers $Headers -ContentType $File.Type -InFile $File.Path -TimeoutSec 300 -MaximumRedirection 0
        }
        if ($Asset.state -ne 'uploaded' -or $Asset.size -ne (Get-Item -LiteralPath $File.Path).Length -or $Asset.digest -ne ('sha256:' + $File.Hash)) {
            throw "GitHub integrity verification failed for $($File.Name). The release remains a draft."
        }
        Write-Host "Verified uploaded asset: $($File.Name)"
    }
    $Ready = Invoke-GitHub 'Get' "$Api/releases/$($Draft.id)"
    if ($Ready.assets.Count -ne $Assets.Count) { throw 'Unexpected draft assets; inspect the release before publishing.' }
    $Published = Invoke-GitHub 'Patch' "$Api/releases/$($Draft.id)" @{ draft = $false; prerelease = $true; make_latest = 'false'; body = $Body }
    if ($Published.draft -or -not $Published.prerelease) { throw 'Unexpected publication state.' }
    Write-Host "Published: $($Published.html_url)"
} finally {
    $Headers.Clear()
    $Credential.Clear()
    $CredentialLines = $null
    Pop-Location
}
