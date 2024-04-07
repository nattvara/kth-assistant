import { Group, SimpleGrid, Title } from "@mantine/core";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "next-i18next";

import { fetchChat } from "@/api/chat";

import Faq from "./Faq";
import styles from "./styles.module.css";

interface FaqsProps {
  courseId: string;
  chatId: string;
}

export default function Faqs(props: FaqsProps) {
  const { courseId, chatId } = props;
  const { t } = useTranslation("chat");

  const { isError, data, error } = useQuery({
    queryKey: ["chat", courseId, chatId],
    queryFn: () => fetchChat(courseId, chatId),
  });

  if (isError) {
    return <span>Error: {error.message}</span>;
  }

  if (data == null) {
    return <></>;
  }

  const randomFaqs = data.faqs.sort(() => 0.5 - Math.random()).slice(0, 4);

  return (
    <Group className={styles.root}>
      <Title order={4} className={styles.title}>
        {t("faqs.title")}
      </Title>
      <SimpleGrid cols={2} className={styles.grid}>
        {randomFaqs.map((faq) => (
          <Faq faq={faq} key={faq.faq_id} />
        ))}
      </SimpleGrid>
    </Group>
  );
}
