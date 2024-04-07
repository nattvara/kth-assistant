import Cookies from "js-cookie";

import { HttpError, makeUrl } from "@/api/http";

export interface Feedback {
  language: string;
  feedback_question_id: string;
  message_id: string;
  answer: string;
}

export interface FeedbackQuestion {
  feedback_question_id: string;
  question: string;
  extra_data: {
    choices: undefined | string[];
  };
}

export interface FeedbackQuestions {
  questions: FeedbackQuestion[];
}

export async function fetchFeedbackQuestions(language: string): Promise<FeedbackQuestions> {
  const sessionCookie = Cookies.get("session_id") as string;

  const response = await fetch(makeUrl(`/feedback/${language}`), {
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

  const data = (await response.json()) as FeedbackQuestions;
  return data;
}

export async function sendFeedback(
  language: string,
  feedbackQuestionId: string,
  messageId: string,
  choice: string,
): Promise<Feedback> {
  const sessionCookie = Cookies.get("session_id") as string;

  const response = await fetch(makeUrl(`/feedback/${language}/questions/${feedbackQuestionId}/messages/${messageId}`), {
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

export async function fetchFeedback(
  language: string,
  feedbackQuestionId: string,
  messageId: string,
): Promise<Feedback> {
  const sessionCookie = Cookies.get("session_id") as string;

  const response = await fetch(makeUrl(`/feedback/${language}/questions/${feedbackQuestionId}/messages/${messageId}`), {
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

export async function fetchFeedbackIsAnswered(
  language: string,
  feedbackQuestionId: string,
  messageId: string,
): Promise<boolean> {
  const sessionCookie = Cookies.get("session_id") as string;

  const response = await fetch(makeUrl(`/feedback/${language}/questions/${feedbackQuestionId}/messages/${messageId}`), {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      "X-Session-ID": sessionCookie,
    },
  });

  if (!response.ok) {
    if (response.status === 404) return false;

    const errorBody = await response.json();
    throw new HttpError(response, errorBody, response.status);
  }

  return true;
}
