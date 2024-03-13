import { Button, Group, Textarea } from "@mantine/core";
import { IconMessage, IconSend } from "@tabler/icons-react";
import styles from "./styles.module.css";

export default function Prompt() {
  return (
    <Group grow wrap="nowrap" preventGrowOverflow={false} className={styles.group}>
      <Textarea
        placeholder="Message KTH Assistant"
        withAsterisk
        autosize
        minRows={1}
        className={styles.textarea}
      />
      <Button className={styles.button} rightSection={<IconSend size={14} />}>Send</Button>
    </Group>
  );
}
