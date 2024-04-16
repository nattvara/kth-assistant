import { Anchor, Button, Pill, Table } from "@mantine/core";
import { IconArrowRight } from "@tabler/icons-react";

import { ChatOverview } from "@/api/chat";

import styles from "./styles.module.css";

interface ChatsTableProps {
  courseId: string;
  chats: ChatOverview[];
}

export default function ChatsTable(props: ChatsTableProps) {
  const { chats, courseId } = props;

  const rows = chats.map((chat) => {
    const currentDate = new Date(chat.created_at);

    const date = currentDate.toISOString().slice(0, 10);
    const time = currentDate.toTimeString().slice(0, 5);

    return (
      <Table.Tr key={chat.chat_id}>
        <Table.Td>
          <Pill>{chat.user_id.substring(0, 5)}</Pill>
        </Table.Td>
        <Table.Td className={styles.min_130}>{date}</Table.Td>
        <Table.Td className={styles.min_130}>{time}</Table.Td>
        <Table.Td>
          <Pill>{chat.llm_model_name}</Pill>
        </Table.Td>
        <Table.Td>
          <Pill>{chat.index_type}</Pill>
        </Table.Td>
        <Table.Td>
          <Anchor href={`/course/${courseId}/chat/${chat.chat_id}`}>
            <Button variant="light" rightSection={<IconArrowRight size={14} />}>
              View the chat
            </Button>
          </Anchor>
        </Table.Td>
      </Table.Tr>
    );
  });

  return (
    <Table striped highlightOnHover>
      <Table.Thead>
        <Table.Tr>
          <Table.Th>User ID</Table.Th>
          <Table.Th>Date</Table.Th>
          <Table.Th>Time</Table.Th>
          <Table.Th>LLM Model</Table.Th>
          <Table.Th>RAG Index</Table.Th>
          <Table.Th>View Chat</Table.Th>
        </Table.Tr>
      </Table.Thead>
      <Table.Tbody>{rows}</Table.Tbody>
    </Table>
  );
}
