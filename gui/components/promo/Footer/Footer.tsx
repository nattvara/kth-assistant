import { Button, Container, Grid, Space, Text } from "@mantine/core";
import { IconMail } from "@tabler/icons-react";

import styles from "./styles.module.css";

const ContactEmail = "ludwigkr@kth.se";

const Footer = () => {
  return (
    <footer className={styles.footer}>
      <Container>
        <Grid gutter={0}>
          <Grid.Col span={5}>
            <Space h="xl" />
            <Text size="xl" mb="md">
              Course Copilot
            </Text>
            <Text mb="xs">This project is part of a master&apos;s thesis at KTH Royal Institute of Technology.</Text>
            <Space h="xl" />
            <Space h="xl" />
          </Grid.Col>
          <Grid.Col span={5} offset={2}>
            <Space h="xl" />
            <Space h="xl" />
            <Button
              leftSection={<IconMail size={14} />}
              variant="default"
              component="a"
              href={`mailto:${ContactEmail}`}
            >
              Contact Researcher
            </Button>
          </Grid.Col>
        </Grid>
      </Container>
    </footer>
  );
};

export default Footer;
