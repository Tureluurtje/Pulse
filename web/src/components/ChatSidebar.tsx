import { Search, Plus, Settings } from 'lucide-react';
import { Chat } from '../App';
import { Input } from './ui/input';
import { Button } from './ui/button';

interface ChatSidebarProps {
  chats: Chat[];
  selectedChatId: string;
  onSelectChat: (chatId: string) => void;
  currentPage: 'chat' | 'settings';
  onNavigate: (page: 'chat' | 'settings') => void;
  compactMode: boolean;
  onCreateContact?: () => void;
}

export function ChatSidebar({ chats, selectedChatId, onSelectChat, currentPage, onNavigate, compactMode, onCreateContact }: ChatSidebarProps) {
  const padding = compactMode ? 'p-3' : 'p-4';
  const avatarSize = compactMode ? 'w-10 h-10' : 'w-12 h-12';

  const handleCreateContact = () => {
    if (onCreateContact) {
      onCreateContact();
    }
  };

  return (
    <div className="w-80 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 flex flex-col">
      {/* Header */}
      <div className={`${padding} border-b border-gray-200 dark:border-gray-800`}>
        <div className={`flex items-center justify-between ${compactMode ? 'mb-3' : 'mb-4'}`}>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="3" fill="white"/>
                <circle cx="12" cy="12" r="7" stroke="white" strokeWidth="2" strokeDasharray="3 3"/>
                <circle cx="12" cy="12" r="10" stroke="white" strokeWidth="1.5" opacity="0.5"/>
              </svg>
            </div>
            <h1 className="text-emerald-600 dark:text-emerald-500">Pulse</h1>
          </div>
          <div className="flex items-center gap-1">
            <Button 
              size="icon" 
              variant="ghost" 
              className="h-9 w-9 rounded-full hover:bg-emerald-50 dark:hover:bg-emerald-950"
              onClick={() => onNavigate('settings')}
            >
              <Settings className="h-4 w-4 text-emerald-600 dark:text-emerald-500" />
            </Button>
            <Button 
              size="icon" 
              variant="ghost" 
              className="h-9 w-9 rounded-full hover:bg-emerald-50 dark:hover:bg-emerald-950"
              onClick={handleCreateContact}
            >
              <Plus className="h-5 w-5 text-emerald-600 dark:text-emerald-500" />
            </Button>
          </div>
        </div>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search chats..."
            className="pl-9 bg-gray-50 dark:bg-gray-800 border-0 focus-visible:ring-1 focus-visible:ring-emerald-200 dark:text-gray-100"
          />
        </div>
      </div>

      {/* Chat List */}
      <div className="flex-1 overflow-y-auto">
        {chats?.map((chat) => (
          <button
            key={chat.id}
            onClick={() => {
              onSelectChat(chat.id);
              onNavigate('chat');
            }}
            className={`w-full ${padding} flex items-start gap-3 transition-colors border-b border-gray-100 dark:border-gray-800 ${
              chat.blocked 
                ? `opacity-75 hover:bg-gray-50 dark:hover:bg-gray-800 ${
                    selectedChatId === chat.id && currentPage === 'chat' ? 'bg-gray-100 dark:bg-gray-800' : ''
                  }` 
                : `hover:bg-gray-50 dark:hover:bg-gray-800 ${
                    selectedChatId === chat.id && currentPage === 'chat' ? 'bg-emerald-50 dark:bg-emerald-950' : ''
                  }`
            }`}
          >
            {/* Avatar */}
            <div className="relative">
              <div className={`${avatarSize} rounded-full flex items-center justify-center text-white ${
                selectedChatId === chat.id && currentPage === 'chat' && !chat.blocked
                  ? 'bg-emerald-500' 
                  : 'bg-gradient-to-br from-emerald-400 to-teal-400'
              } ${chat.blocked ? 'grayscale' : ''}`}>
                {chat.avatar}
              </div>
              {chat.online && !chat.blocked && (
                <div className={`absolute bottom-0 right-0 ${compactMode ? 'w-2.5 h-2.5' : 'w-3 h-3'} bg-emerald-400 rounded-full border-2 border-white dark:border-gray-900`}></div>
              )}
            </div>

            {/* Chat Info */}
            <div className="flex-1 min-w-0 text-left">
              <div className="flex items-center justify-between mb-1">
                <span className={`${
                  selectedChatId === chat.id && currentPage === 'chat' && !chat.blocked
                    ? 'text-gray-900 dark:text-gray-100' 
                    : 'text-gray-700 dark:text-gray-300'
                } ${chat.blocked ? 'line-through' : ''}`}>
                  {chat.name}
                </span>
                <span className="text-xs text-gray-400 dark:text-gray-500">{chat.timestamp}</span>
              </div>
              <div className="flex items-center justify-between gap-2">
                <p className={`text-sm text-gray-500 dark:text-gray-400 truncate ${chat.blocked ? 'italic' : ''}`}>
                  {chat.blocked ? 'Blocked - Click to unblock' : chat.lastMessage}
                </p>
                {chat.unread && !chat.blocked && (
                  <span className="flex-shrink-0 min-w-[20px] h-5 px-1.5 rounded-full bg-emerald-500 text-white text-xs flex items-center justify-center">
                    {chat.unread}
                  </span>
                )}
                {chat.muted && !chat.blocked && (
                  <span className="flex-shrink-0 text-xs text-gray-400">🔕</span>
                )}
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}