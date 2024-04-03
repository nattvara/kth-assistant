import Cookies from "js-cookie";

import { HttpError, makeUrl } from "./http";

export interface Session {
  public_id: string;
  message: string;
}

export async function startSession(): Promise<Session> {
  const response = await fetch(makeUrl(`/session`), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    const errorBody = await response.json();
    throw new HttpError(response, errorBody, response.status);
  }

  const data = (await response.json()) as Session;
  return data;
}

export async function getSession(): Promise<Session> {
  const sessionCookie = Cookies.get("session_id") as string;

  const response = await fetch(makeUrl(`/session/me`), {
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

  const data = (await response.json()) as Session;
  return data;
}
