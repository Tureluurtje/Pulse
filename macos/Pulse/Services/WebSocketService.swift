//
//  WebSocketService.swift
//  Pulse
//
//  Created by Arthur Kwak on 9/2/25.
//

import Foundation

class WebSocketService {
    private var webSocketTask: URLSessionWebSocketTask?
    private weak var viewModel: ChatViewModel?

    init(viewModel: ChatViewModel) {
        self.viewModel = viewModel
    }

    func connect() {
        let url = URL(string: "ws://localhost:5000/socket")!
        webSocketTask = URLSession.shared.webSocketTask(with: url)
        webSocketTask?.resume()
        receive()
    }

    func send(message: Message) {
        guard let json = try? JSONEncoder().encode(message),
              let string = String(data: json, encoding: .utf8) else { return }
        webSocketTask?.send(.string(string)) { error in
            if let error = error { print(error) }
        }
    }

    private func receive() {
        webSocketTask?.receive { [weak self] result in
            switch result {
            case .failure(let error): print(error)
            case .success(let message):
                if case let .string(text) = message,
                   let data = text.data(using: .utf8),
                   let newMessage = try? JSONDecoder().decode(Message.self, from: data) {
                    DispatchQueue.main.async {
                        self?.viewModel?.messages.append(newMessage)
                    }
                }
                self?.receive() // keep listening
            }
        }
    }
    
    func disconnect() {
        webSocketTask?.cancel()
    }
}
