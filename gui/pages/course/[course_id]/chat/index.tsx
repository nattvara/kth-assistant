import { useRouter } from "next/router";

const ChatIndexPage = () => {
  const router = useRouter();
  const { course_id } = router.query;

  if (course_id == null) {
    return <></>;
  }

  router.push(`/course/${course_id}`);
  return <></>;
};

export default ChatIndexPage;
