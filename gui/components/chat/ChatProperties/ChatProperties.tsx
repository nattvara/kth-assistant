import { Alert, LoadingOverlay, SimpleGrid } from "@mantine/core";
import { IconBrain } from "@tabler/icons-react";
import { useQuery } from "@tanstack/react-query";

import { fetchChat } from "@/api/chat";

import styles from "./styles.module.css";

interface ChatPropertiesProps {
  courseId: string;
  chatId: string;
}

export default function ChatProperties(props: ChatPropertiesProps) {
  const { courseId, chatId } = props;

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

  return (
    <SimpleGrid cols={1}>
      <Alert variant="light" color="gray" title="Chat Properties" icon={<IconBrain />} className={styles.alert}>
        <LoadingOverlay visible={isFetching} zIndex={1000} overlayProps={{ radius: "sm", blur: 2 }} />
        This chat is using the model <strong>{data.llm_model_name}</strong> and <strong>{data.index_type}</strong> as index.
      </Alert>
    </SimpleGrid>
  );
}
