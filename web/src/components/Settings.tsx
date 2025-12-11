import { ArrowLeft, Shield, Lock, Eye, Bell, Palette, Info, UserX, Key, Database } from 'lucide-react';
import { Button } from './ui/button';
import { Switch } from './ui/switch';
import { Separator } from './ui/separator';
import { Dialog, DialogContent, DialogTitle, DialogHeader, DialogDescription } from './ui/dialog';
import { useState } from 'react';
import { PulseSettings } from '../App';

interface SettingsProps {
  onBack: () => void;
  darkMode: boolean;
  setDarkMode: (value: boolean) => void;
  compactMode: boolean;
  setCompactMode: (value: boolean) => void;
  settings?: PulseSettings;
  onUpdateSettings?: (settings: Partial<PulseSettings>) => void;
}

export function Settings({ onBack, darkMode, setDarkMode, compactMode, setCompactMode, settings, onUpdateSettings }: SettingsProps) {
  const [showPrivacy, setShowPrivacy] = useState(false);
  const [showTerms, setShowTerms] = useState(false);

  const handleSettingChange = (key: keyof PulseSettings, value: boolean) => {
    if (onUpdateSettings) {
      onUpdateSettings({ [key]: value });
    }
  };

  const handleClearHistory = () => {
    // This would call your backend to clear all history
    console.log('Clear all chat history');
  };

  return (
    <div className="flex-1 flex flex-col bg-white dark:bg-gray-900">
      {/* Settings Header */}
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-800 flex items-center gap-4 bg-white dark:bg-gray-900">
        <Button
          size="icon"
          variant="ghost"
          onClick={onBack}
          className="h-9 w-9 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800"
        >
          <ArrowLeft className="h-5 w-5 text-gray-600 dark:text-gray-400" />
        </Button>
        <h1 className="text-gray-900 dark:text-gray-100">Settings</h1>
      </div>

      {/* Settings Content */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-2xl mx-auto p-6 space-y-6">
          
          {/* Privacy & Security Section */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Shield className="h-5 w-5 text-emerald-600 dark:text-emerald-500" />
              <h2 className="text-gray-900 dark:text-gray-100">Privacy & Security</h2>
            </div>
            <div className="space-y-4 bg-gray-50 dark:bg-gray-800 rounded-xl p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Lock className="h-4 w-4 text-gray-500 dark:text-gray-400" />
                  <div>
                    <p className="text-gray-900 dark:text-gray-100">End-to-End Encryption</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">All messages are encrypted</p>
                  </div>
                </div>
                <Switch 
                  checked={settings?.encryption ?? true} 
                  onCheckedChange={(checked) => handleSettingChange('encryption', checked)}
                />
              </div>
              <Separator className="dark:bg-gray-700" />
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Eye className="h-4 w-4 text-gray-500 dark:text-gray-400" />
                  <div>
                    <p className="text-gray-900 dark:text-gray-100">Read Receipts</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">Show when you've read messages</p>
                  </div>
                </div>
                <Switch 
                  checked={settings?.readReceipts ?? true}
                  onCheckedChange={(checked) => handleSettingChange('readReceipts', checked)}
                />
              </div>
              <Separator className="dark:bg-gray-700" />
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <UserX className="h-4 w-4 text-gray-500 dark:text-gray-400" />
                  <div>
                    <p className="text-gray-900 dark:text-gray-100">Block Unknown Contacts</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">Auto-block messages from strangers</p>
                  </div>
                </div>
                <Switch 
                  checked={settings?.blockUnknown ?? false}
                  onCheckedChange={(checked) => handleSettingChange('blockUnknown', checked)}
                />
              </div>
            </div>
          </div>

          {/* Authentication Section */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Key className="h-5 w-5 text-emerald-600 dark:text-emerald-500" />
              <h2 className="text-gray-900 dark:text-gray-100">Authentication</h2>
            </div>
            <div className="space-y-4 bg-gray-50 dark:bg-gray-800 rounded-xl p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-900 dark:text-gray-100">Two-Factor Authentication</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Add extra security to your account</p>
                </div>
                <Switch 
                  checked={settings?.twoFactor ?? false}
                  onCheckedChange={(checked) => handleSettingChange('twoFactor', checked)}
                />
              </div>
              <Separator className="dark:bg-gray-700" />
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-900 dark:text-gray-100">Biometric Lock</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Use fingerprint or face ID</p>
                </div>
                <Switch 
                  checked={settings?.biometric ?? false}
                  onCheckedChange={(checked) => handleSettingChange('biometric', checked)}
                />
              </div>
            </div>
          </div>

          {/* Data & Storage Section */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Database className="h-5 w-5 text-emerald-600 dark:text-emerald-500" />
              <h2 className="text-gray-900 dark:text-gray-100">Data & Storage</h2>
            </div>
            <div className="space-y-4 bg-gray-50 dark:bg-gray-800 rounded-xl p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-900 dark:text-gray-100">Auto-Delete Messages</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Remove messages after 30 days</p>
                </div>
                <Switch 
                  checked={settings?.autoDelete ?? false}
                  onCheckedChange={(checked) => handleSettingChange('autoDelete', checked)}
                />
              </div>
              <Separator className="dark:bg-gray-700" />
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-900 dark:text-gray-100">Local Backup</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Encrypted backup on your device</p>
                </div>
                <Switch 
                  checked={settings?.localBackup ?? true}
                  onCheckedChange={(checked) => handleSettingChange('localBackup', checked)}
                />
              </div>
              <Separator className="dark:bg-gray-700" />
              <Button 
                variant="outline" 
                className="w-full justify-start text-gray-900 dark:text-gray-100 hover:bg-white dark:hover:bg-gray-900 border-gray-300 dark:border-gray-700"
                onClick={handleClearHistory}
              >
                Clear All Chat History
              </Button>
            </div>
          </div>

          {/* Notifications Section */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Bell className="h-5 w-5 text-emerald-600 dark:text-emerald-500" />
              <h2 className="text-gray-900 dark:text-gray-100">Notifications</h2>
            </div>
            <div className="space-y-4 bg-gray-50 dark:bg-gray-800 rounded-xl p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-900 dark:text-gray-100">Show Message Preview</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Display message content in notifications</p>
                </div>
                <Switch 
                  checked={settings?.showPreview ?? true}
                  onCheckedChange={(checked) => handleSettingChange('showPreview', checked)}
                />
              </div>
              <Separator className="dark:bg-gray-700" />
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-900 dark:text-gray-100">Sound</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Play sound for new messages</p>
                </div>
                <Switch 
                  checked={settings?.sound ?? true}
                  onCheckedChange={(checked) => handleSettingChange('sound', checked)}
                />
              </div>
            </div>
          </div>

          {/* Appearance Section */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Palette className="h-5 w-5 text-emerald-600 dark:text-emerald-500" />
              <h2 className="text-gray-900 dark:text-gray-100">Appearance</h2>
            </div>
            <div className="space-y-4 bg-gray-50 dark:bg-gray-800 rounded-xl p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-900 dark:text-gray-100">Dark Mode</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Use dark theme</p>
                </div>
                <Switch checked={darkMode} onCheckedChange={setDarkMode} />
              </div>
              <Separator className="dark:bg-gray-700" />
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-900 dark:text-gray-100">Compact Mode</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Reduce spacing and padding</p>
                </div>
                <Switch checked={compactMode} onCheckedChange={setCompactMode} />
              </div>
            </div>
          </div>

          {/* About Section */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Info className="h-5 w-5 text-emerald-600 dark:text-emerald-500" />
              <h2 className="text-gray-900 dark:text-gray-100">About</h2>
            </div>
            <div className="space-y-4 bg-gray-50 dark:bg-gray-800 rounded-xl p-4">
              <div className="space-y-2">
                <p className="text-sm text-gray-900 dark:text-gray-100">Pulse v1.0.0</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Privacy-focused messaging platform with end-to-end encryption.
                  Your conversations are secure and never stored on our servers.
                </p>
              </div>
              <Separator className="dark:bg-gray-700" />
              <Button 
                variant="ghost" 
                className="w-full justify-start text-emerald-600 dark:text-emerald-500 hover:bg-emerald-50 dark:hover:bg-emerald-950"
                onClick={() => setShowPrivacy(true)}
              >
                Privacy Policy
              </Button>
              <Button 
                variant="ghost" 
                className="w-full justify-start text-emerald-600 dark:text-emerald-500 hover:bg-emerald-50 dark:hover:bg-emerald-950"
                onClick={() => setShowTerms(true)}
              >
                Terms of Service
              </Button>
            </div>
          </div>

        </div>
      </div>

      {/* Privacy Policy Dialog */}
      <Dialog open={showPrivacy} onOpenChange={setShowPrivacy}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto dark:bg-gray-900 dark:border-gray-800">
          <DialogHeader>
            <DialogTitle className="text-2xl text-gray-900 dark:text-gray-100">Privacy Policy</DialogTitle>
            <DialogDescription className="text-gray-500 dark:text-gray-400">
              Last updated: November 11, 2025
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 text-sm text-gray-700 dark:text-gray-300">
            <p>
              Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
            </p>
            <h3 className="text-gray-900 dark:text-gray-100 mt-6 mb-2">1. Information We Collect</h3>
            <p>
              Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
            </p>
            <p>
              Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.
            </p>
            <h3 className="text-gray-900 dark:text-gray-100 mt-6 mb-2">2. How We Use Your Information</h3>
            <p>
              Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo.
            </p>
            <p>
              Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt.
            </p>
            <h3 className="text-gray-900 dark:text-gray-100 mt-6 mb-2">3. End-to-End Encryption</h3>
            <p>
              At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati cupiditate non provident.
            </p>
            <h3 className="text-gray-900 dark:text-gray-100 mt-6 mb-2">4. Data Retention</h3>
            <p>
              Temporibus autem quibusdam et aut officiis debitis aut rerum necessitatibus saepe eveniet ut et voluptates repudiandae sint et molestiae non recusandae.
            </p>
            <p>
              Itaque earum rerum hic tenetur a sapiente delectus, ut aut reiciendis voluptatibus maiores alias consequatur aut perferendis doloribus asperiores repellat.
            </p>
            <h3 className="text-gray-900 dark:text-gray-100 mt-6 mb-2">5. Your Rights</h3>
            <p>
              Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Quis ipsum suspendisse ultrices gravida.
            </p>
          </div>
        </DialogContent>
      </Dialog>

      {/* Terms of Service Dialog */}
      <Dialog open={showTerms} onOpenChange={setShowTerms}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto dark:bg-gray-900 dark:border-gray-800">
          <DialogHeader>
            <DialogTitle className="text-2xl text-gray-900 dark:text-gray-100">Terms of Service</DialogTitle>
            <DialogDescription className="text-gray-500 dark:text-gray-400">
              Last updated: November 11, 2025
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 text-sm text-gray-700 dark:text-gray-300">
            <p>
              Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
            </p>
            <h3 className="text-gray-900 dark:text-gray-100 mt-6 mb-2">1. Acceptance of Terms</h3>
            <p>
              Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
            </p>
            <h3 className="text-gray-900 dark:text-gray-100 mt-6 mb-2">2. User Responsibilities</h3>
            <p>
              Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo.
            </p>
            <p>
              Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt.
            </p>
            <h3 className="text-gray-900 dark:text-gray-100 mt-6 mb-2">3. Privacy and Security</h3>
            <p>
              At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati cupiditate non provident.
            </p>
            <h3 className="text-gray-900 dark:text-gray-100 mt-6 mb-2">4. Prohibited Activities</h3>
            <p>
              Temporibus autem quibusdam et aut officiis debitis aut rerum necessitatibus saepe eveniet ut et voluptates repudiandae sint et molestiae non recusandae.
            </p>
            <h3 className="text-gray-900 dark:text-gray-100 mt-6 mb-2">5. Termination</h3>
            <p>
              Itaque earum rerum hic tenetur a sapiente delectus, ut aut reiciendis voluptatibus maiores alias consequatur aut perferendis doloribus asperiores repellat.
            </p>
            <h3 className="text-gray-900 dark:text-gray-100 mt-6 mb-2">6. Limitation of Liability</h3>
            <p>
              Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Quis ipsum suspendisse ultrices gravida. Risus commodo viverra maecenas accumsan lacus vel facilisis.
            </p>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}