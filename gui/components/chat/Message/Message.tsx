import { Alert, Grid, Loader, SimpleGrid } from "@mantine/core";
import { IconExclamationCircle } from "@tabler/icons-react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import DOMPurify from "dompurify";
import { useTranslation } from "next-i18next";
import React, { useEffect, useRef, useState } from "react";

import { Feedback } from "@/components/chat";

import { MESSAGE_PENDING, MESSAGE_READY, Message as MessageType, fetchMessage } from "@/api/chat";
import { makeWebsocketUrl } from "@/api/http";
import { TERMINATION_STRING } from "@/api/websocket";

import styles from "./styles.module.css";

// 10 minutes
const REFETCH_TIMEOUT = 1000 * 60 * 10;

const markdownLinkPattern = /\[([^\]]+)\]\(([^)]+)\)/g;
const markdownBoldPattern = /\*\*([^*]+)\*\*/g;

interface MessageProps {
  initialMessage: MessageType;
  courseId: string;
  chatId: string;
  showFeedbackLabel: boolean;
  showAfterFeedbackLabel: boolean;
  readOnly: boolean;
}

export default function Message(props: MessageProps) {
  const { initialMessage, courseId, chatId, showFeedbackLabel, showAfterFeedbackLabel, readOnly } = props;
  const { t } = useTranslation("chat");
  const queryClient = useQueryClient();
  const [message, setMessage] = useState<MessageType>(initialMessage);
  const [shouldRefetch, setShouldRefetch] = useState(true);
  const [displayedContent, setDisplayedContent] = useState("");
  const [showLoading, setShowLoading] = useState(false);
  const [numberOfWords, setNumberOfWords] = useState(0);
  const wsInitialized = useRef(false);
  const loadingRef = useRef<HTMLDivElement>(null);

  const { data } = useQuery({
    queryKey: ["message", courseId, chatId, message.message_id],
    queryFn: () => fetchMessage(courseId, chatId, message.message_id),
    enabled: message.state === MESSAGE_PENDING && shouldRefetch,
    refetchInterval: 100,
  });

  useEffect(() => {
    if (data) {
      setMessage(data);
    }
  }, [data]);

  useEffect(() => {
    if (message.state !== MESSAGE_PENDING) return;

    const createdAtDate = new Date(initialMessage.created_at);
    const timeSinceCreated = new Date().getTime() - createdAtDate.getTime();

    if (timeSinceCreated >= REFETCH_TIMEOUT) {
      console.error("message was in pending state but timeout was reached, no longer re-fetching.");
      setShouldRefetch(false);
    } else {
      const timeoutDuration = REFETCH_TIMEOUT - timeSinceCreated;
      const timer = setTimeout(() => {
        console.error("message was in pending state but timeout was reached, no longer re-fetching.");
        setShouldRefetch(false);
      }, timeoutDuration);

      return () => clearTimeout(timer);
    }
  }, [initialMessage.created_at, message.state]);

  useEffect(() => {
    if (message.streaming && message.websocket && !wsInitialized.current) {
      wsInitialized.current = true;
      setShowLoading(true);
      const ws = new WebSocket(makeWebsocketUrl(message.websocket));
      ws.onmessage = (event) => {
        if (event.data === TERMINATION_STRING) {
          setShowLoading(false);
          ws.close();
          return;
        }
        setDisplayedContent((prevContent) => {
          let newContent = prevContent + event.data;
          newContent = newContent.replace(/\n/g, "<br>");
          newContent = newContent.replace(
            markdownLinkPattern,
            (match, p1, p2) => `<a href="${p2}" target="_blank">${p1}</a>`,
          );
          newContent = newContent.replace(markdownBoldPattern, (match, p1) => `<strong>${p1}</strong>`);

          setNumberOfWords(newContent.split(" ").length);
          return newContent;
        });
      };
      ws.onclose = () => {
        console.log("WebSocket closed");
        setShowLoading(false);
        wsInitialized.current = false;

        queryClient.invalidateQueries({
          queryKey: ["messages", courseId, chatId],
        });
      };
      ws.onerror = (error) => {
        console.log("WebSocket error:", error);
        setShowLoading(false);
        wsInitialized.current = false;

        queryClient.invalidateQueries({
          queryKey: ["messages", courseId, chatId],
        });
      };

      return () => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.close();
        }
      };
    } else if (!message.streaming) {
      let initialContent = message.content || "";
      initialContent = initialContent.replace(/\n/g, "<br>");
      initialContent = initialContent.replace(
        markdownLinkPattern,
        (match, p1, p2) => `<a href="${p2}" target="_blank">${p1}</a>`,
      );
      initialContent = initialContent.replace(markdownBoldPattern, (match, p1) => `<strong>${p1}</strong>`);
      setDisplayedContent(initialContent);
      setNumberOfWords(0);
      setShowLoading(false);
      wsInitialized.current = false;
    }

    return () => {
      wsInitialized.current = false;
    };
  }, [message.message_id, message.streaming, message.websocket, message.content, chatId, courseId, queryClient]);

  useEffect(() => {
    setMessage(initialMessage);
  }, [initialMessage]);

  useEffect(() => {
    if (numberOfWords % 5 === 0 && numberOfWords > 0) {
      loadingRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [numberOfWords]);

  const sanitisedHtml = DOMPurify.sanitize(displayedContent);

  return (
    <>
      {message.feedback_id === null && (
        <SimpleGrid cols={1} className={styles.normal_message}>
          <Grid>
            <strong>
              {message.sender === "student" && <>{t("message.student")}</>}
              {message.sender === "assistant" && <>{t("message.assistant")}</>}
            </strong>
          </Grid>
          <Grid>
            {message.state === MESSAGE_PENDING && shouldRefetch && (
              <SimpleGrid cols={1} className={styles.pending}>
                <span>
                  <Loader className={styles.loader} color="black" type="dots" />
                  <span className={styles.pending_text}>{t("message.pending")}</span>
                </span>
              </SimpleGrid>
            )}
            {message.state === MESSAGE_PENDING && !shouldRefetch && (
              <Alert
                className={styles.error}
                variant="light"
                color="red"
                title={t("message.failed.title")}
                icon={<IconExclamationCircle />}
              >
                {t("message.failed.text")}
              </Alert>
            )}
            {message.state === MESSAGE_READY && (
              <>
                <span className={styles.content} dangerouslySetInnerHTML={{ __html: sanitisedHtml }}></span>
                {showLoading && (
                  <span>
                    <Loader className={styles.loader} ref={loadingRef} color="black" size={12} />
                  </span>
                )}
              </>
            )}
          </Grid>
        </SimpleGrid>
      )}
      {message.feedback_id !== null && (
        <SimpleGrid cols={1} className={styles.feedback_message}>
          <Grid>
            <Feedback
              message={message}
              withLabel={showFeedbackLabel}
              withPostLabel={showAfterFeedbackLabel}
              courseId={courseId}
              chatId={chatId}
              readOnly={readOnly}
            />
          </Grid>
        </SimpleGrid>
      )}
    </>
  );
}
