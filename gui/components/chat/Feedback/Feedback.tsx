import { useQuery } from "@tanstack/react-query";

import { Message } from "@/api/chat";
import { fetchFeedbackQuestions } from "@/api/feedback";

import { SelectFeedback } from "./SelectFeedback";
import { ThumbsFeedback } from "./ThumbsFeedback";

export interface FeedbackProps {
  message: Message;
  withLabel: boolean;
  withPostLabel: boolean;
  courseId: string;
  chatId: string;
}

export default function Feedback(props: FeedbackProps) {
  const { message, withLabel, withPostLabel, courseId, chatId } = props;
  const questionQuery = useQuery({
    queryKey: ["feedback_questions", message.feedback_id],
    queryFn: () => fetchFeedbackQuestions(message.feedback_id as string),
  });

  if (questionQuery.isError) {
    return <span>Failed to fetch feedback question: {questionQuery.error.message}</span>;
  }

  if (questionQuery.data === null || questionQuery.data === undefined) {
    return <></>;
  }

  if (questionQuery.data.extra_data.type === "select") {
    return (
      <SelectFeedback
        message={message}
        feedback={questionQuery.data}
        withLabel={withLabel}
        withPostLabel={withPostLabel}
        courseId={courseId}
        chatId={chatId}
      />
    );
  }

  if (questionQuery.data.extra_data.type === "thumbs") {
    return <ThumbsFeedback message={message} feedback={questionQuery.data} courseId={courseId} chatId={chatId} />;
  }

  return <>Error: Unknown feedback type.</>;
}
