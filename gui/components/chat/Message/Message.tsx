import { Grid, Loader, SimpleGrid } from "@mantine/core";
import { useTranslation } from "next-i18next";
import React, { useEffect, useRef, useState } from "react";

import { Message as MessageType } from "@/api/chat";
import { makeWebsocketUrl } from "@/api/http";
import { TERMINATION_STRING } from "@/api/websocket";

import styles from "./styles.module.css";

interface MessageProps {
  message: MessageType;
}

export default function Message(props: MessageProps) {
  const { message } = props;
  const { t } = useTranslation("chat");
  const [displayedContent, setDisplayedContent] = useState("");
  const [showLoading, setShowLoading] = useState(false);
  const [numberOfWords, setNumberOfWords] = useState(0);
  const wsInitialized = useRef(false);
  const loadingRef = useRef<HTMLDivElement>(null);

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
        <span className={styles.content} dangerouslySetInnerHTML={{ __html: displayedContent }}></span>
        {showLoading && (
          <span>
            <Loader className={styles.loader} ref={loadingRef} color="black" size={12} />
          </span>
        )}
      </Grid>
    </SimpleGrid>
  );
}
