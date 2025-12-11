import { useState, useEffect } from "react";
import { ChatSidebar } from "./components/ChatSidebar";
import { ChatWindow } from "./components/ChatWindow";
import { Settings } from "./components/Settings";

export interface Chat {
    id: string;
    name: string;
    avatar: string;
    lastMessage: string;
    timestamp: string;
    unread?: number;
    online?: boolean;
    blocked?: boolean;
    muted?: boolean;
}

export interface Message {
    id: string;
    text: string;
    sender: "user" | "other";
    timestamp: string;
    senderName?: string;
    status?: "sent" | "delivered" | "read";
}

export interface PulseCallbacks {
    onSendMessage?: (chatId: string, message: string) => Promise<void> | void;
    onBlockChat?: (chatId: string, blocked: boolean) => Promise<void> | void;
    onMuteChat?: (chatId: string, muted: boolean) => Promise<void> | void;
    onClearHistory?: (chatId: string) => Promise<void> | void;
    onUpdateSettings?: (settings: PulseSettings) => Promise<void> | void;
    onSearchMessages?: (query: string) => Promise<Message[]> | Message[];
    onLoadMessages?: (chatId: string) => Promise<Message[]> | Message[];
    onCreateContact?: () => Promise<Chat | null> | Chat | null | void;
    onDeleteContact?: (chatId: string) => Promise<void> | void;
}

export interface PulseSettings {
    encryption?: boolean;
    readReceipts?: boolean;
    blockUnknown?: boolean;
    twoFactor?: boolean;
    biometric?: boolean;
    autoDelete?: boolean;
    localBackup?: boolean;
    showPreview?: boolean;
    sound?: boolean;
    darkMode?: boolean;
    compactMode?: boolean;
}

const mockChats: Chat[] = [
    {
        id: "1",
        name: "Sarah Johnson",
        avatar: "SJ",
        lastMessage: "That sounds great! Let me know when you're free.",
        timestamp: "2m ago",
        unread: 2,
        online: true,
    },
    {
        id: "2",
        name: "Design Team",
        avatar: "DT",
        lastMessage: "Alex: I've uploaded the new mockups",
        timestamp: "15m ago",
        unread: 5,
        online: true,
    },
    {
        id: "3",
        name: "Marcus Chen",
        avatar: "MC",
        lastMessage: "Thanks for your help!",
        timestamp: "1h ago",
        online: false,
    },
    {
        id: "4",
        name: "Emma Wilson",
        avatar: "EW",
        lastMessage: "See you tomorrow 👋",
        timestamp: "3h ago",
        online: true,
    },
    {
        id: "5",
        name: "Project Alpha",
        avatar: "PA",
        lastMessage: "Meeting starts in 10 minutes",
        timestamp: "5h ago",
        online: false,
        blocked: true,
    },
];

const mockMessages: Record<string, Message[]> = {
    "1": [
        {
            id: "1",
            text: "Hey! How are you doing?",
            sender: "other",
            timestamp: "10:30 AM",
            senderName: "Sarah Johnson",
        },
        {
            id: "2",
            text: "I'm doing great! Just finished the new design for Pulse.",
            sender: "user",
            timestamp: "10:32 AM",
            status: "read",
        },
        {
            id: "3",
            text: "Oh that's awesome! Can I take a look?",
            sender: "other",
            timestamp: "10:33 AM",
            senderName: "Sarah Johnson",
        },
        {
            id: "4",
            text: "Sure! I'll send it over in a bit. It has this nice pastel green theme.",
            sender: "user",
            timestamp: "10:35 AM",
            status: "read",
        },
        {
            id: "5",
            text: "That sounds great! Let me know when you're free.",
            sender: "other",
            timestamp: "10:36 AM",
            senderName: "Sarah Johnson",
        },
    ],
    "2": [
        {
            id: "1",
            text: "Good morning team!",
            sender: "other",
            timestamp: "9:00 AM",
            senderName: "Alex",
        },
        {
            id: "2",
            text: "Morning! Ready for today's sprint.",
            sender: "user",
            timestamp: "9:05 AM",
            status: "read",
        },
        {
            id: "3",
            text: "I've uploaded the new mockups",
            sender: "other",
            timestamp: "9:47 AM",
            senderName: "Alex",
        },
    ],
};

// Custom hook to detect system dark mode preference
function useSystemDarkMode() {
    const [isDark, setIsDark] = useState(() => {
        if (typeof window !== "undefined") {
            return window.matchMedia("(prefers-color-scheme: dark)").matches;
        }
        return false;
    });

    useEffect(() => {
        const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
        const handler = (e: MediaQueryListEvent) => setIsDark(e.matches);

        mediaQuery.addEventListener("change", handler);
        return () => mediaQuery.removeEventListener("change", handler);
    }, []);

    return isDark;
}

interface AppProps {
    initialChats?: Chat[];
    initialMessages?: Record<string, Message[]>;
    callbacks?: PulseCallbacks;
    initialSettings?: PulseSettings;
}

