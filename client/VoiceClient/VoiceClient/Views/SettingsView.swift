import SwiftUI

/// Settings view for the application.
struct SettingsView: View {
    @EnvironmentObject var appState: AppState
    @StateObject private var settings = AppSettings.shared

    var body: some View {
        TabView {
            GeneralSettingsView()
                .environmentObject(settings)
                .tabItem {
                    Label("General", systemImage: "gear")
                }

            HotkeySettingsView()
                .environmentObject(settings)
                .tabItem {
                    Label("Hotkey", systemImage: "keyboard")
                }

            DictionarySettingsView()
                .tabItem {
                    Label("Dictionary", systemImage: "text.book.closed")
                }

            AboutView()
                .tabItem {
                    Label("About", systemImage: "info.circle")
                }
        }
        .frame(width: 480, height: 320)
    }
}

// MARK: - General Settings Tab

/// General settings tab.
struct GeneralSettingsView: View {
    @EnvironmentObject var settings: AppSettings
    @State private var connectionStatus: ConnectionStatus = .unknown
    @State private var isTestingConnection = false

    enum ConnectionStatus {
        case unknown
        case testing
        case connected
        case failed(String)

        var icon: String {
            switch self {
            case .unknown: return "circle"
            case .testing: return "arrow.triangle.2.circlepath"
            case .connected: return "checkmark.circle.fill"
            case .failed: return "xmark.circle.fill"
            }
        }

        var color: Color {
            switch self {
            case .unknown: return .secondary
            case .testing: return .orange
            case .connected: return .green
            case .failed: return .red
            }
        }
    }

    var body: some View {
        Form {
            // Server settings
            Section {
                HStack {
                    TextField("Server URL", text: $settings.serverURL)
                        .textFieldStyle(.roundedBorder)

                    // Validation indicator
                    Image(systemName: settings.isServerURLValid ? "checkmark.circle" : "xmark.circle")
                        .foregroundColor(settings.isServerURLValid ? .green : .red)
                }

                HStack {
                    // Connection status
                    HStack(spacing: 4) {
                        Image(systemName: connectionStatus.icon)
                            .foregroundColor(connectionStatus.color)
                        Text(connectionStatusText)
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }

                    Spacer()

                    // Test connection button
                    Button("Test Connection") {
                        testConnection()
                    }
                    .disabled(isTestingConnection || !settings.isServerURLValid)
                }
            } header: {
                Text("Server")
            }

            // Startup settings
            Section {
                Toggle("Launch at Login", isOn: $settings.launchAtLogin)
                    .toggleStyle(.switch)
            } header: {
                Text("Startup")
            }

            // Reset settings
            Section {
                Button("Reset to Defaults") {
                    settings.resetToDefaults()
                    connectionStatus = .unknown
                }
                .foregroundColor(.red)
            }
        }
        .formStyle(.grouped)
        .padding()
    }

    private var connectionStatusText: String {
        switch connectionStatus {
        case .unknown:
            return "Not tested"
        case .testing:
            return "Testing..."
        case .connected:
            return "Connected"
        case .failed(let message):
            return "Failed: \(message)"
        }
    }

    private func testConnection() {
        guard let url = URL(string: settings.serverURL)?.appendingPathComponent("api/status") else {
            connectionStatus = .failed("Invalid URL")
            return
        }

        isTestingConnection = true
        connectionStatus = .testing

        Task {
            do {
                let (_, response) = try await URLSession.shared.data(from: url)
                if let httpResponse = response as? HTTPURLResponse,
                   httpResponse.statusCode == 200 {
                    connectionStatus = .connected
                } else {
                    connectionStatus = .failed("Server error")
                }
            } catch {
                connectionStatus = .failed(error.localizedDescription)
            }
            isTestingConnection = false
        }
    }
}

// MARK: - Hotkey Settings Tab

/// Hotkey settings tab.
struct HotkeySettingsView: View {
    @EnvironmentObject var settings: AppSettings
    @State private var isRecordingHotkey = false
    @State private var showHotkeyHelp = false

    var body: some View {
        Form {
            Section {
                VStack(alignment: .leading, spacing: 12) {
                    Text("Current Hotkey")
                        .font(.headline)

                    HStack {
                        // Current hotkey display
                        Text(settings.hotkeyDisplayString)
                            .font(.system(size: 24, weight: .medium, design: .rounded))
                            .padding(.horizontal, 16)
                            .padding(.vertical, 8)
                            .background(Color.accentColor.opacity(0.15))
                            .cornerRadius(8)

                        Spacer()

                        // Record new hotkey button
                        Button(isRecordingHotkey ? "Press keys..." : "Change Hotkey") {
                            isRecordingHotkey.toggle()
                        }
                        .buttonStyle(.borderedProminent)
                    }

                    if isRecordingHotkey {
                        Text("Press the key combination you want to use, then click Done")
                            .font(.caption)
                            .foregroundColor(.orange)

                        HStack {
                            // Modifier checkboxes
                            ModifierToggle(label: "⌘", isOn: .constant(true))
                            ModifierToggle(label: "⇧", isOn: .constant(true))
                            ModifierToggle(label: "⌃", isOn: .constant(false))
                            ModifierToggle(label: "⌥", isOn: .constant(false))

                            Spacer()

                            Button("Done") {
                                isRecordingHotkey = false
                            }
                        }
                    }

                    Text("Hold this key combination to start recording, release to stop and transcribe.")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            } header: {
                Text("Voice Recording Hotkey")
            }

            Section {
                VStack(alignment: .leading, spacing: 8) {
                    Label("The hotkey works globally across all applications", systemImage: "globe")
                    Label("Hold to record, release to transcribe", systemImage: "hand.tap")
                    Label("Recording stops automatically after 60 seconds", systemImage: "timer")
                }
                .font(.caption)
                .foregroundColor(.secondary)
            } header: {
                Text("How it works")
            }

            Section {
                Button("Reset to Default (⌘⇧V)") {
                    settings.hotkeyModifiers = 0x180000
                    settings.hotkeyKeyCode = 9
                }
            }
        }
        .formStyle(.grouped)
        .padding()
    }
}

/// Modifier key toggle button.
struct ModifierToggle: View {
    let label: String
    @Binding var isOn: Bool

