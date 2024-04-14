import { Anchor, Blockquote, Button, Group, Text, Title } from "@mantine/core";
import { notifications } from "@mantine/notifications";
import { IconExclamationCircle } from "@tabler/icons-react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "next-i18next";

import { HttpError } from "@/api/http";
import { grantConsent } from "@/api/session";

import styles from "./styles.module.css";

const ContactEmail = "ludwigkr@kth.se";

export default function GrantConsent() {
  const { t } = useTranslation("input");
  const queryClient = useQueryClient();

  const sendMutation = useMutation({
    mutationFn: () => grantConsent(),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["session"],
      });
    },
    onError: (error: HttpError) => {
      console.error(error);
      notifications.show({
        title: "Failed to send consent, please try again!",
        color: "red",
        message: error.errorDetail,
        icon: <IconExclamationCircle />,
      });
    },
  });

  return (
    <Group grow wrap="nowrap" preventGrowOverflow={false} className={styles.blockquote_container}>
      <Blockquote className={styles.blockquote}>
        <Title order={4} className={styles.title}>
          {t("consent.title")}
        </Title>
        <Text className={styles.paragraph}>{t("consent.subtitle")}</Text>

        <Title order={5} className={styles.section}>
          {t("consent.sections.purpose.title")}
        </Title>
        <Text className={styles.paragraph}>{t("consent.sections.purpose.description")}</Text>

        <Title order={5} className={styles.section}>
          {t("consent.sections.data.title")}
        </Title>
        <Text className={styles.paragraph}>{t("consent.sections.data.description")}</Text>

        <Title order={5} className={styles.section}>
          {t("consent.sections.participation.title")}
        </Title>
        <Text className={styles.paragraph}>
          <strong>{t("consent.sections.participation.description_part_1")}</strong>
          {t("consent.sections.participation.description_part_2")}
          <Anchor href={`mailto:${ContactEmail}`} target="_blank">
            {t("consent.sections.participation.description_part_3")}
          </Anchor>
          {t("consent.sections.participation.description_part_4")}
        </Text>

        <Button color="teal" size="md" onClick={() => sendMutation.mutate()} loading={sendMutation.isPending}>
          {t("consent.button")}
        </Button>
      </Blockquote>
    </Group>
  );
}
