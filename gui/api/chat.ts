import Cookies from "js-cookie";

import { HttpError, makeUrl } from "@/api/http";

export interface Chat {
  public_id: string;
  llm_model_name: string;
  index_type: string;
  language: string;
}

export interface Message {
  message_id: string;
  content: string | null;
  sender: string;
  created_at: string;
  streaming: boolean;
  websocket: string | null;
}

export interface Messages {
  messages: Message[];
}

export async function startChat(canvasId: string): Promise<Chat> {
  const sessionCookie = Cookies.get("session_id") as string;

  const response = await fetch(makeUrl(`/course/${canvasId}/chat`), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Session-ID": sessionCookie,
    },
  });

  if (!response.ok) {
    const errorBody = await response.json();
    throw new HttpError(response, errorBody);
  }

  const data = (await response.json()) as Chat;
  return data;
}

export async function fetchChat(canvasId: string, chatId: string): Promise<Chat> {
  const sessionCookie = Cookies.get("session_id") as string;

  const response = await fetch(makeUrl(`/course/${canvasId}/chat/${chatId}`), {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      "X-Session-ID": sessionCookie,
    },
  });

  if (!response.ok) {
    const errorBody = await response.json();
    throw new HttpError(response, errorBody);
  }

  const data = (await response.json()) as Chat;
  return data;
}

export async function fetchMessages(canvasId: string, chatId: string): Promise<Messages> {
  const sessionCookie = Cookies.get("session_id") as string;

  const response = await fetch(makeUrl(`/course/${canvasId}/chat/${chatId}/messages`), {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      "X-Session-ID": sessionCookie,
    },
  });

  if (!response.ok) {
    const errorBody = await response.json();
    throw new HttpError(response, errorBody);
  }

  const data = (await response.json()) as Messages;
  return data;
}

export async function sendMessage(canvasId: string, chatId: string, content: string): Promise<Message> {
  const sessionCookie = Cookies.get("session_id") as string;

  const response = await fetch(makeUrl(`/course/${canvasId}/chat/${chatId}/messages`), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Session-ID": sessionCookie,
    },
    body: JSON.stringify({
      content,
    }),
  });

  if (!response.ok) {
    const errorBody = await response.json();
    throw new HttpError(response, errorBody);
  }

  const data = (await response.json()) as Message;
  return data;
}
