import { useRouter } from "next/router";
import { Flex } from "@mantine/core";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { ChatWindow } from "@/components/chat";
import { startChat } from "@/api/chat";
import { useEffect } from "react";

const CoursePage = () => {
  const router = useRouter();
  const { course_id } = router.query;

  const { isFetching, isError, data, error } = useQuery({
    queryKey: ["startChat", course_id],
    queryFn: () => startChat(course_id as string),
    enabled: !!course_id,
  });

  useEffect(() => {
    if (data && data.public_id) {
      router.push(`/course/${course_id}/chat/${data.public_id}`);
    }
  }, [data, course_id, router]);

  if (isFetching) {
    return (
      <Flex
        direction={{ base: "column", sm: "row" }}
        gap={{ base: "sm", sm: "lg" }}
        justify={{ sm: "center" }}
      >
        <p>Starting chat...</p>
      </Flex>
    );
  }

  if (isError) {
    return <span>Error: {error.message}</span>
  }

  return <span></span>;
};

export default CoursePage;
