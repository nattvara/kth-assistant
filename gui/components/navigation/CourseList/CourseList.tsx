import { Button, SimpleGrid, Title } from "@mantine/core";
import { useQuery } from "@tanstack/react-query";

import { fetchCourses } from "@/api/admin";

import styles from "./styles.module.css";

export default function CourseList() {
  const coursesQuery = useQuery({
    queryKey: ["courses"],
    queryFn: () => fetchCourses(),
  });

  if (!coursesQuery.data) {
    return <></>;
  }

  if (coursesQuery.data.courses.length === 0) {
    return <></>;
  }

  return (
    <SimpleGrid cols={1} className={styles.root}>
      <Title order={4}>Courses</Title>
      {coursesQuery.data.courses.map((course) => (
        <Button
          key={course.canvas_id}
          variant="light"
          size="xs"
          component="a"
          href={`/course/${course.canvas_id}/chats`}
          target="_blank"
        >
          {course.name}
        </Button>
      ))}
    </SimpleGrid>
  );
}
