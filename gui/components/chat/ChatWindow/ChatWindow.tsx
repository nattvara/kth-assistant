import { Box, SimpleGrid } from "@mantine/core";
import { MessageFeed } from "@/components/chat";
import { Prompt } from "@/components/input";
import styles from "./styles.module.css";

interface ChatWindowProps {
  courseId: string;
  chatId: string;
}

export default function ChatWindow(props: ChatWindowProps) {
  const { courseId, chatId } = props;

  return (
    <SimpleGrid cols={1}>
      <MessageFeed courseId={courseId} chatId={chatId} />
      <Box className={styles.prompt_container}>
        <Box className={styles.prompt_inner_container}>
          <Box className={styles.prompt}>
            <Prompt courseId={courseId} chatId={chatId} />
          </Box>
        </Box>
      </Box>
    </SimpleGrid>
  );
}
