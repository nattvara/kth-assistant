import { Button, Center, Grid, Group, Text, Tooltip } from "@mantine/core";
import { notifications } from "@mantine/notifications";
import { IconExclamationCircle, IconThumbDown, IconThumbUp } from "@tabler/icons-react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";

import { Message } from "@/api/chat";
import { Feedback as FeedbackData, sendFeedback } from "@/api/feedback";
import { HttpError } from "@/api/http";

import styles from "./styles.module.css";

interface ThumbsFeedbackProps {
  message: Message;
  feedback: FeedbackData;
  courseId: string;
  chatId: string;
}

export function ThumbsFeedback(props: ThumbsFeedbackProps) {
  const { message, feedback, courseId, chatId } = props;
  const { t } = useTranslation("chat");
  const queryClient = useQueryClient();

  const answered = message.content !== null;

  const sendMutation = useMutation({
    mutationFn: (choice: string) => sendFeedback(message.feedback_id as string, choice),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["messages", courseId, chatId],
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

  return (
    <Grid className={styles.thumbs_feedback}>
      <Center inline>
        <Text className={`${styles.question} ${styles.thumbs_feedback_question}`}>{feedback.question}</Text>
        <Group className={styles.question_group}>
          {feedback.extra_data.choices.map((value, index) => (
            <Tooltip
              label={value === "thumbs_up" ? t("feedback.thumbs_up_tooltip") : t("feedback.thumbs_down_tooltip")}
              key={index}
            >
              <Button
                key={index}
                variant={message.content === value ? "" : "light"}
                color={value === "thumbs_up" ? "green" : "red"}
                size="xs"
                className={answered ? styles.no_pointer : ""}
                onClick={() => sendMutation.mutate(value)}
                loading={sendMutation.isPending}
              >
                {value === "thumbs_up" && <IconThumbUp />}
                {value === "thumbs_down" && <IconThumbDown />}
              </Button>
            </Tooltip>
          ))}
        </Group>
        {answered && (
          <span className={`${styles.question} ${styles.thumbs_done} ${styles.thumbs_feedback_question}`}>
            {t("feedback.done")}
          </span>
        )}
      </Center>
    </Grid>
  );
}
