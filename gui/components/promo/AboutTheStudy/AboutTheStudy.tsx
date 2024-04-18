import { Container, SimpleGrid, Text, Title } from "@mantine/core";

import styles from "./styles.module.css";

const AboutTheStudy = () => {
  return (
    <section id="about-the-study">
      <Container>
        <SimpleGrid cols={1}>
          <Title order={1} className={styles.title}>
            About the study
          </Title>
          <Text className={styles.text}>
            The study evaluates different tools and techniques for developing AI assistants, focusing specifically on
            the use of Large Language Models (LLMs) and Retrieval Augmented Generation (RAG) techniques, such as
            traditional search algorithms like TF/IDF and advanced vector embeddings. The goal is to ascertain which
            methods are most effective at accurately sourcing and managing course-specific information within a learning
            management system. This part of the study will help pinpoint the most efficient AI models and retrieval
            techniques to enhance educational experiences by facilitating better access to content.
          </Text>

          <Text className={styles.text}>
            Additionally, the study assesses student preferences for the functionality and effectiveness of these AI
            assistants. Through targeted surveys, it will gather both qualitative and quantitative feedback concerning
            the accuracy of information retrieval, the responsiveness of the AI systems, and overall user satisfaction.
            The results will provide crucial insights into which AI configurations are most aligned with user needs,
            guiding further development of AI applications in educational environments.
          </Text>
        </SimpleGrid>
      </Container>
    </section>
  );
};

export default AboutTheStudy;