export default function App({
    initialChats = mockChats,
    initialMessages = mockMessages,
    callbacks = {},
    initialSettings = {},
}: AppProps = {}) {
    const systemDarkMode = useSystemDarkMode();
    const [selectedChatId, setSelectedChatId] = useState<string>("1");
    const [currentPage, setCurrentPage] = useState<"chat" | "settings">("chat");
    const [chats, setChats] = useState<Chat[]>(initialChats);
    const [messages, setMessages] =
        useState<Record<string, Message[]>>(initialMessages);
    const [darkMode, setDarkMode] = useState(
        initialSettings?.darkMode ?? systemDarkMode
    );
    const [compactMode, setCompactMode] = useState(
        initialSettings?.compactMode ?? false
    );
    const [settings, setSettings] = useState<PulseSettings>(initialSettings);

    const selectedChat = chats?.find((chat) => chat.id === selectedChatId);
    const chatMessages = messages?.[selectedChatId] || [];

    // Update dark mode when system preference changes (if user hasn't manually set it)
    useEffect(() => {
        if (initialSettings?.darkMode === undefined) {
            setDarkMode(systemDarkMode);
        }
    }, [systemDarkMode, initialSettings?.darkMode]);

    const handleSendMessage = async (message: string) => {
        if (callbacks?.onSendMessage) {
            await callbacks.onSendMessage(selectedChatId, message);
        } else {
            // Default behavior: add message locally
            const newMessage: Message = {
                id: Date.now().toString(),
                text: message,
                sender: "user",
                timestamp: new Date().toLocaleTimeString("en-US", {
                    hour: "numeric",
                    minute: "2-digit",
                }),
                status: "sent",
            };
            setMessages((prev) => ({
                ...prev,
                [selectedChatId]: [...(prev[selectedChatId] || []), newMessage],
            }));
        }
    };

    const handleBlockChat = async (chatId: string) => {
        const chat = chats.find((c) => c.id === chatId);
        const newBlockedState = !chat?.blocked;

        if (callbacks?.onBlockChat) {
            await callbacks.onBlockChat(chatId, newBlockedState);
        }

        setChats(
            chats.map((chat) =>
                chat.id === chatId
                    ? { ...chat, blocked: newBlockedState }
                    : chat
            )
        );
    };

    const handleMuteChat = async (chatId: string) => {
        const chat = chats.find((c) => c.id === chatId);
        const newMutedState = !chat?.muted;

        if (callbacks?.onMuteChat) {
            await callbacks.onMuteChat(chatId, newMutedState);
        }

        setChats(
            chats.map((chat) =>
                chat.id === chatId ? { ...chat, muted: newMutedState } : chat
            )
        );
    };

    const handleClearHistory = async (chatId: string) => {
        if (callbacks?.onClearHistory) {
            await callbacks.onClearHistory(chatId);
        }

        setMessages((prev) => ({
            ...prev,
            [chatId]: [],
        }));
    };

    const handleUpdateSettings = async (
        newSettings: Partial<PulseSettings>
    ) => {
        const updatedSettings = { ...settings, ...newSettings };
        setSettings(updatedSettings);

        if (callbacks?.onUpdateSettings) {
            await callbacks.onUpdateSettings(updatedSettings);
        }
    };

    const handleDarkModeChange = (value: boolean) => {
        setDarkMode(value);
        handleUpdateSettings({ darkMode: value });
    };

    const handleCompactModeChange = (value: boolean) => {
        setCompactMode(value);
        handleUpdateSettings({ compactMode: value });
    };

    const handleCreateContact = async () => {
        if (callbacks?.onCreateContact) {
            try {
                const newChat = await callbacks.onCreateContact();
                if (newChat) {
                    setChats((prev) => [newChat, ...(prev || [])]);
                    setSelectedChatId(newChat.id);
                }
            } catch (e) {
                console.error("onCreateContact failed", e);
            }
            return;
        }

        // Fallback: prompt locally
        const name = window.prompt("Create new chat - enter name");
        if (name) {
            const id = Date.now().toString();
            const avatar = name
                .split(" ")
                .map((p) => p[0])
                .slice(0, 2)
                .join("");
            const newChat: Chat = {
                id,
                name,
                avatar,
                lastMessage: "",
                timestamp: "just now",
                online: true,
            };
            setChats((prev) => [newChat, ...(prev || [])]);
            setSelectedChatId(id);
        }
    };

    return (
        <div className={darkMode ? "dark" : ""}>
            <div className="flex h-screen w-full bg-gray-50 dark:bg-gray-900">
                <ChatSidebar
                    chats={chats}
                    selectedChatId={selectedChatId}
                    onSelectChat={setSelectedChatId}
                    currentPage={currentPage}
                    onNavigate={setCurrentPage}
                    compactMode={compactMode}
                    onCreateContact={handleCreateContact}
                />
                {currentPage === "chat" ? (
                    <ChatWindow
                        chat={selectedChat}
                        messages={chatMessages}
                        onSendMessage={handleSendMessage}
                        onBlockChat={handleBlockChat}
                        onMuteChat={handleMuteChat}
                        onClearHistory={handleClearHistory}
                        compactMode={compactMode}
                    />
                ) : (
                    <Settings
                        onBack={() => setCurrentPage("chat")}
                        darkMode={darkMode}
                        setDarkMode={handleDarkModeChange}
                        compactMode={compactMode}
                        setCompactMode={handleCompactModeChange}
                        settings={settings}
                        onUpdateSettings={handleUpdateSettings}
                    />
                )}
            </div>
        </div>
    );
}
