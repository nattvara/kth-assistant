import { Grid, Loader, SimpleGrid } from "@mantine/core";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "next-i18next";
import React, { useEffect, useRef, useState } from "react";

import { MESSAGE_PENDING, MESSAGE_READY, Message as MessageType, fetchMessage } from "@/api/chat";
import { makeWebsocketUrl } from "@/api/http";
import { TERMINATION_STRING } from "@/api/websocket";

import styles from "./styles.module.css";

interface MessageProps {
  initialMessage: MessageType;
  courseId: string;
  chatId: string;
}

export default function Message(props: MessageProps) {
  const { initialMessage, courseId, chatId } = props;
  const { t } = useTranslation("chat");
  const [message, setMessage] = useState<MessageType>(initialMessage);
  const [displayedContent, setDisplayedContent] = useState("");
  const [showLoading, setShowLoading] = useState(false);
  const [numberOfWords, setNumberOfWords] = useState(0);
  const wsInitialized = useRef(false);
  const loadingRef = useRef<HTMLDivElement>(null);

  const { data } = useQuery({
    queryKey: ["message", courseId, chatId, message.message_id],
    queryFn: () => fetchMessage(courseId, chatId, message.message_id),
    enabled: message.state === MESSAGE_PENDING,
    refetchInterval: 100,
  });

  useEffect(() => {
    if (data) {
      setMessage(data);
    }
  }, [data]);

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
          const docPattern = /\\document\{([^}]+)\}\{([^}]+)\}/g;
          newContent = newContent.replace(docPattern, (match, p1, p2) => {
            return `<a href="${p1}" target="_blank">${p2}</a>`;
          });

          setNumberOfWords(newContent.split(" ").length);
          return newContent;
        });
      };
      ws.onclose = () => {
        console.log("WebSocket closed");
        setShowLoading(false);
        wsInitialized.current = false;
      };
      ws.onerror = (error) => {
        console.log("WebSocket error:", error);
        setShowLoading(false);
        wsInitialized.current = false;
      };

      return () => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.close();
        }
      };
    } else if (!message.streaming) {
      let initialContent = message.content || "";
      const docPattern = /\\document\{([^}]+)\}\{([^}]+)\}/g;
      initialContent = initialContent.replace(docPattern, (match, p1, p2) => {
        return ` <a href="${p1}" target="_blank">${p2}</a> `;
      });
      setDisplayedContent(initialContent);
      setNumberOfWords(0);
      wsInitialized.current = false;
    }

    return () => {
      wsInitialized.current = false;
    };
  }, [message.message_id, message.streaming, message.websocket, message.content]);

  useEffect(() => {
    if (numberOfWords % 5 === 0 && numberOfWords > 0) {
      loadingRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [numberOfWords]);

  return (
    <SimpleGrid cols={1} className={styles.root}>
      <Grid>
        <strong>
          {message.sender === "student" && <>{t("message.student")}</>}
          {message.sender === "assistant" && <>{t("message.assistant")}</>}
        </strong>
      </Grid>
      <Grid>
        {message.state === MESSAGE_PENDING && (
          <SimpleGrid cols={1} className={styles.pending}>
            <span>
              <Loader className={styles.loader} color="black" type="dots" />
              <span className={styles.pending_text}>{t("message.pending")}</span>
            </span>
          </SimpleGrid>
        )}
        {message.state === MESSAGE_READY && (
          <>
            <span className={styles.content} dangerouslySetInnerHTML={{ __html: displayedContent }}></span>
            {showLoading && (
              <span>
                <Loader className={styles.loader} ref={loadingRef} color="black" size={12} />
              </span>
            )}
          </>
        )}
      </Grid>
    </SimpleGrid>
  );
}
