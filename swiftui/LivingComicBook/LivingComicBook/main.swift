import SwiftUI

struct Issue: Codable, Identifiable {
    let id: String
    let title: String
    let logline: String
    let panels: [Panel]
}

struct Panel: Codable, Identifiable {
    let id: String
    let page: Int
    let panel: Int
    let action: String
    let dialogue: [[String:String]]
    let visual_prompt: String
    let camera: String
    let image_path: String?
    let video_path: String?
    let audio_path: String?
}

@MainActor
final class ComicViewModel: ObservableObject {
    @Published var idea = "Calder, Thor, and the Huemon Trainer enter the living comic engine"
    @Published var issue: Issue?
    @Published var selectedPanel: Panel?
    @Published var isGenerating = false
    @Published var status = "Ready"
    let base = URL(string: "http://127.0.0.1:8766")!

    func generate() {
        isGenerating = true
        status = "Generating issue..."
        Task {
            do {
                var req = URLRequest(url: base.appendingPathComponent("/api/generate"))
                req.httpMethod = "POST"
                req.addValue("application/json", forHTTPHeaderField: "Content-Type")
                req.httpBody = try JSONSerialization.data(withJSONObject: ["idea": idea, "panel_count": 6, "style": "dark cinematic comic book, polished gutters, speech bubbles"])
                let (data, _) = try await URLSession.shared.data(for: req)
                let decoded = try JSONDecoder().decode(Issue.self, from: data)
                issue = decoded
                selectedPanel = decoded.panels.first
                status = "Generated \(decoded.panels.count) panels"
            } catch {
                status = "Error: \(error.localizedDescription)"
            }
            isGenerating = false
        }
    }
}

struct PanelCard: View {
    let panel: Panel
    let active: Bool
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            ZStack {
                RoundedRectangle(cornerRadius: 18).fill(LinearGradient(colors: [.black, Color(red:0.09, green:0.11, blue:0.18)], startPoint: .top, endPoint: .bottom))
                RoundedRectangle(cornerRadius: 18).stroke(active ? .yellow : .white.opacity(0.35), lineWidth: active ? 4 : 1)
                Text("Panel \(panel.panel)\n\(panel.action)").font(.headline).foregroundColor(.white).padding()
            }.frame(minHeight: active ? 260 : 180)
            ForEach(panel.dialogue.indices, id: \.self) { idx in
                let line = panel.dialogue[idx]
                Text("\(line["speaker"] ?? "?"): \(line["text"] ?? "")")
                    .padding(8).background(Color.white).foregroundColor(.black).clipShape(RoundedRectangle(cornerRadius: 12))
            }
            Text(panel.camera).font(.caption).foregroundStyle(.secondary)
        }.padding(10).background(Color(red:0.05, green:0.06, blue:0.09)).clipShape(RoundedRectangle(cornerRadius: 22))
    }
}

struct ContentView: View {
    @StateObject var vm = ComicViewModel()
    var body: some View {
        NavigationSplitView {
            VStack(alignment: .leading) {
                Text("Living Comic Book").font(.largeTitle.bold())
                TextEditor(text: $vm.idea).frame(height: 120).border(.gray.opacity(0.3))
                Button(vm.isGenerating ? "Generating..." : "Generate Full Issue") { vm.generate() }.keyboardShortcut("g")
                Text(vm.status).foregroundStyle(.secondary)
                Spacer()
            }.padding().frame(minWidth: 320)
        } detail: {
            ScrollViewReader { proxy in
                ScrollView {
                    LazyVGrid(columns: [GridItem(.adaptive(minimum: 340), spacing: 22)], spacing: 22) {
                        ForEach(vm.issue?.panels ?? []) { panel in
                            PanelCard(panel: panel, active: vm.selectedPanel?.id == panel.id)
                                .id(panel.id)
                                .onTapGesture { withAnimation(.spring()) { vm.selectedPanel = panel; proxy.scrollTo(panel.id, anchor: .center) } }
                        }
                    }.padding(30)
                }.background(Color(red:0.025, green:0.027, blue:0.04))
            }
        }.frame(minWidth: 1100, minHeight: 760)
    }
}

@main
struct LivingComicBookApp: App {
    var body: some Scene { WindowGroup { ContentView() } }
}
