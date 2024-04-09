import { Alert, Collapse, Notification, SimpleGrid, Text, Title } from "@mantine/core";
import { useQueries, useQuery } from "@tanstack/react-query";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { useEffect, useState } from "react";

import { Message } from "@/api/chat";
import { fetchFeedbackIsAnswered, fetchFeedbackQuestions } from "@/api/feedback";

import FeedbackQuestion from "./FeedbackQuestion";
import styles from "./styles.module.css";

interface FeedbackQuestionsProps {
  message: Message;
}

export default function FeedbackQuestions(props: FeedbackQuestionsProps) {
  const { message } = props;
  const { t } = useTranslation("chat");
  const router = useRouter();
  const { locale } = router;
  const [showFeedback, setShowFeedback] = useState(false);

  const { data, isError, error } = useQuery({
    queryKey: ["feedback"],
    queryFn: () => fetchFeedbackQuestions(locale as string),
  });

  const feedbackAnsweredQueries =
    data?.questions.map((question) => ({
      queryKey: ["feedback_isAnswered", question.feedback_question_id, message.message_id],
      queryFn: () => fetchFeedbackIsAnswered(locale as string, question.feedback_question_id, message.message_id),
      retry: 0,
      enabled: !!data,
    })) || [];

  const feedbackAnswers = useQueries({ queries: feedbackAnsweredQueries });

  useEffect(() => {
    if (data) {
      const allQuestionsAnswered = feedbackAnswers.every((query) => query.isSuccess && query.data);
      setShowFeedback(!allQuestionsAnswered);
    }
  }, [data, feedbackAnswers]);

  if (isError) {
    return <span>Failed to fetch feedback questions: {error.message}</span>;
  }

  if (data === null || data === undefined) {
    return <></>;
  }

  return (
    <SimpleGrid cols={1}>
      <Collapse in={showFeedback} transitionDuration={300}>
        <Alert variant="light" color="teal" className={styles.alert}>
          <Title order={3} className={styles.title}>
            {t("feedback.title")}
          </Title>
          <Text size="sm" className={styles.subtitle}>
            {t("feedback.subtitle")}
          </Text>

          {data.questions.map((question) => (
            <FeedbackQuestion
              key={question.feedback_question_id}
              question={question}
              message={message}
              language={locale as string}
            />
          ))}
        </Alert>
      </Collapse>
      {!showFeedback && (
        <Notification
          title={t("feedback.done")}
          withCloseButton={false}
          color="teal"
          className={styles.done}
        ></Notification>
      )}
    </SimpleGrid>
  );
}
