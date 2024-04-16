import { Box } from "@mantine/core";
import { useQuery } from "@tanstack/react-query";
import React, { useEffect, useRef } from "react";

import { ChatProperties, Faqs, Message } from "@/components/chat";

import { fetchMessages } from "@/api/chat";

import styles from "./styles.module.css";

interface MessageFeedProps {
  courseId: string;
  chatId: string;
  readOnly: boolean;
}

export default function MessageFeed(props: MessageFeedProps) {
  const { courseId, chatId, readOnly } = props;
  const lastMessageRef = useRef<HTMLDivElement>(null);

  const { isError, data, error } = useQuery({
    queryKey: ["messages", courseId, chatId],
    queryFn: () => fetchMessages(courseId, chatId),
  });

  useEffect(() => {
    if (data && lastMessageRef.current) {
      const el = lastMessageRef.current;

      // wrapping the call in a timeout allows for a repaint
      // before triggering the scroll
      setTimeout(() => {
        el.scrollIntoView({ behavior: "smooth" });
      }, 0);
    }
  }, [data]);

  if (isError) {
    return <span>Error: {error.message}</span>;
  }

  if (data == null) {
    return <></>;
  }

  return (
    <Box className={styles.message_feed_container}>
      <div className={styles.message_feed}>
        <ChatProperties courseId={courseId} chatId={chatId} />

        {data.messages.length == 0 && <Faqs courseId={courseId} chatId={chatId} />}

        {data.messages.map((message, index) => (
          <div key={message.message_id} ref={index === data.messages.length - 1 ? lastMessageRef : null}>
            <Message
              initialMessage={message}
              courseId={courseId}
              chatId={chatId}
              readOnly={readOnly}
              showFeedbackLabel={
                index !== 0 && message.sender == "feedback" && data.messages[index - 1].sender !== "feedback"
              }
              showAfterFeedbackLabel={
                message.sender == "feedback" &&
                (index === data.messages.length - 1 || data.messages[index + 1].sender !== "feedback")
              }
            />
          </div>
        ))}
      </div>
    </Box>
  );
}
