import { apiFetch } from "./api";

export async function getMessages(conversationID: string) {
    const res = await apiFetch(`/conversations/${conversationID}/messages`, {
        method: "GET",
    });
    if (!res.ok) {
        throw new Error(`getMessages failed: ${res.statusText}`);
    }
    const data = await res.json();
    return data;
}

export async function sendMessage(conversationId: string, content: string) {
    const res = await apiFetch(`/messages/send`, {
        method: "POST",
        body: JSON.stringify({ conversation_id: conversationId, content }),
    });
    return res;
}

export default { getMessages, sendMessage };
