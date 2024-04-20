import { Anchor, Container, Grid, SimpleGrid, Space, Text } from "@mantine/core";

import styles from "./styles.module.css";

const ContactEmail = "ludwigkr@kth.se";
const SupervisorOneProfile = "https://www.kth.se/profile/mwelle";
const SupervisorTwoProfile = "https://www.kth.se/profile/fen";

const Footer = () => {
  return (
    <footer id="contact" className={styles.footer}>
      <Container>
        <Grid gutter={0}>
          <Grid.Col span={12}>
            <Space h="xl" />
            <Text size="xl" mb="md">
              Course Copilot
            </Text>
            <Text mb="xs">This project is part of a master&apos;s thesis at KTH Royal Institute of Technology.</Text>
            <Space h="xl" />
            <SimpleGrid cols={1}>
              <span>
                <strong>Student</strong>: Ludwig Kristoffersson <span> </span>
                <Anchor href={`mailto:${ContactEmail}`} target="_blank">
                  {ContactEmail}
                </Anchor>
              </span>
              <span>
                <strong>Supervisor</strong>:{" "}
                <Anchor href={SupervisorOneProfile} target="_blank">
                  Michael Welle
                </Anchor>
              </span>
              <span>
                <strong>Supervisor</strong>:{" "}
                <Anchor href={SupervisorTwoProfile} target="_blank">
                  Fredrik Enoksson
                </Anchor>
              </span>
            </SimpleGrid>
          </Grid.Col>
        </Grid>
      </Container>
    </footer>
  );
};

export default Footer;
