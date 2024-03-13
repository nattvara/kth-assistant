import { Grid, SimpleGrid } from "@mantine/core";
import styles from "./styles.module.css";

interface MessageProps {
  sender: string;
  message: string;
}

export default function Message(props: MessageProps) {
  const { sender, message } = props;

  return (
    <SimpleGrid cols={1} className={styles.root}>
      <Grid>
        {sender}
      </Grid>
      <Grid>
        {message}
      </Grid>
    </SimpleGrid>
  );
}
