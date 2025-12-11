import React from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Routes, Route, useNavigate } from "react-router-dom";
import App from "./App.tsx";
import "./index.css";
import Login from "./components/Login";
import Register from "./components/Register";
import * as messagesService from "./services/messages";
import * as authService from "./services/auth";

function ProtectedAppWrapper() {
    const navigate = useNavigate();
    const [loading, setLoading] = React.useState(true);

    React.useEffect(() => {
        (async () => {
            const authenticated = await authService.isAuthenticated();
            if (!authenticated) {
                navigate("/login");
            } else {
                setLoading(false);
            }
        })();
    }, [navigate]);

    if (loading) return <p>Loading...</p>;

    // callbacks wired to backend
    const callbacks = {
        onSendMessage: async (chatId: string, message: string) => {
            try {
                await messagesService.sendMessage(chatId, message);
            } catch (e) {
                console.error("sendMessage failed", e);
                throw e;
            }
        },
        onLoadMessages: async (chatId: string) => {
            try {
                const msgs = await messagesService.getMessages(chatId);
                return msgs.map((m: any) => ({
                    id: m.id,
                    text: m.content,
                    sender: m.sender_id
                        ? m.sender_id === "user"
                            ? "user"
                            : "other"
                        : "other",
                    timestamp: new Date(m.created_at).toLocaleTimeString(),
                }));
            } catch (e) {
                console.error("loadMessages failed", e);
                return [];
            }
        },
        onCreateContact: async () => {
            const name = window.prompt("Create new chat - enter name");
            if (!name) return null;
            const id = Date.now().toString();
            const avatar = name
                .split(" ")
                .map((p) => p[0])
                .slice(0, 2)
                .join("");
            return {
                id,
                name,
                avatar,
                lastMessage: "",
                timestamp: "just now",
                online: true,
            };
        },
    };

    return <App callbacks={callbacks} />;
}

const root = createRoot(document.getElementById("root")!);

root.render(
    <React.StrictMode>
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<ProtectedAppWrapper />} />
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
            </Routes>
        </BrowserRouter>
    </React.StrictMode>
);
