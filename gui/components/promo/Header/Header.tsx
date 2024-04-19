import { AppShell, Badge, Button, Center, SimpleGrid } from "@mantine/core";
import { IconMail, IconMovie } from "@tabler/icons-react";
import { useRouter } from "next/router";

import styles from "./styles.module.css";

const ContactEmail = "ludwigkr@kth.se";

export default function HeaderNavbar() {
  const router = useRouter();

  return (
    <AppShell.Header p="md">
      <SimpleGrid cols={2}>
        <Badge size="lg" radius={10} variant="light">
          Canvas AI Copilot
        </Badge>

        <Center>
          <Button
            leftSection={<IconMail size={14} />}
            className={styles.button}
            color="blue"
            component="a"
            href={`mailto:${ContactEmail}`}
          >
            Contact The Researcher
          </Button>
        </Center>
      </SimpleGrid>
    </AppShell.Header>
  );
}
