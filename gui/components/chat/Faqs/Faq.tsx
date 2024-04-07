import { Blockquote, Paper } from "@mantine/core";
import { notifications } from "@mantine/notifications";
import { IconExclamationCircle, IconQuote } from "@tabler/icons-react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { Faq as FaqData, sendMessageUsingFaq } from "@/api/chat";
import { HttpError } from "@/api/http";

import styles from "./styles.module.css";

interface FaqProps {
  faq: FaqData;
  courseId: string;
  chatId: string;
}

export default function Faq(props: FaqProps) {
  const { faq, courseId, chatId } = props;
  const [hover, setHover] = useState(false);
  const queryClient = useQueryClient();

  const sendMutation = useMutation({
    mutationFn: (faqId: string) => sendMessageUsingFaq(courseId, chatId, faqId),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["messages", courseId, chatId],
      });
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

  const handleClick = () => {
    sendMutation.mutate(faq.faq_id);
  };

  return (
    <Paper className={styles.paper} shadow={hover ? "xl" : "sm"} radius="xs">
      <Blockquote
        className={styles.quote}
        icon={<IconQuote />}
        onMouseEnter={() => setHover(true)}
        onMouseLeave={() => setHover(false)}
        onClick={handleClick}
        color="blue"
      >
        {faq.question}
      </Blockquote>
    </Paper>
  );
}
