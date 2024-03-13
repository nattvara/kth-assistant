import { Group, MantineProvider, Skeleton } from "@mantine/core";
import { AppShell, Burger } from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import Head from "next/head";
import "@mantine/core/styles.css";

import { theme } from "../theme";

export default function App({ Component, pageProps }: any) {
  const [opened, { toggle }] = useDisclosure();

  return (
    <MantineProvider theme={theme}>
      <Head>
        <title>KTH Assistant</title>
        <meta
          name="viewport"
          content="minimum-scale=1, initial-scale=1, width=device-width, user-scalable=no"
        />
        <link rel="shortcut icon" href="/favicon.svg" />
      </Head>
      <AppShell
        header={{ height: 60 }}
        navbar={{
          width: 300,
          breakpoint: "sm",
          collapsed: { mobile: !opened, desktop: !opened },
        }}
        padding="0"
      >
        <AppShell.Header>
          <Group h="100%" px="md">
            <Burger opened={opened} onClick={toggle} size="sm" />
            KTH Assistant
          </Group>
        </AppShell.Header>

        <AppShell.Navbar p="md">
          <Skeleton h={28} mt="sm" animate={false} />
          <Skeleton h={28} mt="sm" animate={false} />
          <Skeleton h={28} mt="sm" animate={false} />
        </AppShell.Navbar>

        <AppShell.Main>
          <Component {...pageProps} />
        </AppShell.Main>
      </AppShell>
    </MantineProvider>
  );
}
