import { Button, Group, Textarea } from "@mantine/core";
import { notifications } from "@mantine/notifications";
import { IconExclamationCircle, IconSend } from "@tabler/icons-react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { sendMessage } from "@/api/chat";
import { HttpError } from "@/api/http";

import styles from "./styles.module.css";
import { useTranslation } from "next-i18next";

interface PromptProps {
  courseId: string;
  chatId: string;
}

export default function Prompt(props: PromptProps) {
  const { t } = useTranslation("input");
  const { courseId, chatId } = props;
  const queryClient = useQueryClient();
  const [message, setMessage] = useState("");

  const sendMutation = useMutation({
    mutationFn: (newMessage: string) => sendMessage(courseId, chatId, newMessage),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["messages", courseId, chatId],
      });
      setMessage("");
    },
    onError: (error: HttpError) => {
      console.error(error);
      notifications.show({
        title: "Failed to send message",
        color: "red",
        message: error.errorDetail,
        icon: <IconExclamationCircle />,
      });
    },
  });

  const handleSendMessage = () => {
    if (message.trim()) {
      sendMutation.mutate(message);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <Group grow wrap="nowrap" preventGrowOverflow={false} className={styles.group}>
      <Textarea
        placeholder={t("prompt.placeholder")}
        withAsterisk
        autosize
        minRows={1}
        className={styles.textarea}
        value={message}
        onChange={(e) => setMessage(e.currentTarget.value)}
        onKeyDown={handleKeyDown}
        disabled={sendMutation.isPending}
      />
      <Button
        className={styles.button}
        rightSection={<IconSend size={14} />}
        onClick={handleSendMessage}
        disabled={sendMutation.isPending}
        loading={sendMutation.isPending}
      >
        {t("prompt.button_text")}
      </Button>
    </Group>
  );
}
