# PowerShell Local Web Server using .NET HttpListener
# Hosts the dashboard HTML page on http://localhost:8080

$port = 8080
$url = "http://localhost:$port/"
$htmlPath = "dashboard/index.html"

$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add($url)

try {
    $listener.Start()
    Write-Host "[WEBSERVER] Local host dashboard server successfully started!"
    Write-Host "[WEBSERVER] Serving page at: $url"
    Write-Host "[WEBSERVER] Press Ctrl+C in this terminal to stop the server."
    
    while ($listener.IsListening) {
        try {
            $context = $listener.GetContext()
            $request = $context.Request
            $response = $context.Response
            
            # Read index.html
            if (Test-Path $htmlPath) {
                $html = Get-Content -Raw -Encoding UTF8 -Path $htmlPath
                $buffer = [System.Text.Encoding]::UTF8.GetBytes($html)
                
                $response.StatusCode = 200
                $response.ContentType = "text/html; charset=utf-8"
                $response.ContentLength64 = $buffer.Length
                $response.OutputStream.Write($buffer, 0, $buffer.Length)
            } else {
                $errText = "Error: dashboard/index.html file not found in workspace."
                $buffer = [System.Text.Encoding]::UTF8.GetBytes($errText)
                $response.StatusCode = 404
                $response.ContentLength64 = $buffer.Length
                $response.OutputStream.Write($buffer, 0, $buffer.Length)
            }
            
            $response.OutputStream.Close()
        } catch {
            # Handle request-specific exceptions silently to keep server running
        }
    }
} catch {
    Write-Host "[ERROR] Could not start server: $_"
} finally {
    if ($listener) {
        $listener.Close()
    }
}
