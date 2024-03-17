export class HttpError extends Error {
  public statusCode: number;
  public statusText: string;
  public errorDetail: string;
  public headers: Headers;
  public code: string;

  constructor(response: Response, errorBody: {detail: string | { msg: string }[]}, code: string = "UnknownCode", message?: string) {
    super(message || "An error occurred");

    this.name = "HttpError";
    this.statusCode = response.status;
    this.statusText = response.statusText;
    this.errorDetail = typeof errorBody.detail === "string" ? errorBody.detail : errorBody.detail.map(d => d.msg).join(", ");
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
  baseURL = "/";
  baseWebsocketURL = "/";
} else {
  baseURL = "http://localhost:8000";
  baseWebsocketURL = "ws://localhost:8000";
}

export const makeUrl = (uri: string) => `${baseURL}${uri}`;
export const makeWebsocketUrl = (uri: string) => `${baseWebsocketURL}${uri}`;
