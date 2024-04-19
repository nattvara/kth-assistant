import { Button, Container, Space, Text, Title } from "@mantine/core";
import { useMediaQuery } from "@mantine/hooks";
import { IconArrowDown } from "@tabler/icons-react";
import { useRouter } from "next/router";

import styles from "./styles.module.css";

const Jumbo = () => {
  const router = useRouter();
  const isLargeScreen = useMediaQuery("(min-width: 56.25em)");

  return (
    <section id="jumbo" className={styles.jumbo}>
      <Container fluid>
        <div className={styles.jumbo_content}>
          <div className={styles.title}>
            <Title className={styles.title_text}>
              <span className={styles.primary_color}>Canvas AI Copilot</span> - an AI Powered Assistant in Canvas.
            </Title>
          </div>

          <div className={styles.description_text}>
            <Text size="xl">
              Canvas AI Copilot is a smart assistant in Canvas course rooms, designed to answer student questions
              effectively. This tool is part of a master thesis on how chatbots can enhance E-learning.
            </Text>
          </div>

          {isLargeScreen && (
            <div className={styles.buttons}>
              <Button
                rightSection={<IconArrowDown size={16} />}
                radius="lg"
                size="md"
                onClick={() => router.push("#demo")}
              >
                View a demo
              </Button>

              <Button variant="default" radius="lg" size="md" onClick={() => router.push("#features")}>
                What it can help with
              </Button>
            </div>
          )}
          {!isLargeScreen && (
            <>
              <div className={styles.buttons}>
                <Button
                  rightSection={<IconArrowDown size={16} />}
                  radius="lg"
                  size="md"
                  onClick={() => router.push("#demo")}
                >
                  View a demo
                </Button>
              </div>
              <Space h="lg" />
              <div className={styles.buttons}>
                <Button variant="default" radius="lg" size="md" onClick={() => router.push("#features")}>
                  What it can help with
                </Button>
              </div>
            </>
          )}
        </div>
      </Container>
    </section>
  );
};

export default Jumbo;
