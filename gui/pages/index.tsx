import { Blockquote, Grid } from "@mantine/core";
import { IconInfoCircle } from "@tabler/icons-react";
import { GetServerSidePropsContext } from "next";
import { serverSideTranslations } from "next-i18next/serverSideTranslations";

const IndexPage = () => {
  return (
    <Grid>
      <Grid.Col span={10} offset={1}>
        <Blockquote color="blue" cite="Canvas Copilot" icon={<IconInfoCircle />} mt="xl">
          No course selected.
        </Blockquote>
      </Grid.Col>
    </Grid>
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

export default IndexPage;
