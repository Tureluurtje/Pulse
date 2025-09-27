//
//  MessageRow.swift
//  Pulse
//
//  Created by Arthur Kwak on 9/2/25.
//

import SwiftUI

struct MessageRow: View {
    let message: Message

    var body: some View {
        HStack {
            if message.sender == "Me" {
                Spacer()
                Text(message.text)
                    .padding()
                    .background(Color.blue)
                    .foregroundColor(.white)
                    .cornerRadius(12)
            } else {
                Text(message.text)
                    .padding()
                    .background(Color.gray.opacity(0.3))
                    .foregroundColor(.black)
                    .cornerRadius(12)
                Spacer()
            }
        }
        .padding(.horizontal)
    }
}

struct MessageRow_Previews: PreviewProvider {
    static var previews: some View {
        MessageRow(message: Message(id: UUID(), text: "Hello!", sender: "Alice", timestamp: Date()))
            .previewLayout(.sizeThatFits)
    }
}
