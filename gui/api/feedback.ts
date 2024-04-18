import { HttpError, getSessionId, makeUrl } from "@/api/http";

export const UNANSWERED = "UNANSWERED";

export interface Feedback {
  feedback_question_id: string;
  question: string;
  extra_data: {
    type: string;
    choices: string[];
  };
}

export async function fetchFeedbackQuestions(feedbackId: string): Promise<Feedback> {
  const sessionCookie = getSessionId() as string;

  const response = await fetch(makeUrl(`/feedback/${feedbackId}`), {
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

  const data = (await response.json()) as Feedback;
  return data;
}

export async function sendFeedback(feedback_id: string, choice: string): Promise<Feedback> {
  const sessionCookie = getSessionId() as string;

  const response = await fetch(makeUrl(`/feedback/${feedback_id}`), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Session-ID": sessionCookie,
    },
    body: JSON.stringify({
      choice,
    }),
  });

  if (!response.ok) {
    const errorBody = await response.json();
    throw new HttpError(response, errorBody, response.status);
  }

  const data = (await response.json()) as Feedback;
  return data;
}
