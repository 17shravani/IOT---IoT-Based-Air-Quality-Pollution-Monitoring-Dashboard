# PowerShell script to generate mock air quality data and analytical report.
# This ensures the workspace contains valid data out of the box.

$LogsDir = "data"
$LogsFile = "data/sensor_logs.csv"
$ReportsDir = "reports"
$ReportFile = "reports/air_quality_report.txt"

# Create directories
New-Item -ItemType Directory -Force -Path $LogsDir | Out-Null
New-Item -ItemType Directory -Force -Path $ReportsDir | Out-Null

# Initialize CSV log file
$Header = "timestamp,temperature,humidity,gas_raw,pm25,pm10,aqi,category,alert_triggered,alert_message,mode"
Set-Content -Path $LogsFile -Value $Header

# Function to calculate AQI PM2.5
function Get-Aqi ($pm25) {
    if ($pm25 -le 12.0) { return [Math]::Round(((50 - 0)/(12.0 - 0)) * ($pm25 - 0) + 0) }
    elseif ($pm25 -le 35.4) { return [Math]::Round(((100 - 51)/(35.4 - 12.1)) * ($pm25 - 12.1) + 51) }
    elseif ($pm25 -le 55.4) { return [Math]::Round(((150 - 101)/(55.4 - 35.5)) * ($pm25 - 35.5) + 101) }
    elseif ($pm25 -le 150.4) { return [Math]::Round(((200 - 151)/(150.4 - 55.5)) * ($pm25 - 55.5) + 151) }
    elseif ($pm25 -le 250.4) { return [Math]::Round(((300 - 201)/(250.4 - 150.5)) * ($pm25 - 150.5) + 201) }
    else { return [Math]::Round(((500 - 301)/(500.4 - 250.5)) * ($pm25 - 250.5) + 301) }
}

# Function to classify category
function Get-Category ($aqi) {
    if ($aqi -le 50) { return "Good" }
    elseif ($aqi -le 100) { return "Moderate" }
    elseif ($aqi -le 150) { return "Unhealthy for Sensitive Groups" }
    elseif ($aqi -le 200) { return "Unhealthy" }
    elseif ($aqi -le 300) { return "Very Unhealthy" }
    else { return "Hazardous" }
}

# Populate 24h data (96 readings at 15-minute intervals)
$Now = Get-Date
$Readings = @()
$TotalSteps = 96

Write-Host "[PS SIMULATOR] Generating 96 historical records (24 hours)..."

