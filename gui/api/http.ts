import Cookies from "js-cookie";

export function getSessionId() {
  let sessionId = Cookies.get("session_id");

  if (!sessionId) {
    const local = localStorage.getItem("session_id");
    if (local) {
      sessionId = local;
    }
  }

  return sessionId;
}

export function setSessionId(sessionId: string) {
  try {
    Cookies.set("session_id", sessionId, { expires: 365, secure: true, sameSite: "None" });
  } catch (e) {
    localStorage.setItem("session_id", sessionId);
  }
}

export class HttpError extends Error {
  public statusCode: number;
  public statusText: string;
  public errorDetail: string;
  public headers: Headers;
  public code: number;

  constructor(response: Response, errorBody: { detail: string | { msg: string }[] }, code: number, message?: string) {
    super(message || "An error occurred");

    this.name = "HttpError";
    this.statusCode = response.status;
    this.statusText = response.statusText;
    this.errorDetail =
      typeof errorBody.detail === "string" ? errorBody.detail : errorBody.detail.map((d) => d.msg).join(", ");
    this.headers = response.headers;
    this.code = code;

    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, HttpError);
    }
  }
}

let baseURL: string;
let baseWebsocketURL: string;

if (process.env.NODE_ENV === "production") {
  baseURL = "https://copilot.openuni.ai/api";
  baseWebsocketURL = "wss://copilot.openuni.ai/api";
} else {
  baseURL = "http://localhost:8000";
  baseWebsocketURL = "ws://localhost:8000";
}

export const makeUrl = (uri: string) => `${baseURL}${uri}`;
export const makeWebsocketUrl = (uri: string) => `${baseWebsocketURL}${uri}`;
