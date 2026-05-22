import AVKit
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
    @Published var panelCount = 1
    let base = URL(string: ProcessInfo.processInfo.environment["LIVING_COMIC_BACKEND_URL"] ?? "http://127.0.0.1:8776")!
    let session: URLSession = {
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 3600
        config.timeoutIntervalForResource = 3600
        return URLSession(configuration: config)
    }()

    func assetURL(_ relative: String?) -> URL? {
        guard let relative, !relative.isEmpty else { return nil }
        let components = relative.split(separator: "/").map(String.init)
        var url = base.appendingPathComponent("assets")
        for component in components { url.appendPathComponent(component) }
        return url
    }

    func generate() {
        isGenerating = true
        status = panelCount == 1 ? "Generating 1 real LTX panel..." : "Generating \(panelCount) real LTX panels; this can take a while..."
        Task {
            do {
                var req = URLRequest(url: base.appendingPathComponent("/api/generate"))
                req.httpMethod = "POST"
                req.addValue("application/json", forHTTPHeaderField: "Content-Type")
                req.httpBody = try JSONSerialization.data(withJSONObject: ["idea": idea, "panel_count": panelCount, "style": "dark cinematic comic book, polished gutters, speech bubbles"])
                let (data, response) = try await session.data(for: req)
                guard let http = response as? HTTPURLResponse else {
                    throw NSError(domain: "LivingComic", code: -1, userInfo: [NSLocalizedDescriptionKey: "No HTTP response from backend"])
                }
                guard (200..<300).contains(http.statusCode) else {
                    let body = String(data: data, encoding: .utf8) ?? "<unreadable body>"
                    throw NSError(domain: "LivingComic", code: http.statusCode, userInfo: [NSLocalizedDescriptionKey: "Backend HTTP \(http.statusCode): \(body)"])
                }
                do {
                    let decoded = try JSONDecoder().decode(Issue.self, from: data)
                    issue = decoded
                    selectedPanel = decoded.panels.first
                    status = "Generated \(decoded.panels.count) panel asset set\(decoded.panels.count == 1 ? "" : "s")"
                } catch {
                    let body = String(data: data, encoding: .utf8) ?? "<unreadable body>"
                    throw NSError(domain: "LivingComic", code: -2, userInfo: [NSLocalizedDescriptionKey: "Could not decode Issue JSON: \(error.localizedDescription). Body: \(body.prefix(800))"])
                }
            } catch {
                status = "Error: \(error.localizedDescription)"
            }
            isGenerating = false
        }
    }
}

struct AutoVideoPlayer: View {
    let url: URL
    @State private var player: AVPlayer?

    var body: some View {
        VideoPlayer(player: player)
            .onAppear {
                let p = AVPlayer(url: url)
                p.actionAtItemEnd = .none
                player = p
                NotificationCenter.default.addObserver(forName: .AVPlayerItemDidPlayToEndTime, object: p.currentItem, queue: .main) { _ in
                    p.seek(to: .zero)
                    p.play()
                }
                p.play()
            }
            .onDisappear {
                player?.pause()
                player = nil
            }
    }
}

