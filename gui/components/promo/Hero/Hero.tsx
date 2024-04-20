import { Anchor, Button, Container, Space, Text, Title } from "@mantine/core";
import { useMediaQuery } from "@mantine/hooks";
import { IconArrowDown } from "@tabler/icons-react";
import { useRouter } from "next/router";

import styles from "./styles.module.css";

const Hero = () => {
  const router = useRouter();
  const isLargeScreen = useMediaQuery("(min-width: 56.25em)");

  return (
    <section id="hero" className={styles.hero}>
      <Container fluid>
        <div className={styles.hero_content}>
          <div className={styles.title}>
            <Title className={styles.title_text}>
              <span className={styles.primary_color}>Canvas AI Copilot</span> - an AI Powered Assistant in Canvas.
            </Title>
          </div>
          <div className={styles.description_text}>
            <Text size="xl">
              Canvas AI Copilot is a smart assistant integrated into Canvas course rooms, designed to enhance the
              E-learning experience by creating a favorable learning environment. This tool is part of a master thesis
              at<span> </span>
              <Anchor href="https://intra.kth.se/utbildning/e-larande" target="_blank">
                KTH&apos;s E-Learning unit
              </Anchor>
              , exploring how chatbots can facilitate E-learning, conducted during
              <strong> the spring term of 2024</strong>.
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

export default Hero;
