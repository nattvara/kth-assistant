import { Alert, Group, Image, LoadingOverlay, SimpleGrid, Space, Text } from "@mantine/core";
import { IconBrain } from "@tabler/icons-react";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "next-i18next";

import { fetchChat } from "@/api/chat";

import styles from "./styles.module.css";

interface ChatPropertiesProps {
  courseId: string;
  chatId: string;
}

export default function ChatProperties(props: ChatPropertiesProps) {
  const { courseId, chatId } = props;
  const { t, i18n } = useTranslation("chat");

  const { isFetching, isError, data, error } = useQuery({
    queryKey: ["chat", courseId, chatId],
    queryFn: () => fetchChat(courseId, chatId),
  });

  if (isError) {
    return <span>Error: {error.message}</span>;
  }

  if (data == null) {
    return <></>;
  }

  const modelAndIndexType = t("properties.model_and_index_type", {
    modelName: data.llm_model_name,
    indexType: data.index_type,
  });

  return (
    <SimpleGrid cols={1}>
      <Alert variant="light" color="gray" title={t("properties.title")} icon={<IconBrain />} className={styles.alert}>
        <LoadingOverlay visible={isFetching} zIndex={1000} overlayProps={{ radius: "sm", blur: 2 }} />
        <div dangerouslySetInnerHTML={{ __html: modelAndIndexType }} />

        <Space h="md" />

        <div>
          {t("properties.course_room")}: <strong>{data.course_name}</strong>
        </div>

        <Space h="sm" />

        <Group align="center">
          {i18n.language === "en" && (
            <Image src="/flag-en.svg" radius="sm" h={30} w="auto" fit="contain" alt="UK flag" />
          )}
          {i18n.language === "sv" && (
            <Image src="/flag-sv.svg" radius="sm" h={30} w="auto" fit="contain" alt="Swedish flag" />
          )}
          <Text>{t("properties.language")}</Text>
        </Group>
      </Alert>
    </SimpleGrid>
  );
}
