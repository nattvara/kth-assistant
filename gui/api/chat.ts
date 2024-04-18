import { HttpError, getSessionId, makeUrl } from "@/api/http";

export interface Faq {
  faq_id: string;
  question: string;
}

export interface Chat {
  public_id: string;
  llm_model_name: string;
  index_type: string;
  language: string;
  course_name: string;
  faqs: Faq[];
  read_only: boolean;
}

export interface ChatOverview {
  chat_id: string;
  llm_model_name: string;
  index_type: string;
  user_id: string;
  created_at: string;
}

export interface Chats {
  chats: ChatOverview[];
}

export interface Course {
  canvas_id: string;
  language: string;
  name: string;
}

export const MESSAGE_PENDING = "pending";

export const MESSAGE_READY = "ready";

export type MessageState = typeof MESSAGE_READY | typeof MESSAGE_PENDING;

export interface Message {
  message_id: string;
  content: string | null;
  sender: string;
  state: MessageState;
  created_at: string;
  streaming: boolean;
  websocket: string | null;
  from_faq: boolean;
  feedback_id: string | null;
}

export interface Messages {
  messages: Message[];
}

export class ChatNotFoundError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ChatNotFoundError";
  }
}

export async function fetchCourse(canvasId: string): Promise<Course> {
  const sessionCookie = getSessionId() as string;

  const response = await fetch(makeUrl(`/course/${canvasId}`), {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      "X-Session-ID": sessionCookie,
    },
  });

  if (!response.ok) {
    const errorBody = await response.json();
    throw new HttpError(response, errorBody, response.status);
  }

  const data = (await response.json()) as Course;
  return data;
}

export async function fetchChats(canvasId: string): Promise<Chats> {
  const sessionCookie = getSessionId() as string;

  const response = await fetch(makeUrl(`/course/${canvasId}/chat`), {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      "X-Session-ID": sessionCookie,
    },
  });

  if (!response.ok) {
    const errorBody = await response.json();
    throw new HttpError(response, errorBody, response.status);
  }

  const data = (await response.json()) as Chats;
  return data;
}

export async function startChat(canvasId: string): Promise<Chat> {
  const sessionCookie = getSessionId() as string;

  const response = await fetch(makeUrl(`/course/${canvasId}/chat`), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Session-ID": sessionCookie,
    },
  });

  if (!response.ok) {
    const errorBody = await response.json();
    throw new HttpError(response, errorBody, response.status);
  }

  const data = (await response.json()) as Chat;
  return data;
}

export async function fetchChat(canvasId: string, chatId: string): Promise<Chat> {
  const sessionCookie = getSessionId() as string;

  const response = await fetch(makeUrl(`/course/${canvasId}/chat/${chatId}`), {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      "X-Session-ID": sessionCookie,
    },
  });

  if (response.status === 404) {
    throw new ChatNotFoundError("chat not found");
  }

  if (!response.ok) {
    const errorBody = await response.json();
    throw new HttpError(response, errorBody, response.status);
  }

  const data = (await response.json()) as Chat;
  return data;
}

export async function fetchMessages(canvasId: string, chatId: string): Promise<Messages> {
  const sessionCookie = getSessionId() as string;

  const response = await fetch(makeUrl(`/course/${canvasId}/chat/${chatId}/messages`), {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      "X-Session-ID": sessionCookie,
    },
  });

  if (!response.ok) {
    const errorBody = await response.json();
    throw new HttpError(response, errorBody, response.status);
  }

  const data = (await response.json()) as Messages;
  return data;
}

export async function fetchMessage(canvasId: string, chatId: string, messageId: string): Promise<Message> {
  const sessionCookie = getSessionId() as string;

  const response = await fetch(makeUrl(`/course/${canvasId}/chat/${chatId}/messages/${messageId}`), {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      "X-Session-ID": sessionCookie,
    },
  });

  if (!response.ok) {
    const errorBody = await response.json();
    throw new HttpError(response, errorBody, response.status);
  }

  const data = (await response.json()) as Message;
  return data;
}

export async function sendMessage(canvasId: string, chatId: string, content: string): Promise<Message> {
  const sessionCookie = getSessionId() as string;

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
    throw new HttpError(response, errorBody, response.status);
  }

  const data = (await response.json()) as Message;
  return data;
}

export async function sendMessageUsingFaq(canvasId: string, chatId: string, faqId: string): Promise<Message> {
  const sessionCookie = getSessionId() as string;

  const response = await fetch(makeUrl(`/course/${canvasId}/chat/${chatId}/messages`), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Session-ID": sessionCookie,
    },
    body: JSON.stringify({
      faq_id: faqId,
    }),
  });

  if (!response.ok) {
    const errorBody = await response.json();
    throw new HttpError(response, errorBody, response.status);
  }

  const data = (await response.json()) as Message;
  return data;
}
