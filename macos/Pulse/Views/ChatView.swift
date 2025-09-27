//
//  ChatView.swift
//  Pulse
//
//  Created by Arthur Kwak on 9/2/25.
//

import SwiftUI

struct ChatView: View {
    @EnvironmentObject var viewModel: ChatViewModel
    @State private var typedMessage: String = ""

    var body: some View {
        VStack {
            ScrollView {
                LazyVStack(spacing: 8) {
                    ForEach(viewModel.messages) { message in
                        MessageRow(message: message)
                    }
                }
            }
            
            HStack {
                TextField("Type a message", text: $typedMessage)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                Button("Send") {
                    viewModel.send(message: typedMessage, sender: "Me")
                    typedMessage = ""
                }
                .padding(.horizontal)
                .background(Color.blue)
                .foregroundColor(.white)
                .cornerRadius(8)
            }
            .padding()
        }
        .padding()
    }
}

struct ChatView_Previews: PreviewProvider {
    static var previews: some View {
        ChatView()
            .environmentObject(ChatViewModel())
    }
}