struct PanelCard: View {
    let panel: Panel
    let active: Bool
    let imageURL: URL?
    let videoURL: URL?

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            ZStack(alignment: .bottomLeading) {
                RoundedRectangle(cornerRadius: 18)
                    .fill(LinearGradient(colors: [.black, Color(red:0.09, green:0.11, blue:0.18)], startPoint: .top, endPoint: .bottom))

                if active, let videoURL, videoURL.pathExtension.lowercased() == "mp4" {
                    AutoVideoPlayer(url: videoURL)
                        .clipShape(RoundedRectangle(cornerRadius: 18))
                        .overlay(Color.black.opacity(0.08))
                } else if let imageURL {
                    AsyncImage(url: imageURL) { phase in
                        switch phase {
                        case .empty:
                            ProgressView().controlSize(.large)
                        case .success(let image):
                            image.resizable().scaledToFill()
                        case .failure:
                            fallbackPanel
                        @unknown default:
                            fallbackPanel
                        }
                    }
                    .clipShape(RoundedRectangle(cornerRadius: 18))
                } else {
                    fallbackPanel
                }

                RoundedRectangle(cornerRadius: 18)
                    .stroke(active ? .yellow : .white.opacity(0.35), lineWidth: active ? 4 : 1)

                VStack(alignment: .leading, spacing: 4) {
                    Text("Panel \(panel.panel)")
                        .font(.caption.bold())
                        .padding(.horizontal, 9)
                        .padding(.vertical, 5)
                        .background(active ? Color.yellow : Color.black.opacity(0.7))
                        .foregroundColor(active ? .black : .white)
                        .clipShape(Capsule())
                    if active {
                        Text("LTX motion layer")
                            .font(.caption2)
                            .padding(.horizontal, 8)
                            .padding(.vertical, 4)
                            .background(Color.black.opacity(0.65))
                            .foregroundColor(.white)
                            .clipShape(Capsule())
                    }
                }.padding(12)
            }
            .frame(minHeight: active ? 360 : 230)
            .clipped()

            VStack(alignment: .leading, spacing: 7) {
                Text(panel.action)
                    .font(.subheadline.weight(.semibold))
                    .foregroundColor(.white)
                ForEach(panel.dialogue.indices, id: \.self) { idx in
                    let line = panel.dialogue[idx]
                    Text("\(line["speaker"] ?? "?"): \(line["text"] ?? "")")
                        .padding(8)
                        .background(Color.white)
                        .foregroundColor(.black)
                        .clipShape(RoundedRectangle(cornerRadius: 12))
                }
                Text(panel.camera).font(.caption).foregroundStyle(.secondary)
            }
        }
        .padding(10)
        .background(Color(red:0.05, green:0.06, blue:0.09))
        .clipShape(RoundedRectangle(cornerRadius: 22))
        .shadow(color: active ? .yellow.opacity(0.25) : .black.opacity(0.3), radius: active ? 20 : 8)
    }

    var fallbackPanel: some View {
        VStack(spacing: 12) {
            Image(systemName: "photo.on.rectangle.angled")
                .font(.system(size: 42))
            Text("Panel \(panel.panel)")
                .font(.headline)
            Text(panel.visual_prompt)
                .font(.caption)
                .multilineTextAlignment(.center)
                .padding(.horizontal)
        }
        .foregroundColor(.white.opacity(0.85))
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}

struct ContentView: View {
    @StateObject var vm = ComicViewModel()
    var body: some View {
        NavigationSplitView {
            VStack(alignment: .leading) {
                Text("Living Comic Book").font(.largeTitle.bold())
                TextEditor(text: $vm.idea).frame(height: 120).border(.gray.opacity(0.3))
                Stepper("Panels: \(vm.panelCount)", value: $vm.panelCount, in: 1...12)
                    .disabled(vm.isGenerating)
                Text("Tip: real Hapa-LTX panels are slow. Start with 1 panel, then raise this for longer runs.")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                Button(vm.isGenerating ? "Generating..." : (vm.panelCount == 1 ? "Generate Preview Panel" : "Generate Issue")) { vm.generate() }.keyboardShortcut("g")
                Text(vm.status).foregroundStyle(.secondary)
                if let issue = vm.issue {
                    Divider().padding(.vertical, 8)
                    Text(issue.title).font(.headline)
                    Text(issue.logline).font(.caption).foregroundStyle(.secondary)
                    Text("Click a panel to play its LTX motion layer.").font(.caption).foregroundStyle(.secondary)
                }
                Spacer()
            }.padding().frame(minWidth: 320)
        } detail: {
            ScrollViewReader { proxy in
                ScrollView {
                    LazyVGrid(columns: [GridItem(.adaptive(minimum: 420), spacing: 24)], spacing: 24) {
                        ForEach(vm.issue?.panels ?? []) { panel in
                            PanelCard(
                                panel: panel,
                                active: vm.selectedPanel?.id == panel.id,
                                imageURL: vm.assetURL(panel.image_path),
                                videoURL: vm.assetURL(panel.video_path)
                            )
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
