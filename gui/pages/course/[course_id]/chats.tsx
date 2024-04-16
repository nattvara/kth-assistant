import { Flex, Group, Loader, Paper, SimpleGrid, Space, Text, Title } from "@mantine/core";
import { useQuery } from "@tanstack/react-query";
import { GetServerSidePropsContext } from "next";
import { serverSideTranslations } from "next-i18next/serverSideTranslations";
import { useRouter } from "next/router";

import { ChatsTable } from "@/components/tables";

import { fetchChats, fetchCourse } from "@/api/chat";

const CourseChatsPage = () => {
  const router = useRouter();
  const { course_id } = router.query;

  const courseQuery = useQuery({
    queryKey: ["course", course_id],
    queryFn: () => fetchCourse(course_id as string),
    enabled: course_id !== null,
  });

  const chatsQuery = useQuery({
    queryKey: ["chats", course_id],
    queryFn: () => fetchChats(course_id as string),
    enabled: course_id !== null,
  });

  if (courseQuery.isError) {
    return <span>Course Error: {courseQuery.error.message}</span>;
  }

  if (chatsQuery.isError) {
    return <span>Chats Error: {chatsQuery.error.message}</span>;
  }

  if (courseQuery.isFetching || chatsQuery.isFetching) {
    return (
      <Flex direction={{ base: "column", sm: "row" }} gap={{ base: "sm", sm: "lg" }} justify={{ sm: "center" }}>
        <Group justify="center">
          <p>Loading chats</p>
          <Loader size="sm" type="dots" color="black" />
        </Group>
      </Flex>
    );
  }

  if (courseQuery.data === null || chatsQuery.data === null) {
    return <></>;
  }

  if (courseQuery.data === undefined || chatsQuery.data === undefined) {
    return <></>;
  }

  return (
    <Paper p="xl">
      <SimpleGrid cols={1}>
        <Title>{courseQuery.data.name}</Title>
        <Text>
          <strong>{chatsQuery.data.chats.length}</strong> chats in the course
        </Text>
        <ChatsTable courseId={course_id as string} chats={chatsQuery.data.chats} />
      </SimpleGrid>
      {[...Array(10)].map((_, i) => (
        <Space key={i} h="xl" />
      ))}
    </Paper>
  );
};

export async function getServerSideProps(context: GetServerSidePropsContext) {
  const { locale } = context;
  const translations = await serverSideTranslations(locale as string, ["common"]);

  return {
    props: {
      ...translations,
    },
  };
}

export default CourseChatsPage;
