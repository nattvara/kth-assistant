import { AppShell, Badge, Button, Center, SimpleGrid } from "@mantine/core";
import { IconMovie } from "@tabler/icons-react";
import { useRouter } from "next/router";

import styles from "./styles.module.css";

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
            color="blue"
            className={styles.button}
            rightSection={<IconMovie />}
            onClick={() => router.push("#demo")}
          >
            Look at the demo
          </Button>
        </Center>
      </SimpleGrid>
    </AppShell.Header>
  );
}
