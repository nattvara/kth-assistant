import { Container, Text, Timeline, Title } from "@mantine/core";
import { IconCheckbox, IconCylinder, IconMessageCircle, IconTool } from "@tabler/icons-react";

import styles from "./styles.module.css";

const HowItWorks = () => {
  return (
    <section id="how-it-works" className={styles.how_it_works}>
      <Container>
        <Title className={styles.title} order={1}>
          How it Works
        </Title>
        <Timeline active={4} bulletSize={44} lineWidth={4}>
          <Timeline.Item bullet={<IconCheckbox size={20} />} title="Register Your Course">
            <Text>Get your course set up with the Copilot.</Text>
          </Timeline.Item>

          <Timeline.Item bullet={<IconCylinder size={20} />} title="Index Course Rooms">
            <Text>Copilot keeps a fresh index of all course rooms.</Text>
          </Timeline.Item>

          <Timeline.Item bullet={<IconTool size={20} />} title="Add the Copilot">
            <Text>Use the &quot;Redirect tool&quot; in Canvas to add the Copilot to your course.</Text>
          </Timeline.Item>

          <Timeline.Item bullet={<IconMessageCircle size={20} />} title="Start Chatting">
            <Text>
              Students can start chatting with the Course Copilot to get help and enhance their learning experience.
            </Text>
          </Timeline.Item>
        </Timeline>
      </Container>
    </section>
  );
};

export default HowItWorks;
