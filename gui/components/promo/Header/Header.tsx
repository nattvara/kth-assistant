import { AppShell, Badge, Button, Center, SimpleGrid } from "@mantine/core";
import { IconMail } from "@tabler/icons-react";

import styles from "./styles.module.css";

export default function HeaderNavbar() {
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
            href="#contact"
          >
            Contact
          </Button>
        </Center>
      </SimpleGrid>
    </AppShell.Header>
  );
}
