import { useRouter } from "next/router";

import { ChatWindow } from "@/components/chat";

const CoursePage = () => {
  const router = useRouter();
  const { course_id, chat_id } = router.query;

  return (
    <ChatWindow courseId={course_id as string} chatId={chat_id as string} />
  );
};

export default CoursePage;
