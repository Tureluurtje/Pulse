//
//  SidebarView.swift
//  Pulse
//
//  Created by Arthur Kwak on 9/2/25.
//

import SwiftUI

struct SidebarView: View {
    @State private var chats: [Chat] = [
        Chat(id: UUID(), name: "Alice", lastMessage: "Hey! How are you?", time: "12:45", profileColor: .blue),
        Chat(id: UUID(), name: "Bob", lastMessage: "Let's meet tomorrow.", time: "11:30", profileColor: .green),
        Chat(id: UUID(), name: "Charlie", lastMessage: "Thanks for the info.", time: "09:15", profileColor: .orange),
        Chat(id: UUID(), name: "Dana", lastMessage: "See you soon!", time: "Yesterday", profileColor: .purple)
    ]
    
    @State private var selectedChat: Chat?

    var body: some View {
        VStack(alignment: .leading) {
            Text("Chats")
                .font(.largeTitle)
                .bold()
                .padding(.horizontal)
                .padding(.top)
            
            ScrollView {
                LazyVStack(alignment: .leading, spacing: 0) {
                    ForEach(chats) { chat in
                        ChatRow(chat: chat, isSelected: chat.id == selectedChat?.id)
                            .onTapGesture { selectedChat = chat }
                    }
                }
            }
        }
        .frame(minWidth: 250, maxWidth: 300)
        .background(Color(NSColor.windowBackgroundColor))
    }
}

struct ChatRow: View {
    let chat: Chat
    let isSelected: Bool

    var body: some View {
        HStack(spacing: 12) {
            Circle()
                .fill(chat.profileColor)
                .frame(width: 50, height: 50)
                .overlay(Text(chat.name.prefix(1)).foregroundColor(.white))
            
            VStack(alignment: .leading, spacing: 4) {
                Text(chat.name)
                    .font(.headline)
                    .foregroundColor(.primary)
                Text(chat.lastMessage)
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                    .lineLimit(1)
            }
            
            Spacer()
            
            Text(chat.time)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .padding(.vertical, 8)
        .padding(.horizontal)
        .background(isSelected ? Color.blue.opacity(0.2) : Color.clear)
    }
}

struct SidebarView_Previews: PreviewProvider {
    static var previews: some View {
        SidebarView()
            .frame(width: 300)
    }
}
