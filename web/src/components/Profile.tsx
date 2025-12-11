import { X, Mail, Phone, Shield, Info } from 'lucide-react';
import { Chat } from '../App';
import { Button } from './ui/button';
import { Separator } from './ui/separator';

interface ProfileProps {
  chat: Chat;
  onClose: () => void;
  onBlock: () => void;
  onMute: () => void;
}

export function Profile({ chat, onClose, onBlock, onMute }: ProfileProps) {
  return (
    <div className="flex-1 flex flex-col bg-white dark:bg-gray-900">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-800 flex items-center justify-between bg-white dark:bg-gray-900">
        <h2 className="text-gray-900 dark:text-gray-100">Profile</h2>
        <Button
          size="icon"
          variant="ghost"
          onClick={onClose}
          className="h-9 w-9 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800"
        >
          <X className="h-5 w-5 text-gray-600 dark:text-gray-400" />
        </Button>
      </div>

      {/* Profile Content */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-2xl mx-auto p-6 space-y-6">
          {/* Avatar and Name */}
          <div className="flex flex-col items-center gap-4 py-6">
            <div className="relative">
              <div className="w-32 h-32 rounded-full bg-gradient-to-br from-emerald-400 to-teal-400 flex items-center justify-center text-white text-5xl">
                {chat.avatar}
              </div>
              {chat.online && (
                <div className="absolute bottom-2 right-2 w-6 h-6 bg-emerald-400 rounded-full border-4 border-white dark:border-gray-900"></div>
              )}
            </div>
            <div className="text-center">
              <h1 className="text-2xl text-gray-900 dark:text-gray-100 mb-1">{chat.name}</h1>
              <p className="text-sm text-gray-500 dark:text-gray-400">{chat.online ? 'Online' : 'Offline'}</p>
            </div>
          </div>

          {/* Contact Information */}
          <div>
            <h3 className="text-sm text-gray-500 dark:text-gray-400 mb-3">Contact Information</h3>
            <div className="space-y-3 bg-gray-50 dark:bg-gray-800 rounded-xl p-4">
              <div className="flex items-center gap-3">
                <Mail className="h-4 w-4 text-gray-500 dark:text-gray-400" />
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Email</p>
                  <p className="text-sm text-gray-900 dark:text-gray-100">{chat.name.toLowerCase().replace(' ', '.')}@example.com</p>
                </div>
              </div>
              <Separator className="dark:bg-gray-700" />
              <div className="flex items-center gap-3">
                <Phone className="h-4 w-4 text-gray-500 dark:text-gray-400" />
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Phone</p>
                  <p className="text-sm text-gray-900 dark:text-gray-100">+1 (555) 123-4567</p>
                </div>
              </div>
            </div>
          </div>

          {/* Security & Privacy */}
          <div>
            <h3 className="text-sm text-gray-500 dark:text-gray-400 mb-3">Security & Privacy</h3>
            <div className="space-y-3 bg-gray-50 dark:bg-gray-800 rounded-xl p-4">
              <div className="flex items-center gap-3">
                <Shield className="h-4 w-4 text-emerald-600 dark:text-emerald-500" />
                <div>
                  <p className="text-sm text-gray-900 dark:text-gray-100">Encryption</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Messages are end-to-end encrypted</p>
                </div>
              </div>
              <Separator className="dark:bg-gray-700" />
              <div className="flex items-center gap-3">
                <Info className="h-4 w-4 text-gray-500 dark:text-gray-400" />
                <div>
                  <p className="text-sm text-gray-900 dark:text-gray-100">Verified Contact</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Security code: 12345-67890</p>
                </div>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="space-y-2">
            <Button
              variant="outline"
              className="w-full justify-start text-gray-900 dark:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-800"
              onClick={onMute}
            >
              {chat.muted ? 'Unmute Notifications' : 'Mute Notifications'}
            </Button>
            <Button
              variant="outline"
              className="w-full justify-start text-gray-900 dark:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-800"
            >
              Search Messages
            </Button>
            <Button
              variant="outline"
              className="w-full justify-start text-gray-900 dark:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-800"
            >
              Clear Chat History
            </Button>
            <Separator className="dark:bg-gray-700" />
            <Button
              variant="outline"
              className="w-full justify-start text-red-600 dark:text-red-500 hover:bg-red-50 dark:hover:bg-red-950"
              onClick={onBlock}
            >
              {chat.blocked ? 'Unblock Contact' : 'Block Contact'}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
