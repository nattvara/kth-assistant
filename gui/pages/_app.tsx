import { Alert, AppShell, MantineProvider } from "@mantine/core";
import "@mantine/core/styles.css";
import { useDisclosure } from "@mantine/hooks";
import { Notifications } from "@mantine/notifications";
import "@mantine/notifications/styles.css";
import { IconPlugConnectedX } from "@tabler/icons-react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import Cookies from "js-cookie";
import { appWithTranslation, useTranslation } from "next-i18next";
import { AppProps } from "next/app";
import Head from "next/head";
import { useRouter } from "next/router";
import { useEffect, useRef, useState } from "react";

import { HeaderNavbar } from "@/components/navigation";

import { HttpError } from "@/api/http";
import { getSession, startSession } from "@/api/session";

import { theme } from "../theme";

function App({ Component, pageProps }: AppProps) {
  const router = useRouter();
  const { t } = useTranslation("common");
  const { course_id } = router.query;
  const [opened, { toggle }] = useDisclosure();
  const queryClient = new QueryClient();
  const [hasValidSession, setValidSession] = useState<null | boolean>(null);
  const sessionInitiated = useRef(false);

  useEffect(() => {
    const manageSession = async () => {
      if (!sessionInitiated.current) {
        sessionInitiated.current = true;

        const sessionCookie = Cookies.get("session_id");
        const startNewSession = async () => {
          console.log("Starting new session");

          const newSession = await startSession();
          Cookies.set("session_id", newSession.public_id, {
            expires: 365,
            sameSite: 'None',
            secure: true
          });
          setValidSession(true);
        };

        if (!sessionCookie) {
          await startNewSession();
        } else {
          try {
            await getSession();
            setValidSession(true);
          } catch (error) {
            setValidSession(false);
            const typedError = error as HttpError;
            if (typedError.statusCode === 401) {
              await startNewSession();
              setValidSession(true);
            }
          }
        }

        sessionInitiated.current = false;
      }
    };

    manageSession();
  }, []);

  return (
    <MantineProvider theme={theme}>
      <Notifications />
      <QueryClientProvider client={queryClient}>
        <Head>
          <title>{t("header.app_name")}</title>
          <meta name="viewport" content="minimum-scale=1, initial-scale=1, width=device-width, user-scalable=no" />
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
          <HeaderNavbar opened={opened} toggle={toggle} courseId={course_id as string}></HeaderNavbar>
          <AppShell.Main>
            {hasValidSession && <Component {...pageProps} />}
            {!hasValidSession && hasValidSession !== null && (
              <Alert variant="light" color="red" title="Failed to connect to cloud" icon={<IconPlugConnectedX />}>
                There is no valid session. The application is most likely misconfigured.
              </Alert>
            )}
          </AppShell.Main>
        </AppShell>
      </QueryClientProvider>
    </MantineProvider>
  );
}

export default appWithTranslation(App);
