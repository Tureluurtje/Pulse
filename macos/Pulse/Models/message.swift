//
//  message.swift
//  Pulse
//
//  Created by Arthur Kwak on 9/2/25.
//

import Foundation
import SwiftUI

// Chat for sidebar
struct Chat: Identifiable, Hashable {
    let id: UUID
    let name: String
    let lastMessage: String
    let time: String
    let profileColor: Color
}

// Message for chat panel
struct Message: Identifiable, Encodable, Decodable, Hashable {
    let id: UUID
    let text: String
    let sender: String
    let timestamp: Date
}
