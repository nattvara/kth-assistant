import { Grid, SimpleGrid } from "@mantine/core";
import styles from "./styles.module.css";

interface MessageProps {
  sender: string;
  content: string;
}

export default function Message(props: MessageProps) {
  const { sender, content } = props;

  return (
    <SimpleGrid cols={1} className={styles.root}>
      <Grid>
        <strong>{sender}</strong>
      </Grid>
      <Grid>
        {content}
      </Grid>
    </SimpleGrid>
  );
}