    var body: some View {
        Button {
            isOn.toggle()
        } label: {
            Text(label)
                .font(.system(size: 16, weight: .medium))
                .frame(width: 32, height: 32)
                .background(isOn ? Color.accentColor : Color.secondary.opacity(0.2))
                .foregroundColor(isOn ? .white : .primary)
                .cornerRadius(6)
        }
        .buttonStyle(.plain)
    }
}

// MARK: - Dictionary Settings Tab

/// Dictionary settings tab (placeholder for Task 4.3.1).
struct DictionarySettingsView: View {
    @State private var entries: [DictionaryEntry] = []
    @State private var newPattern = ""
    @State private var newReplacement = ""
    @State private var isLoading = false
    @State private var errorMessage: String?

    struct DictionaryEntry: Identifiable {
        let id: Int
        let pattern: String
        let replacement: String
    }

    var body: some View {
        VStack(spacing: 0) {
            // Header
            HStack {
                Text("Personal Dictionary")
                    .font(.headline)
                Spacer()
                Text("\(entries.count)/100")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            .padding()

            Divider()

            // Entry list
            if entries.isEmpty {
                VStack(spacing: 8) {
                    Image(systemName: "text.book.closed")
                        .font(.largeTitle)
                        .foregroundColor(.secondary)
                    Text("No dictionary entries")
                        .foregroundColor(.secondary)
                    Text("Add patterns to customize transcription")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else {
                List {
                    ForEach(entries) { entry in
                        HStack {
                            VStack(alignment: .leading) {
                                Text(entry.pattern)
                                    .font(.body)
                                Text("→ \(entry.replacement)")
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                            }
                            Spacer()
                            Button {
                                deleteEntry(entry)
                            } label: {
                                Image(systemName: "trash")
                                    .foregroundColor(.red)
                            }
                            .buttonStyle(.plain)
                        }
                    }
                }
            }

            Divider()

            // Add new entry
            VStack(spacing: 8) {
                HStack {
                    TextField("Pattern", text: $newPattern)
                        .textFieldStyle(.roundedBorder)
                    Text("→")
                    TextField("Replacement", text: $newReplacement)
                        .textFieldStyle(.roundedBorder)
                    Button("Add") {
                        addEntry()
                    }
                    .disabled(newPattern.isEmpty || newReplacement.isEmpty || entries.count >= 100)
                }

                if let error = errorMessage {
                    Text(error)
                        .font(.caption)
                        .foregroundColor(.red)
                }
            }
            .padding()
        }
        .onAppear {
            loadEntries()
        }
    }

    private func loadEntries() {
        // TODO: Load from API (Task 4.3.1)
        isLoading = true
        // Simulated data for now
        entries = []
        isLoading = false
    }

    private func addEntry() {
        // TODO: Add via API (Task 4.3.1)
        guard !newPattern.isEmpty, !newReplacement.isEmpty else { return }
        let newEntry = DictionaryEntry(
            id: entries.count + 1,
            pattern: newPattern,
            replacement: newReplacement
        )
        entries.append(newEntry)
        newPattern = ""
        newReplacement = ""
    }

    private func deleteEntry(_ entry: DictionaryEntry) {
        // TODO: Delete via API (Task 4.3.1)
        entries.removeAll { $0.id == entry.id }
    }
}

// MARK: - About Tab

/// About tab.
struct AboutView: View {
    var body: some View {
        VStack(spacing: 16) {
            Spacer()

            Image(systemName: "mic.circle.fill")
                .font(.system(size: 64))
                .foregroundColor(.accentColor)

            Text("VoiceClient")
                .font(.title)
                .fontWeight(.bold)

            Text("Version 1.0.0")
                .foregroundColor(.secondary)

            Text("Voice-to-text client for KumaKuma AI")
                .font(.caption)
                .foregroundColor(.secondary)

            Spacer()

            HStack(spacing: 16) {
                Link("GitHub", destination: URL(string: "https://github.com")!)
                Text("•")
                    .foregroundColor(.secondary)
                Link("Documentation", destination: URL(string: "https://github.com")!)
            }
            .font(.caption)

            Text("© 2025 KumaKuma AI")
                .font(.caption2)
                .foregroundColor(.secondary)

            Spacer()
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .padding()
    }
}

// MARK: - Preview

#if DEBUG
struct SettingsView_Previews: PreviewProvider {
    static var previews: some View {
        SettingsView()
            .environmentObject(AppState())
    }
}
#endif
