import { SimpleGrid } from "@mantine/core";
import { GetServerSidePropsContext } from "next";
import { serverSideTranslations } from "next-i18next/serverSideTranslations";

import { AboutTheStudy, Demo, FeatureShowcase, Footer, Header, HowItWorks, Jumbo } from "@/components/promo";

const IndexPage = () => {
  return (
    <SimpleGrid cols={1}>
      <Header />
      <Jumbo />
      <Demo />
      <div id="features"></div>
      <FeatureShowcase
        title="Course Logistics Support"
        description="Course Copilot smoothly handles queries about deadlines, exams, lab assignments, and more."
        imageUrl="/images/feature_1.png"
        imageAlt="Illustration of Course Copilot answering a student's question about course deadlines"
        side={"right"}
        size="xl"
        withBorder={false}
      />
      <FeatureShowcase
        title="Finding Course Materials"
        description="Students can rely on Course Copilot to find books, lecture slides, and other course-related materials uploaded to the classroom."
        imageUrl="/images/feature_2.png"
        imageAlt="Image showing Course Copilot helping a student find the course literature."
        side={"left"}
        size="lg"
        withBorder={true}
      />
      <FeatureShowcase
        title="Help with Assignments and Problems"
        description="With access to labs and exercises, Course Copilot helps students find the right answers and solutions."
        imageUrl="/images/feature_3.png"
        imageAlt="Image of Course Copilot helping a student work through a lab exercise."
        side={"right"}
        size="lg"
        withBorder={true}
      />
      <HowItWorks />
      <AboutTheStudy />
      <Footer />
    </SimpleGrid>
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
