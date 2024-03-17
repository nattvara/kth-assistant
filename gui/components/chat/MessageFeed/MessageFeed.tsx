import React, { useEffect, useRef } from 'react';
import { fetchMessages } from "@/api/chat";
import { Message } from "@/components/chat";
import { useQuery } from "@tanstack/react-query";
import styles from "./styles.module.css";
import { Box } from "@mantine/core";

interface MessageFeedProps {
  courseId: string;
  chatId: string;
}

export default function MessageFeed(props: MessageFeedProps) {
  const { courseId, chatId } = props;
  const lastMessageRef = useRef<HTMLDivElement>(null);

  const { isError, data, error } = useQuery({
    queryKey: ["messages", courseId, chatId],
    queryFn: () => fetchMessages(courseId, chatId),
  });

  useEffect(() => {
    if (data && lastMessageRef.current) {
      const el = lastMessageRef.current;
      el.scrollIntoView({ behavior: 'smooth' });
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
        {data.messages.map((message, index) => (
          <div
            key={message.message_id}
            ref={index === data.messages.length - 1 ? lastMessageRef : null}
          >
            <Message
              sender={message.sender}
              content={message.content}
            />
          </div>
        ))}
      </div>
    </Box>
  );
}
