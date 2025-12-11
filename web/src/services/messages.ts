import { apiFetch } from "./api";

export async function getMessages(conversationId: string) {
    // backend expects conversation_id as query param
    const res = await apiFetch(
        `/messages?conversation_id=${encodeURIComponent(conversationId)}`
    );
    return res;
}

export async function sendMessage(conversationId: string, content: string) {
    const res = await apiFetch(`/messages/send`, {
        method: "POST",
        body: JSON.stringify({ conversation_id: conversationId, content }),
    });
    return res;
}

export default { getMessages, sendMessage };
