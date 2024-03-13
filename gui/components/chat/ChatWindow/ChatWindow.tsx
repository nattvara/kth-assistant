import { Box, SimpleGrid } from "@mantine/core";
import { MessageFeed } from "@/components/chat";
import { Prompt } from "@/components/input";
import styles from "./styles.module.css";

export default function ChatWindow() {
  return (
    <SimpleGrid cols={1} className={styles.root}>
      <MessageFeed className={styles.message_feed} />
      <Box className={styles.prompt}>
        <Prompt />
      </Box>
    </SimpleGrid>
  );
}
