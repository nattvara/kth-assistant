import { Button, Collapse, Group, Notification, Paper, SimpleGrid, Text } from "@mantine/core";
import { notifications } from "@mantine/notifications";
import { IconExclamationCircle } from "@tabler/icons-react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";

import { Message } from "@/api/chat";
import { Feedback as FeedbackData, sendFeedback } from "@/api/feedback";
import { HttpError } from "@/api/http";

import styles from "./styles.module.css";

interface SelectFeedbackProps {
  message: Message;
  feedback: FeedbackData;
  withLabel: boolean;
  withPostLabel: boolean;
  courseId: string;
  chatId: string;
}

export function SelectFeedback(props: SelectFeedbackProps) {
  const { message, feedback, withLabel, withPostLabel, courseId, chatId } = props;
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
    <SimpleGrid cols={1} className={styles.feedback}>
      {withLabel && <p className={styles.label}>{t("feedback.label")}</p>}
      <Collapse in={answered} transitionDuration={300}>
        <Notification
          title={t("feedback.done")}
          withCloseButton={false}
          color="teal"
          className={styles.done}
        ></Notification>
      </Collapse>
      <Collapse in={!answered} transitionDuration={300}>
        <Paper shadow="sm" p="xs" className={styles.paper} withBorder>
          <Text className={styles.question}>{feedback.question}</Text>
          <Group className={styles.question_group}>
            {feedback.extra_data.choices.map((value, index) => (
              <Button
                key={index}
                variant="light"
                color="teal"
                size="xs"
                className={styles.button}
                onClick={() => sendMutation.mutate(value)}
                loading={sendMutation.isPending}
              >
                {value}
              </Button>
            ))}
          </Group>
        </Paper>
      </Collapse>
      {withPostLabel && <p className={styles.after}>{t("feedback.after")}</p>}
    </SimpleGrid>
  );
}
