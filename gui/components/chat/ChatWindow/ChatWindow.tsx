import { Box, SimpleGrid } from "@mantine/core";
import { MessageFeed } from "@/components/chat";
import { Prompt } from "@/components/input";
import styles from "./styles.module.css";

export default function ChatWindow() {
  return (
    <SimpleGrid cols={1}>
      <Box className={styles.message_feed_container}>
        <MessageFeed className={styles.message_feed} />
      </Box>
      <Box className={styles.prompt_container}>
        <Box className={styles.prompt_inner_container}>
          <Box className={styles.prompt}>
            <Prompt />
          </Box>
        </Box>
      </Box>
    </SimpleGrid>
  );
}
