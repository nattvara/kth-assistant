import { useQuery } from "@tanstack/react-query";
import { serverSideTranslations } from "next-i18next/serverSideTranslations";
import { useRouter } from "next/router";

import { ChatWindow } from "@/components/chat";

import { fetchChat } from "@/api/chat";

const ChatPage = () => {
  const router = useRouter();
  const { course_id, chat_id } = router.query;

  const { isError, data, error } = useQuery({
    queryKey: ["chat", course_id, chat_id],
    queryFn: () => fetchChat(course_id as string, chat_id as string),
  });

  if (!course_id) return <></>;

  if (!chat_id) return <></>;

  if (isError) {
    return <span>Error: {error.message}</span>;
  }

  if (data == null) {
    return <></>;
  }

  if (router.locale !== data.language) {
    router.push(router.pathname, router.asPath, { locale: data.language });
  }

  return <ChatWindow courseId={course_id as string} chatId={chat_id as string} />;
};

export async function getServerSideProps(context) {
  const { locale } = context;
  const translations = await serverSideTranslations(locale, ["input"]);

  return {
    props: {
      ...translations,
    },
  };
}

export default ChatPage;
