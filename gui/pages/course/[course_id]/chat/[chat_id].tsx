import { Button, Flex, Group, SimpleGrid, Space, Title } from "@mantine/core";
import { useQuery } from "@tanstack/react-query";
import { GetServerSidePropsContext } from "next";
import { serverSideTranslations } from "next-i18next/serverSideTranslations";
import { useRouter } from "next/router";

import { ChatWindow } from "@/components/chat";

import { ChatNotFoundError, fetchChat } from "@/api/chat";
import { getSession } from "@/api/session";

const ChatPage = () => {
  const router = useRouter();
  const { course_id, chat_id } = router.query;

  const { isError, data, error } = useQuery({
    queryKey: ["chat", course_id, chat_id],
    queryFn: () => fetchChat(course_id as string, chat_id as string),
    retryDelay: 500,
  });

  const sessionQuery = useQuery({
    queryKey: ["session"],
    queryFn: () => getSession(),
  });

  const startNewChat = () => {
    router.push(`/course/${course_id}/chat`);
  };

  if (!course_id) return <></>;

  if (!chat_id) return <></>;

  if (isError) {
    if (error instanceof ChatNotFoundError) {
      return (
        <Flex direction={{ base: "column", sm: "row" }} gap={{ base: "sm", sm: "lg" }} justify={{ sm: "center" }}>
          <Group justify="center">
            <SimpleGrid cols={1}>
              <Space h="xl" />
              <Title order={3}>This chat was not found</Title>
              <Button color="blue" size="md" onClick={() => startNewChat()}>
                Click here to start a new one!
              </Button>
            </SimpleGrid>
          </Group>
        </Flex>
      );
    }
    return <span>Error: {error.message}</span>;
  }

  if (data == null) {
    return <></>;
  }

  if (router.locale !== data.language) {
    router.push(router.pathname, router.asPath, { locale: data.language });
  }

  if (sessionQuery.data && sessionQuery.data.consent === false) {
    router.push(`/course/${course_id}`);
  }

  return <ChatWindow courseId={course_id as string} chatId={chat_id as string} readOnly={data.read_only} />;
};

export async function getServerSideProps(context: GetServerSidePropsContext) {
  const { locale } = context;
  const translations = await serverSideTranslations(locale as string, ["common", "input", "chat"]);

  return {
    props: {
      ...translations,
    },
  };
}

export default ChatPage;
