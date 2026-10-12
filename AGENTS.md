# Development

The Firefox extension starts `server.sh`, which replaces itself with the Go native messaging server. Its parent process identifies the connected browser.

Use the connected browser's absolute application bundle path for activation. Do not fall back to a browser name or the system default browser when identification fails.

Build with `CGO_ENABLED=0 go build .`. For `go test ./...`, set `alfred_workflow_version=0.0.0`, `alfred_workflow_bundleid`, `alfred_workflow_cache` and `alfred_workflow_data` to test values and temporary directories: awgo validates these during package initialisation. The release script also signs, notarises and optionally publishes; do not use it for a local test build.

After replacing the installed executable, restart the browser or reconnect the extension so the native messaging server uses the new build and RPC interface.
