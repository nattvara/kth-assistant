import { HttpError, getSessionId, makeUrl } from "@/api/http";

export interface Course {
  canvas_id: string;
  language: string;
  name: string;
}

export interface Courses {
  courses: Course[];
}

export async function fetchCourses(): Promise<Courses> {
  const sessionCookie = getSessionId() as string;

  const response = await fetch(makeUrl(`/admin/courses`), {
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

  const data = (await response.json()) as Courses;
  return data;
}
