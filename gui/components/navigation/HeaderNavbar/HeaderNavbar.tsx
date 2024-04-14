import { AppShell, Burger, Button, Group, Pill, SimpleGrid, Skeleton } from "@mantine/core";
import { IconMessageCircle } from "@tabler/icons-react";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { MouseEventHandler, useEffect } from "react";

import { getSession } from "@/api/session";

interface HeaderNavbarProps {
  opened: boolean;
  toggle: MouseEventHandler<HTMLButtonElement>;
  courseId: string;
}

export default function HeaderNavbar(props: HeaderNavbarProps) {
  const { opened, toggle, courseId } = props;
  const { t } = useTranslation("common");
  const router = useRouter();

  const sessionQuery = useQuery({
    queryKey: ["session"],
    queryFn: () => getSession(),
  });

  const startNewChat = () => {
    router.push(`/course/${courseId}`);
  };

  useEffect(() => {
    sessionQuery.refetch();
  }, [router.pathname, sessionQuery]);

  if (!sessionQuery.data) {
    return <></>;
  }

  return (
    <>
      <AppShell.Header>
        <SimpleGrid cols={2} h="100%" w="100%" px="md">
          <Group>
            {sessionQuery.data.consent && <Burger opened={opened} onClick={toggle} size="sm" />}
            <Pill size="xl">{t("header.app_name")}</Pill>
          </Group>
          <Group justify="flex-end">
            {courseId !== undefined && sessionQuery.data.consent && (
              <Button variant="light" rightSection={<IconMessageCircle />} onClick={() => startNewChat()}>
                {t("header.new_chat")}
              </Button>
            )}
          </Group>
        </SimpleGrid>
      </AppShell.Header>

      <AppShell.Navbar p="md">
        <Skeleton h={28} mt="sm" animate={false} />
        <Skeleton h={28} mt="sm" animate={false} />
        <Skeleton h={28} mt="sm" animate={false} />
      </AppShell.Navbar>
    </>
  );
}
