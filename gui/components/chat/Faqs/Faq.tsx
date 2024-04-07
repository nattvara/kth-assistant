import { Blockquote, Paper } from "@mantine/core";
import { IconQuote } from "@tabler/icons-react";
import { useState } from "react";

import { Faq as FaqData } from "@/api/chat";

import styles from "./styles.module.css";

interface FaqProps {
  faq: FaqData;
}

export default function Faq(props: FaqProps) {
  const { faq } = props;
  const [hover, setHover] = useState(false);

  return (
    <Paper className={styles.paper} shadow={hover ? "xl" : "sm"} radius="xs">
      <Blockquote
        className={styles.quote}
        icon={<IconQuote />}
        onMouseEnter={() => setHover(true)}
        onMouseLeave={() => setHover(false)}
        color="blue"
      >
        {faq.question}
      </Blockquote>
    </Paper>
  );
}
