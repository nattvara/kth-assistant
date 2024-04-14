import { Flex, Group, Loader } from "@mantine/core";
import { useQuery } from "@tanstack/react-query";
import { GetServerSidePropsContext } from "next";
import { serverSideTranslations } from "next-i18next/serverSideTranslations";
import { useRouter } from "next/router";
import { useEffect, useState } from "react";

import { GrantConsent } from "@/components/input";

import { fetchCourse, startChat } from "@/api/chat";
import { HttpError } from "@/api/http";
import { getSession } from "@/api/session";

const CoursePage = () => {
  const router = useRouter();
  const { course_id } = router.query;
  const [grantedConsent, setGrantedConsent] = useState<boolean | null>(null);

  const startChatQuery = useQuery({
    queryKey: ["startChat", course_id],
    queryFn: () => startChat(course_id as string),
    enabled: !!course_id && grantedConsent === true,
  });

  const sessionQuery = useQuery({
    queryKey: ["session"],
    queryFn: () => getSession(),
  });

  const courseQuery = useQuery({
    queryKey: ["course", course_id],
    queryFn: () => fetchCourse(course_id as string),
    enabled: !!course_id,
  });

  useEffect(() => {
    if (!courseQuery.data) return;

    if (router.locale !== courseQuery.data.language) {
      router.push(router.pathname, router.asPath, { locale: courseQuery.data.language });
    }
  }, [courseQuery.data, router]);

  useEffect(() => {
    if (!sessionQuery.data) return;
    setGrantedConsent(sessionQuery.data.consent);

    if (startChatQuery.data && startChatQuery.data.public_id) {
      router.push(`/course/${course_id}/chat/${startChatQuery.data.public_id}`);
    }
  }, [startChatQuery.data, sessionQuery.data, course_id, router, grantedConsent]);

  if (grantedConsent === false) {
    return <GrantConsent></GrantConsent>;
  }

  if (courseQuery.isFetching) {
    return (
      <Flex direction={{ base: "column", sm: "row" }} gap={{ base: "sm", sm: "lg" }} justify={{ sm: "center" }}>
        <Group justify="center">
          <p>Loading</p>
          <Loader size="sm" type="dots" color="black" />
        </Group>
      </Flex>
    );
  }

  if (startChatQuery.isFetching) {
    return (
      <Flex direction={{ base: "column", sm: "row" }} gap={{ base: "sm", sm: "lg" }} justify={{ sm: "center" }}>
        <Group justify="center">
          <p>Starting chat</p>
          <Loader size="sm" type="dots" color="black" />
        </Group>
      </Flex>
    );
  }

  if (startChatQuery.isError) {
    if ((startChatQuery.error as HttpError).code === 404) {
      return <span>Error: Course not found</span>;
    }

    return <span>Error: {startChatQuery.error.message}</span>;
  }

  return <span></span>;
};

export async function getServerSideProps(context: GetServerSidePropsContext) {
  const { locale } = context;
  const translations = await serverSideTranslations(locale as string, ["common", "input"]);

  return {
    props: {
      ...translations,
    },
  };
}

export default CoursePage;
