import { apiFetch } from "./api";

const API_BASE = import.meta.env.PROD
    ? "https://api.pulse.kwako.nl"
    : "http://localhost:8000";

export async function apiFetchDebug(path: string, opts: RequestInit = {}) {
    console.log("Mock apiFetch called with path:", path, "and opts:", opts);
    console.log(
        `url constructed: ${API_BASE}${
            path.startsWith("/") ? path : `/${path}`
        }`
    );
    return Promise.resolve(new Response(null, { status: 200 }));
}

async function getMessages(conversationID: string) {
    const res = await apiFetch(`/conversations/${conversationID}/messages`, {
        method: "GET",
    });
    if (!res.ok) {
        throw new Error(`getMessages failed: ${res.statusText}`);
    }
    const data = await res.json();
    return data;
}

export async function getConversations() {
    // backend expects conversation_id as query param
    const res = await apiFetch(`/conversations/`, {
        method: "GET",
    });
    if (!res.ok) {
        throw new Error(`getConversations failed: ${res.statusText}`);
    }
    const data: Conversation[] = await res.json();
    data.forEach((conversation: Conversation) => {
        getMessages(conversation.id).then(msgRes => {
            conversation.messages = msgRes;
        });
    });
    return data;
}

export interface Conversation {
  id: string;
  name: string;
  messages?: Message[]
  created_by: string;
  created_at: string; // ISO8601 timestamp
  participant_count: number;
}

export interface Message {
    id: string;
    content: string;
    sender_id: string;
    created_at: string; // ISO8601 timestamp
}