for ($i = 0; $i -lt $TotalSteps; $i++) {
    $OffsetMinutes = 15 * ($TotalSteps - $i)
    $Timestamp = $Now.AddMinutes(-$OffsetMinutes)
    $Hour = $Timestamp.Hour + ($Timestamp.Minute / 60.0)
    
    # Mode cycle
    $Mode = "normal"
    if ($i -ge 25 -and $i -lt 35) { $Mode = "gas_leak" }
    elseif ($i -ge 50 -and $i -lt 65) { $Mode = "wildfire" }
    elseif ($i -ge 70 -and $i -lt 80) { $Mode = "heavy_rain" }
    elseif ($i -ge 85) { $Mode = "clean_air" }
    
    # Diurnal Temp/Humidity
    $TempCycle = 5.0 * [Math]::Sin(2 * [Math]::PI * ($Hour - 8) / 24.0)
    $HumCycle = -10.0 * [Math]::Sin(2 * [Math]::PI * ($Hour - 8) / 24.0)
    
    $Temp = 25.0 + $TempCycle + (Get-Random -Minimum -20 -Maximum 20)/100.0
    $Hum = 60.0 + $HumCycle + (Get-Random -Minimum -50 -Maximum 50)/100.0
    if ($Hum -gt 100.0) { $Hum = 100.0 }
    if ($Hum -lt 0.0) { $Hum = 0.0 }
    
    # Traffic spikes at 8-10 AM and 5-7 PM
    $TrafficFactor = 0.0
    if ($Hour -ge 8.0 -and $Hour -le 10.0) {
        $TrafficFactor = [Math]::Sin([Math]::PI * ($Hour - 8) / 2.0)
    }
    elseif ($Hour -ge 17.0 -and $Hour -le 19.0) {
        $TrafficFactor = [Math]::Sin([Math]::PI * ($Hour - 17) / 2.0)
    }
    
    $TrafficGas = 400.0 * $TrafficFactor
    $TrafficPM = 15.0 * $TrafficFactor
    
    # Base readings
    $Gas = 400.0 + $TrafficGas + (Get-Random -Minimum -150 -Maximum 150)/10.0
    $PM25 = 8.0 + $TrafficPM + (Get-Random -Minimum -10 -Maximum 10)/10.0
    
    # Apply mode overrides
    if ($Mode -eq "gas_leak") {
        $Gas += (Get-Random -Minimum 1800 -Maximum 2800)
        $PM25 += (Get-Random -Minimum 100 -Maximum 300)/10.0
    }
    elseif ($Mode -eq "wildfire") {
        $Gas += (Get-Random -Minimum 1200 -Maximum 1800)
        $PM25 += (Get-Random -Minimum 1900 -Maximum 3200)/10.0
    }
    elseif ($Mode -eq "heavy_rain") {
        $Gas -= (Get-Random -Minimum 40 -Maximum 80)
        $PM25 = $PM25 * 0.15
        $Temp -= 3.5
        $Hum = $Hum + 20.0
        if ($Hum -gt 98.0) { $Hum = 98.0 }
    }
    elseif ($Mode -eq "clean_air") {
        $Gas = $Gas * 0.75
        $PM25 = 3.5 + (Get-Random -Minimum -5 -Maximum 5)/10.0
    }
    
    # Clamp
    if ($Gas -lt 0) { $Gas = 0 }
    if ($PM25 -lt 0.1) { $PM25 = 0.1 }
    $Gas = [Math]::Round($Gas)
    $PM25 = [Math]::Round($PM25, 2)
    
    $PM10 = $PM25 * 1.6 + (Get-Random -Minimum -10 -Maximum 10)/10.0
    if ($Mode -eq "wildfire") {
        $PM10 = $PM25 * 2.2 + (Get-Random -Minimum -30 -Maximum 30)/10.0
    }
    if ($PM10 -lt 0.2) { $PM10 = 0.2 }
    $PM10 = [Math]::Round($PM10, 2)
    
    # AQI
    $Aqi = Get-Aqi $PM25
    $Category = Get-Category $Aqi
    
    # Alerts
    $AlertTriggered = "False"
    $AlertMsg = ""
    if ($Aqi -gt 100) {
        $AlertTriggered = "True"
        $AlertMsg = "WARNING: $Category Air Quality (AQI $Aqi) detected!"
    }
    if ($Gas -gt 1500) {
        $AlertTriggered = "True"
        if ($AlertMsg) { $AlertMsg += " " }
        $AlertMsg += "DANGER: High Combustible/Harmful Gas Level ($Gas Analog)!"
    }
    
    # Round Temp/Hum
    $Temp = [Math]::Round($Temp, 2)
    $Hum = [Math]::Round($Hum, 2)
    
    # Append
    $CSVLine = "$($Timestamp.ToString('yyyy-MM-dd HH:mm:ss')),$Temp,$Hum,$Gas,$PM25,$PM10,$Aqi,$Category,$AlertTriggered,`"$AlertMsg`",$Mode"
    Add-Content -Path $LogsFile -Value $CSVLine
}

Write-Host "[PS SIMULATOR] CSV data successfully logged: $LogsFile"

# ----------------------------------------------------
# Generate Report Analysis
# ----------------------------------------------------
Write-Host "[PS ANALYZER] Compiling air quality analytical report..."

$Lines = Get-Content -Path $LogsFile | Select-Object -Skip 1
$TotalRecords = $Lines.Count

# Initialize metrics variables
$SumTemp = 0; $MinTemp = 999; $MaxTemp = -999
$SumHum = 0; $MinHum = 999; $MaxHum = -999
$SumGas = 0; $MinGas = 99999; $MaxGas = -99999
$SumPM25 = 0; $MinPM25 = 999; $MaxPM25 = -999
$SumPM10 = 0; $MinPM10 = 999; $MaxPM10 = -999
$SumAqi = 0; $MinAqi = 999; $MaxAqi = -999
$AlertsCount = 0

$CatCounts = @{
    "Good" = 0
    "Moderate" = 0
    "Unhealthy for Sensitive Groups" = 0
    "Unhealthy" = 0
    "Very Unhealthy" = 0
    "Hazardous" = 0
}

# Parse
foreach ($Line in $Lines) {
    # Match columns via regex or simple split, considering quotes in alerts
    # Structure: timestamp,temp,hum,gas,pm25,pm10,aqi,category,alert_triggered,alert_message,mode
    # Regex split to handle quotes in alert message
    $Cols = $Line -split ',(?=(?:[^"]*"[^"]*")*[^"]*$)'
    
    $Temp = [double]$Cols[1]
    $Hum = [double]$Cols[2]
    $Gas = [double]$Cols[3]
    $PM25 = [double]$Cols[4]
    $PM10 = [double]$Cols[5]
    $Aqi = [double]$Cols[6]
    $Category = $Cols[7].Replace('"', '')
    $AlertTriggered = $Cols[8]
    
    # Sum/Min/Max calculations
    $SumTemp += $Temp; if ($Temp -lt $MinTemp) { $MinTemp = $Temp }; if ($Temp -gt $MaxTemp) { $MaxTemp = $Temp }
    $SumHum += $Hum; if ($Hum -lt $MinHum) { $MinHum = $Hum }; if ($Hum -gt $MaxHum) { $MaxHum = $Hum }
    $SumGas += $Gas; if ($Gas -lt $MinGas) { $MinGas = $Gas }; if ($Gas -gt $MaxGas) { $MaxGas = $Gas }
    $SumPM25 += $PM25; if ($PM25 -lt $MinPM25) { $MinPM25 = $PM25 }; if ($PM25 -gt $MaxPM25) { $MaxPM25 = $PM25 }
    $SumPM10 += $PM10; if ($PM10 -lt $MinPM10) { $MinPM10 = $PM10 }; if ($PM10 -gt $MaxPM10) { $MaxPM10 = $PM10 }
    $SumAqi += $Aqi; if ($Aqi -lt $MinAqi) { $MinAqi = $Aqi }; if ($Aqi -gt $MaxAqi) { $MaxAqi = $Aqi }
    
    if ($AlertTriggered -eq "True") { $AlertsCount++ }
    
    if ($CatCounts.ContainsKey($Category)) {
        $CatCounts[$Category]++
    }
}

$AvgTemp = $SumTemp / $TotalRecords
$AvgHum = $SumHum / $TotalRecords
$AvgGas = $SumGas / $TotalRecords
$AvgPM25 = $SumPM25 / $TotalRecords
$AvgPM10 = $SumPM10 / $TotalRecords
$AvgAqi = $SumAqi / $TotalRecords

# Build text report
$ReportContent = @"
========================================================================
                 AIR QUALITY & POLLUTION ANALYTICAL REPORT             
========================================================================
Generated at:       $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
Monitoring Period:  $($Lines[0].Split(',')[0]) to $($Lines[-1].Split(',')[0])
Total Duration:     24 Hours (96 Intervals)
Data Logs Processed: $TotalRecords readings
Alerts Triggered:   $AlertsCount thresholds breached
------------------------------------------------------------------------

1. METRIC STATISTICS
---------------------
Metric               | Average      | Minimum      | Maximum      | Unit
------------------------------------------------------------------------
Temperature          | $($AvgTemp.ToString('F2'))        | $($MinTemp.ToString('F2'))        | $($MaxTemp.ToString('F2'))        | *C
Humidity             | $($AvgHum.ToString('F2'))        | $($MinHum.ToString('F2'))        | $($MaxHum.ToString('F2'))        | %
MQ135 Gas Raw        | $($AvgGas.ToString('F2'))        | $($MinGas.ToString('F2'))        | $($MaxGas.ToString('F2'))        | analog value
PM2.5                | $($AvgPM25.ToString('F2'))        | $($MinPM25.ToString('F2'))        | $($MaxPM25.ToString('F2'))        | ug/m3
PM10                 | $($AvgPM10.ToString('F2'))        | $($MinPM10.ToString('F2'))        | $($MaxPM10.ToString('F2'))        | ug/m3
AQI                  | $($AvgAqi.ToString('F2'))        | $($MinAqi.ToString('F2'))        | $($MaxAqi.ToString('F2'))        | index points

2. AQI CATEGORY DISTRIBUTION
-----------------------------
Category                         | Count    | Percentage
---------------------------------------------------------
Good                             | $($CatCounts["Good"])        | $([Math]::Round(($CatCounts["Good"]/$TotalRecords)*100, 1))%
Moderate                         | $($CatCounts["Moderate"])        | $([Math]::Round(($CatCounts["Moderate"]/$TotalRecords)*100, 1))%
Unhealthy for Sensitive Groups   | $($CatCounts["Unhealthy for Sensitive Groups"])        | $([Math]::Round(($CatCounts["Unhealthy for Sensitive Groups"]/$TotalRecords)*100, 1))%
Unhealthy                        | $($CatCounts["Unhealthy"])        | $([Math]::Round(($CatCounts["Unhealthy"]/$TotalRecords)*100, 1))%
Very Unhealthy                   | $($CatCounts["Very Unhealthy"])        | $([Math]::Round(($CatCounts["Very Unhealthy"]/$TotalRecords)*100, 1))%
Hazardous                        | $($CatCounts["Hazardous"])        | $([Math]::Round(($CatCounts["Hazardous"]/$TotalRecords)*100, 1))%

3. SYSTEM REMARKS & ACTIONS REQUIRED
------------------------------------
$(if ($AlertsCount -gt 0) {
"   [ALERT] The system registered $AlertsCount instances of excessive pollution.
   Recommendation: Review the timeline for correlation with peak industrial activity
   or traffic peaks. Deploy localized air purification systems or activate HVAC ventilation filters."
} else {
"   [NORMAL] Air quality remained within satisfactory bounds during the reporting period.
   No corrective actions required."
})
========================================================================
"@

Set-Content -Path $ReportFile -Value $ReportContent
Write-Host "[PS ANALYZER] Analytical report successfully compiled: $ReportFile"
