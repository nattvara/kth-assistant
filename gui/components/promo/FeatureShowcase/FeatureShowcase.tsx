import { Container, Grid, Image, Text, Title } from "@mantine/core";
import { useMediaQuery } from "@mantine/hooks";

import styles from "./styles.module.css";

interface FeatureShowcaseProps {
  title: string;
  description: string;
  imageUrl: string;
  imageAlt: string;
  side: "right" | "left";
  size: "xl" | "lg";
  withBorder: boolean;
}

const FeatureShowcase = ({ title, description, imageUrl, imageAlt, side, size, withBorder }: FeatureShowcaseProps) => {
  const isLargeScreen = useMediaQuery("(min-width: 56.25em)");
  const textColumnOrder = !isLargeScreen ? 1 : side === "right" ? 1 : 2;
  const imageColumnOrder = !isLargeScreen ? 2 : side === "right" ? 2 : 1;

  return (
    <section className={styles.section}>
      <Container>
        <Grid gutter="xl" align="center">
          <Grid.Col className={styles.text_col} span={isLargeScreen ? 6 : 12} order={textColumnOrder}>
            <Title className={styles.title} order={1}>
              {title}
            </Title>
            <Text className={styles.description}>{description}</Text>
          </Grid.Col>
          <Grid.Col span={isLargeScreen ? 6 : 12} order={imageColumnOrder}>
            {side === "right" && (
              <Image
                src={imageUrl}
                alt={imageAlt}
                className={`${styles.image} ${size === "xl" ? styles.xl : ""} ${size === "lg" ? styles.lg : ""} ${withBorder ? styles.with_border : ""}`}
              />
            )}
            {side === "left" && isLargeScreen && (
              <div className={styles.container}>
                <Image
                  src={imageUrl}
                  alt={imageAlt}
                  className={`${styles.image} ${styles.grow_left} ${size === "xl" ? styles.xl : ""} ${size === "lg" ? styles.lg : ""} ${withBorder ? styles.with_border : ""}`}
                />
              </div>
            )}
            {side === "left" && !isLargeScreen && (
              <Image
                src={imageUrl}
                alt={imageAlt}
                className={`${styles.image} ${size === "xl" ? styles.xl : ""} ${size === "lg" ? styles.lg : ""} ${withBorder ? styles.with_border : ""}`}
              />
            )}
          </Grid.Col>
        </Grid>
      </Container>
    </section>
  );
};

export default FeatureShowcase;
