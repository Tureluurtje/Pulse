import { useState } from 'react';
import { Send, MoreVertical, Search, Check, CheckCheck } from 'lucide-react';
import { Chat, Message } from '../App';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuSeparator } from './ui/dropdown-menu';
import { Dialog, DialogContent, DialogTitle, DialogDescription } from './ui/dialog';
import { Profile } from './Profile';

interface ChatWindowProps {
  chat?: Chat;
  messages: Message[];
  onBlockChat: (chatId: string) => void;
  onMuteChat: (chatId: string) => void;
  compactMode: boolean;
}

export function ChatWindow({ chat, messages, onBlockChat, onMuteChat, compactMode }: ChatWindowProps) {
  const [messageText, setMessageText] = useState('');
  const [showAvatarDialog, setShowAvatarDialog] = useState(false);
  const [showProfile, setShowProfile] = useState(false);
  const [showSearch, setShowSearch] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (messageText.trim()) {
      // In a real app, this would send the message
      setMessageText('');
    }
  };

  const handleClearHistory = () => {
    // In a real app, this would clear the chat history
    console.log('Clearing chat history');
  };

  if (!chat) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-emerald-100 dark:bg-emerald-900 flex items-center justify-center">
            <span className="text-3xl">💬</span>
          </div>
          <h2 className="text-gray-600 dark:text-gray-400 mb-2">Welcome to Pulse</h2>
          <p className="text-sm text-gray-400 dark:text-gray-500">Select a chat to start messaging</p>
        </div>
      </div>
    );
  }

  if (showProfile) {
    return (
      <Profile
        chat={chat}
        onClose={() => setShowProfile(false)}
        onBlock={() => {
          onBlockChat(chat.id);
          setShowProfile(false);
        }}
        onMute={() => {
          onMuteChat(chat.id);
        }}
      />
    );
  }

  const padding = compactMode ? 'p-3' : 'p-6';
  const spacing = compactMode ? 'space-y-2' : 'space-y-4';
  const headerPadding = compactMode ? 'px-4 py-2' : 'px-6 py-4';

  return (
    <div className="flex-1 flex flex-col bg-white dark:bg-gray-900">
      {/* Chat Header */}
      <div className={`${headerPadding} border-b border-gray-200 dark:border-gray-800 flex items-center justify-between bg-white dark:bg-gray-900`}>
        <div className="flex items-center gap-3">
          <div className="relative cursor-pointer" onClick={() => setShowAvatarDialog(true)}>
            <div className={`${compactMode ? 'w-8 h-8 text-sm' : 'w-10 h-10'} rounded-full bg-gradient-to-br from-emerald-400 to-teal-400 flex items-center justify-center text-white`}>
              {chat.avatar}
            </div>
            {chat.online && (
              <div className={`absolute bottom-0 right-0 ${compactMode ? 'w-2 h-2' : 'w-3 h-3'} bg-emerald-400 rounded-full border-2 border-white dark:border-gray-900`}></div>
            )}
          </div>
          <div className="cursor-pointer" onClick={() => setShowProfile(true)}>
            <h2 className="text-gray-900 dark:text-gray-100">{chat.name}</h2>
            <p className="text-xs text-gray-500 dark:text-gray-400">{chat.online ? 'Online' : 'Offline'}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button 
            size="icon" 
            variant="ghost" 
            className="h-9 w-9 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800"
            onClick={() => setShowSearch(!showSearch)}
          >
            <Search className="h-4 w-4 text-gray-600 dark:text-gray-400" />
          </Button>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button size="icon" variant="ghost" className="h-9 w-9 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800">
                <MoreVertical className="h-4 w-4 text-gray-600 dark:text-gray-400" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-48">
              <DropdownMenuItem className="cursor-pointer" onClick={() => setShowProfile(true)}>
                View Profile
              </DropdownMenuItem>
              <DropdownMenuItem className="cursor-pointer" onClick={() => onMuteChat(chat.id)}>
                {chat.muted ? 'Unmute Notifications' : 'Mute Notifications'}
              </DropdownMenuItem>
              <DropdownMenuItem className="cursor-pointer" onClick={() => setShowSearch(!showSearch)}>
                Search Messages
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem className="cursor-pointer" onClick={handleClearHistory}>
                Clear History
              </DropdownMenuItem>
              <DropdownMenuItem 
                className="cursor-pointer text-red-600 dark:text-red-500"
                onClick={() => onBlockChat(chat.id)}
              >
                {chat.blocked ? 'Unblock Contact' : 'Block Contact'}
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      {/* Search Bar */}
      {showSearch && (
        <div className="px-6 py-3 border-b border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-800">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Search in conversation..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9 bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-700 focus-visible:ring-1 focus-visible:ring-emerald-200"
            />
          </div>
        </div>
      )}

      {/* Avatar Dialog */}
      <Dialog open={showAvatarDialog} onOpenChange={setShowAvatarDialog}>
        <DialogContent className="sm:max-w-md dark:bg-gray-900 dark:border-gray-800">
          <DialogTitle className="sr-only">Profile Picture</DialogTitle>
          <DialogDescription className="sr-only">
            View enlarged profile picture for {chat.name}
          </DialogDescription>
          <div className="flex flex-col items-center gap-4 py-4">
            <div className="w-48 h-48 rounded-full bg-gradient-to-br from-emerald-400 to-teal-400 flex items-center justify-center text-white text-6xl">
              {chat.avatar}
            </div>
            <div className="text-center">
              <h3 className="text-gray-900 dark:text-gray-100 mb-1">{chat.name}</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">{chat.online ? 'Online' : 'Offline'}</p>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Messages or Blocked View */}
      {chat.blocked ? (
        <div className="flex-1 flex items-center justify-center bg-gray-50 dark:bg-gray-900">
          <div className="text-center max-w-md px-6">
            <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-gray-200 dark:bg-gray-800 flex items-center justify-center">
              <span className="text-3xl">🚫</span>
            </div>
            <h2 className="text-gray-900 dark:text-gray-100 mb-2">Contact Blocked</h2>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
              Unblock {chat.name} to see messages and send new ones.
            </p>
            <Button
              onClick={() => onBlockChat(chat.id)}
              className="bg-gradient-to-br from-emerald-400 to-emerald-500 hover:from-emerald-500 hover:to-emerald-600 text-white"
            >
              Unblock Contact
            </Button>
          </div>
        </div>
      ) : (
        <div className={`flex-1 overflow-y-auto ${padding} ${spacing} bg-gradient-to-b from-white to-gray-50 dark:from-gray-900 dark:to-gray-950`}>
          {messages
            .filter(message => 
              !searchQuery || 
              message.text.toLowerCase().includes(searchQuery.toLowerCase())
            )
            .map((message) => (
            <div
              key={message.id}
              className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`max-w-[70%] ${message.sender === 'user' ? 'order-2' : 'order-1'}`}>
                {message.sender === 'other' && message.senderName && (
                  <p className="text-xs text-gray-500 dark:text-gray-400 mb-1 ml-3">{message.senderName}</p>
                )}
                <div
                  className={`${compactMode ? 'px-3 py-2 text-sm' : 'px-4 py-2.5'} rounded-2xl ${
                    message.sender === 'user'
                      ? 'bg-gradient-to-br from-emerald-400 to-emerald-500 text-white rounded-br-md'
                      : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-bl-md'
                  }`}
                >
                  <p>{message.text}</p>
                </div>
                <div className={`flex items-center gap-1 text-xs text-gray-400 dark:text-gray-500 mt-1 ${message.sender === 'user' ? 'justify-end mr-3' : 'ml-3'}`}>
                  <span>{message.timestamp}</span>
                  {message.sender === 'user' && message.status && (
                    <span className="flex items-center">
                      {message.status === 'sent' && (
                        <Check className="h-3 w-3 text-gray-400" />
                      )}
                      {message.status === 'delivered' && (
                        <CheckCheck className="h-3 w-3 text-gray-400" />
                      )}
                      {message.status === 'read' && (
                        <CheckCheck className="h-3 w-3 text-emerald-400" />
                      )}
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Message Input */}
      {!chat.blocked && (
        <div className={`${compactMode ? 'p-3' : 'p-4'} border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900`}>
          <form onSubmit={handleSendMessage} className="flex items-center gap-3">
            <Input
              value={messageText}
              onChange={(e) => setMessageText(e.target.value)}
              placeholder="Type a message..."
              className="flex-1 bg-gray-50 dark:bg-gray-800 border-0 focus-visible:ring-1 focus-visible:ring-emerald-200 rounded-full px-5 dark:text-gray-100"
            />
            <Button
              type="submit"
              size="icon"
              className={`${compactMode ? 'h-9 w-9' : 'h-10 w-10'} rounded-full bg-gradient-to-br from-emerald-400 to-emerald-500 hover:from-emerald-500 hover:to-emerald-600 shadow-sm`}
            >
              <Send className="h-4 w-4" />
            </Button>
          </form>
        </div>
      )}
    </div>
  );
}