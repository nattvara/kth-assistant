import { Grid, Loader, SimpleGrid } from "@mantine/core";
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
  const [displayedContent, setDisplayedContent] = useState("");
  const [showLoading, setShowLoading] = useState(false);
  const wsInitialized = useRef(false);

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
        setDisplayedContent((prevContent) => prevContent + event.data);
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
      setDisplayedContent(message.content || "");
      wsInitialized.current = false;
    }

    return () => {
      wsInitialized.current = false;
    };
  }, [message.message_id, message.streaming, message.websocket, message.content]);

  return (
    <SimpleGrid cols={1} className={styles.root}>
      <Grid>
        <strong>
          {message.sender === "student" && <>You</>}
          {message.sender === "assistant" && <>Copilot</>}
        </strong>
      </Grid>
      <Grid>
        <span className={styles.content}>
          {displayedContent}
          {showLoading && (
            <span>
              <Loader className={styles.loader} color="black" size={12} />
            </span>
          )}
        </span>
      </Grid>
    </SimpleGrid>
  );
}
