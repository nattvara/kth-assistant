import { Container, SimpleGrid, Text, Title } from "@mantine/core";

import styles from "./styles.module.css";

const AboutTheStudy = () => {
  return (
    <section id="about-the-study" className={styles.section}>
      <Container>
        <SimpleGrid cols={1}>
          <Title order={1} className={styles.title}>
            About the study
          </Title>
          <Text className={styles.text}>
            The study evaluates various tools and techniques for developing AI assistants, with a special focus on the
            use of Large Language Models (LLMs) and Retrieval Augmented Generation (RAG) techniques like TF/IDF and
            advanced vector embeddings. The aim is to determine the most effective methods for accurately sourcing and
            managing course-specific information within a learning management system.
          </Text>

          <Text className={styles.text}>
            The study also evaluates student preferences for the functionality and effectiveness of these AI assistants
            through questions in the chat, collecting both qualitative and quantitative feedback on information
            retrieval accuracy, AI system responsiveness, and overall student satisfaction. The findings will provide
            vital insights into the AI configurations that best align with user needs, guiding further development of AI
            applications in educational settings.
          </Text>
        </SimpleGrid>
      </Container>
    </section>
  );
};

export default AboutTheStudy;
