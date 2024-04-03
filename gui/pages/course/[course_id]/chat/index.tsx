import { GetServerSidePropsContext } from "next";
import { serverSideTranslations } from "next-i18next/serverSideTranslations";
import { useRouter } from "next/router";

const ChatIndexPage = () => {
  const router = useRouter();
  const { course_id } = router.query;

  if (course_id == null) {
    return <></>;
  }

  router.push(`/course/${course_id}`);
  return <></>;
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

export default ChatIndexPage;
