import { GetServerSidePropsContext } from "next";
import { serverSideTranslations } from "next-i18next/serverSideTranslations";

const IndexPage = () => {
  return <p>foo</p>;
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

export default IndexPage;
