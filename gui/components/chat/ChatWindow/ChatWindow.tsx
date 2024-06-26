import { Box, SimpleGrid } from "@mantine/core";

import { MessageFeed } from "@/components/chat";
import { Prompt } from "@/components/input";

import styles from "./styles.module.css";

interface ChatWindowProps {
  courseId: string;
  chatId: string;
  readOnly: boolean;
}

export default function ChatWindow(props: ChatWindowProps) {
  const { courseId, chatId, readOnly } = props;

  return (
    <SimpleGrid cols={1}>
      <MessageFeed courseId={courseId} chatId={chatId} readOnly={readOnly} />
      <Box className={styles.prompt_container}>
        <Box className={styles.prompt_inner_container}>
          <Box className={styles.prompt}>{!readOnly && <Prompt courseId={courseId} chatId={chatId} />}</Box>
        </Box>
      </Box>
    </SimpleGrid>
  );
}
