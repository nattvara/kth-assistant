import { HttpError, getSessionId, makeUrl } from "./http";

export interface Session {
  public_id: string;
  message: string;
  consent: boolean;
}

export interface Consent {
  granted: boolean;
}

export interface GrantAdmin {
  ok: boolean;
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
  const sessionCookie = getSessionId() as string;

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

export async function grantConsent(): Promise<Consent> {
  const sessionCookie = getSessionId() as string;

  const response = await fetch(makeUrl(`/session/consent`), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Session-ID": sessionCookie,
    },
    body: JSON.stringify({
      granted: true,
    }),
  });

  if (!response.ok) {
    const errorBody = await response.json();
    throw new HttpError(response, errorBody, response.status);
  }

  const data = (await response.json()) as Consent;
  return data;
}

export async function grantAdminAccess(adminToken: string): Promise<GrantAdmin> {
  const sessionCookie = getSessionId() as string;

  const response = await fetch(makeUrl(`/session/grant_admin/${adminToken}`), {
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

  const data = (await response.json()) as GrantAdmin;
  return data;
}
