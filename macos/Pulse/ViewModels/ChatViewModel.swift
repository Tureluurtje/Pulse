//
//  ChatViewModel.swift
//  Pulse
//
//  Created by Arthur Kwak on 9/2/25.
//

import Foundation
import Combine

class ChatViewModel: ObservableObject {
    @Published var messages: [Message] = []
    
    // private var webSocketService: WebSocketService?  // WebSocket service (not used yet)
    
    init() {
        // Only add dummy messages for now, no WebSocket
        messages = [
            Message(id: UUID(), text: "Hello!", sender: "Alice", timestamp: Date()),
            Message(id: UUID(), text: "Hi there!", sender: "Me", timestamp: Date()),
            Message(id: UUID(), text: "This is a dummy message.", sender: "Alice", timestamp: Date())
        ]
        
        /*
        // Uncomment this when you have a Flask WebSocket server
        webSocketService = WebSocketService(viewModel: self)
        webSocketService?.connect()
        */
    }
    
    func send(message: String, sender: String) {
        let newMessage = Message(id: UUID(), text: message, sender: sender, timestamp: Date())
        messages.append(newMessage)
        
        /*
        // Uncomment this when WebSocket is ready
        webSocketService?.send(message: newMessage)
        */
    }
}
