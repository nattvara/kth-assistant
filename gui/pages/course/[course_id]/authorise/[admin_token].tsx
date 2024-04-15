import { Button, Grid, Paper, SimpleGrid, Space, Title } from "@mantine/core";
import { useMutation } from "@tanstack/react-query";
import { GetServerSidePropsContext } from "next";
import { serverSideTranslations } from "next-i18next/serverSideTranslations";
import { useRouter } from "next/router";
import { useState } from "react";

import { HttpError } from "@/api/http";
import { grantAdminAccess } from "@/api/session";

const AuthorisePage = () => {
  const router = useRouter();
  const { course_id, admin_token } = router.query;
  const [failed, setFailed] = useState<null | boolean>(null);

  const accessMutation = useMutation({
    mutationFn: (adminToken: string) => grantAdminAccess(adminToken),
    onSuccess: () => {
      router.push(`/course/${course_id}/chats`);
    },
    onError: (error: HttpError) => {
      console.error(error);
      setFailed(true);
    },
  });

  if (!course_id) return <></>;

  if (!admin_token) return <></>;

  if (failed === true) return <>Failed to grant admin access</>;

  return (
    <SimpleGrid cols={1}>
      <Space h="xl" />
      <Space h="xl" />
      <Grid justify="center">
        <Paper p="lg" shadow="lg" withBorder>
          <SimpleGrid cols={1}>
            <Title order={3}>To get admin access to the course</Title>
            <Button color="teal" size="lg" onClick={() => accessMutation.mutate(admin_token as string)}>
              Click here
            </Button>
          </SimpleGrid>
        </Paper>
      </Grid>
    </SimpleGrid>
  );
};

export async function getServerSideProps(context: GetServerSidePropsContext) {
  const { locale } = context;
  const translations = await serverSideTranslations(locale as string, ["common", "input", "chat"]);

  return {
    props: {
      ...translations,
    },
  };
}

export default AuthorisePage;
