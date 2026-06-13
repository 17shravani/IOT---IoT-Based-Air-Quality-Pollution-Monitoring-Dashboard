# Reload Path variables from registry to ensure Git is detected
$machinePath = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
$userPath = [System.Environment]::GetEnvironmentVariable("Path", "User")
$env:Path = "$machinePath;$userPath"

$gitExe = $null

# Check if git is in path
$gitCmd = Get-Command git -ErrorAction SilentlyContinue
if ($gitCmd) {
    $gitExe = "git"
    Write-Host "Git detected in PATH: $( $gitCmd.Source )"
} else {
    # Scan standard installation paths
    $commonPaths = @(
        "C:\Program Files\Git\cmd\git.exe",
        "C:\Program Files\Git\bin\git.exe",
        "C:\Program Files (x86)\Git\cmd\git.exe",
        "C:\Program Files (x86)\Git\bin\git.exe"
    )
    foreach ($path in $commonPaths) {
        if (Test-Path $path) {
            $gitExe = $path
            Write-Host "Git detected at local path: $gitExe"
            break
        }
    }
}

if (-not $gitExe) {
    Write-Error "Git is not detected. Please verify that Git was installed successfully."
    exit 1
}

# Run Git initialization and commit
Write-Host "Initializing Git repository..."
& $gitExe init

Write-Host "Staging all project files..."
& $gitExe add --all

# Configure dummy user info if not configured to prevent commits failing
$gitUser = & $gitExe config --get user.name
if (-not $gitUser) {
    Write-Host "Setting temporary Git user configuration..."
    & $gitExe config user.name "AETHER-Network-Agent"
    & $gitExe config user.email "agent@aether.network"
}

Write-Host "Creating initial commit..."
& $gitExe commit -m "Initial commit: AETHER Network Command Center Platform"

Write-Host "Setting main branch..."
& $gitExe branch -M main

Write-Host "Setting remote origin URL..."
# Check and remove remote if it already exists
$remoteCheck = & $gitExe remote get-url origin 2>$null
if ($remoteCheck) {
    & $gitExe remote remove origin
}
& $gitExe remote add origin "https://github.com/17shravani/IOT---IoT-Based-Air-Quality-Pollution-Monitoring-Dashboard.git"

Write-Host "Pushing files to GitHub repository..."
Write-Host "Note: If Git Credential Manager pops up a sign-in window on your screen, please complete the sign-in to authenticate the push."
& $gitExe push -u origin main --force

Write-Host "Process completed."
