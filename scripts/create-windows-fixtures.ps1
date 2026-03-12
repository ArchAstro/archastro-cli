param(
    [Parameter(Mandatory = $true)]
    [string]$OutputDir,
    [string]$Version = "0.3.1",
    [string]$ArchLabel = "x64"
)

$ErrorActionPreference = "Stop"

$AssetName = "archastro-windows-$ArchLabel.zip"
$TempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("archastro-fixture-" + [System.Guid]::NewGuid().ToString("N"))
$PayloadDir = Join-Path $TempRoot "payload"
$SourcePath = Join-Path $TempRoot "Program.cs"
$BinaryPath = Join-Path $PayloadDir "archastro.exe"
$ChecksumPath = Join-Path $OutputDir "SHA256SUMS"
$ArchivePath = Join-Path $OutputDir $AssetName

New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
New-Item -ItemType Directory -Path $PayloadDir -Force | Out-Null

$Source = @"
using System;

public static class Program
{
    public static void Main(string[] args)
    {
        if (args.Length > 0 && (args[0] == "--version" || args[0] == "version"))
        {
            Console.WriteLine("$Version");
            return;
        }

        if (args.Length > 1 && args[0] == "completion")
        {
            switch (args[1])
            {
                case "bash":
                    Console.WriteLine("complete -W \"--version completion\" archastro");
                    return;
                case "zsh":
                    Console.WriteLine("#compdef archastro");
                    return;
                case "fish":
                    Console.WriteLine("complete -c archastro -l version");
                    return;
            }
        }

        Console.WriteLine("archastro fixture");
    }
}
"@

try {
    Set-Content -Path $SourcePath -Value $Source
    $Csc = Get-Command csc.exe -ErrorAction SilentlyContinue
    if (-not $Csc) {
        throw "csc.exe is required to generate Windows fixture binaries"
    }
    & $Csc.Source /nologo /target:exe /out:$BinaryPath $SourcePath | Out-Null
    Compress-Archive -Path $BinaryPath -DestinationPath $ArchivePath -Force
    $Checksum = (Get-FileHash $ArchivePath -Algorithm SHA256).Hash.ToLowerInvariant()
    Set-Content -Path $ChecksumPath -Value "$Checksum  $AssetName"
} finally {
    Remove-Item $TempRoot -Recurse -Force -ErrorAction SilentlyContinue
}
