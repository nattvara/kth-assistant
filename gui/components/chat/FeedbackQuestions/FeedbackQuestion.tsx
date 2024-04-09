import { Button, Group, Paper, SimpleGrid, Title } from "@mantine/core";
import { notifications } from "@mantine/notifications";
import { IconExclamationCircle } from "@tabler/icons-react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";

import { Message } from "@/api/chat";
import {
  FeedbackQuestion as FeedbackQuestionData,
  fetchFeedback,
  fetchFeedbackIsAnswered,
  sendFeedback,
} from "@/api/feedback";
import { HttpError } from "@/api/http";

import styles from "./styles.module.css";

function shuffleArray(array: string[]): string[] {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
  return array;
}

interface FeedbackQuestionProps {
  message: Message;
  question: FeedbackQuestionData;
  language: string;
}

export default function FeedbackQuestion(props: FeedbackQuestionProps) {
  const { message, question, language } = props;
  const [shuffledChoices, setShuffledChoices] = useState<string[]>([]);
  const queryClient = useQueryClient();

  const isAnswered = useQuery({
    queryKey: ["feedback_isAnswered", question.feedback_question_id, message.message_id],
    queryFn: () => fetchFeedbackIsAnswered(language, question.feedback_question_id, message.message_id),
    retry: 0,
  });

  const feedbackResponse = useQuery({
    queryKey: ["feedback_response", question.feedback_question_id, message.message_id],
    queryFn: () => fetchFeedback(language, question.feedback_question_id, message.message_id),
    retry: 0,
    enabled: isAnswered.data,
  });

  const sendMutation = useMutation({
    mutationFn: (choice: string) => sendFeedback(language, question.feedback_question_id, message.message_id, choice),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["feedback_isAnswered", question.feedback_question_id, message.message_id],
      });
      queryClient.invalidateQueries({
        queryKey: ["feedback_response", question.feedback_question_id, message.message_id],
      });
    },
    onError: (error: HttpError) => {
      console.error(error);
      notifications.show({
        title: "Failed to send feedback",
        color: "red",
        message: error.errorDetail,
        icon: <IconExclamationCircle />,
      });
    },
  });

  useEffect(() => {
    if (question.extra_data.choices !== undefined) {
      setShuffledChoices(shuffleArray(question.extra_data.choices));
    }
  }, [question.extra_data.choices]);

  const handleSelectChoice = (value: string) => {
    sendMutation.mutate(value);
  };

  if (isAnswered.isError) {
    return <span>Failed to fetch feedback response: {isAnswered.error.message}</span>;
  }

  if (isAnswered.data === null || isAnswered.data === undefined) {
    return <></>;
  }

  if (!isAnswered.data) {
    return (
      <SimpleGrid cols={1} className={styles.question}>
        <Paper shadow="md" p="md" className={styles.paper}>
          <Title order={4}>{question.question}</Title>
          <Group className={styles.question_group}>
            {shuffledChoices.map((value, index) => (
              <Button
                key={index}
                variant="light"
                color="teal"
                className={styles.button}
                onClick={() => handleSelectChoice(value)}
              >
                {value}
              </Button>
            ))}
          </Group>
        </Paper>
      </SimpleGrid>
    );
  }

  if (feedbackResponse.isError) {
    return <span>Failed to fetch feedback response: {feedbackResponse.error.message}</span>;
  }

  return (
    <SimpleGrid cols={1} className={styles.question}>
      <Paper shadow="md" p="md" className={styles.paper}>
        <Title order={4}>{question.question}</Title>
        <Group className={styles.question_group}>
          {feedbackResponse.data !== undefined &&
            shuffledChoices.map((value, index) => (
              <Button
                key={index}
                variant={value === feedbackResponse.data.answer ? "filled" : "outline"}
                color="teal"
                className={styles.no_pointer}
              >
                {value}
              </Button>
            ))}
          <Title order={6} className={styles.thanks}>
            Thanks for your answer!
          </Title>
        </Group>
      </Paper>
    </SimpleGrid>
  );
}
