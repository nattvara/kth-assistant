import { Group, MantineProvider, Skeleton } from "@mantine/core";
import { AppShell, Burger } from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import { Notifications } from '@mantine/notifications';
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import Head from "next/head";
import { useEffect, useState } from "react";
import Cookies from "js-cookie";
import "@mantine/core/styles.css";
import '@mantine/notifications/styles.css';

import { startSession, getSession } from "@/api/session";
import { theme } from "../theme";

export default function App({ Component, pageProps }: any) {
  const [ opened, { toggle } ] = useDisclosure();
  const queryClient = new QueryClient();
  const [ hasValidSession, setValidSession ] = useState(false);
  const sessionCookie = Cookies.get("session_id");

  useEffect(() => {
    const manageSession = async () => {

      const startNewSession = async () => {
        console.log("Starting new session");

        const newSession = await startSession();
        Cookies.set("session_id", newSession.public_id, { expires: 365 });
        await setValidSession(true);
      };

      if (!sessionCookie) {
        await startNewSession();
      } else {
        try {
          await getSession();
          await setValidSession(true);
        } catch (error: any) {
          if (error.response && error.response.status === 401) {
            await startNewSession();
          }
        }
      }
    };

    manageSession();
  }, [sessionCookie]);

  if (!hasValidSession) {
    return <></>;
  }

  return (
    <MantineProvider theme={theme}>
      <Notifications />
      <QueryClientProvider client={queryClient}>
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
      </QueryClientProvider>
    </MantineProvider>
  );
}
