//
//  ContentView.swift
//  Pulse
//
//  Created by Arthur Kwak on 9/2/25.
//

import SwiftUI

struct ContentView: View {
    @StateObject var viewModel = ChatViewModel()
    
    var body: some View {
        NavigationView {
            SidebarView()
            ChatView()
                .environmentObject(viewModel)
        }
    }
}

