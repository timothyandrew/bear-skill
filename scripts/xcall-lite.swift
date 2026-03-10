import Cocoa

class AppDelegate: NSObject, NSApplicationDelegate {
    var expectingResponse = true

    func applicationDidFinishLaunching(_ notification: Notification) {
        // Register URL scheme handler
        NSAppleEventManager.shared().setEventHandler(
            self,
            andSelector: #selector(handleURL(event:reply:)),
            forEventClass: AEEventClass(kInternetEventClass),
            andEventID: AEEventID(kAEGetURL)
        )

        // Parse CLI args
        let args = CommandLine.arguments
        guard args.count >= 2 else {
            fputs("Usage: xcall-lite <bear-url>\n", stderr)
            NSApp.terminate(nil)
            return
        }

        var urlString = args[1]

        // Append x-success and x-error callback params
        let separator = urlString.contains("?") ? "&" : "?"
        let successCB = "xcall-lite-callback://success"
        let errorCB = "xcall-lite-callback://error"
        urlString += "\(separator)x-success=\(successCB.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed)!)&x-error=\(errorCB.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed)!)"

        guard let url = URL(string: urlString) else {
            fputs("Invalid URL: \(urlString)\n", stderr)
            exit(1)
        }

        // Open the Bear URL
        NSWorkspace.shared.open(url)

        // Timeout after 30 seconds
        DispatchQueue.main.asyncAfter(deadline: .now() + 30) {
            if self.expectingResponse {
                fputs("Timeout waiting for callback\n", stderr)
                exit(1)
            }
        }
    }

    @objc func handleURL(event: NSAppleEventDescriptor, reply: NSAppleEventDescriptor) {
        expectingResponse = false
        guard let urlString = event.paramDescriptor(forKeyword: AEKeyword(keyDirectObject))?.stringValue,
              let url = URL(string: urlString),
              let components = URLComponents(url: url, resolvingAgainstBaseURL: false) else {
            fputs("Failed to parse callback URL\n", stderr)
            exit(1)
        }

        let isError = url.host == "error"

        // Build JSON from query parameters
        var result: [String: String] = [:]
        if let items = components.queryItems {
            for item in items {
                if let value = item.value {
                    result[item.name] = value
                }
            }
        }

        // Output JSON
        if let jsonData = try? JSONSerialization.data(withJSONObject: result, options: [.prettyPrinted, .sortedKeys]),
           let jsonString = String(data: jsonData, encoding: .utf8) {
            print(jsonString)
        } else {
            print("{}")
        }

        exit(isError ? 1 : 0)
    }
}

let app = NSApplication.shared
let delegate = AppDelegate()
app.delegate = delegate
app.run()
