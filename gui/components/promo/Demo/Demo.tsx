import { Container, SimpleGrid, Title } from "@mantine/core";

import styles from "./styles.module.css";

const Demo = () => {
  return (
    <section id="demo" className={styles.demo}>
      <Container>
        <SimpleGrid cols={1}>
          <Title order={1} className={styles.title}>
            A Demo of the Copilot
          </Title>
          <div className={styles.video}>
            <iframe
              className={styles.iframe}
              width="100%"
              height="500"
              src="https://www.youtube.com/embed/spdZ4jwI8mo"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
              title="Embedded youtube"
            ></iframe>
          </div>
        </SimpleGrid>
      </Container>
    </section>
  );
};

export default Demo;
