import React, { useEffect, useState, useRef } from 'react';
import { Grid, Loader, SimpleGrid } from '@mantine/core';
import styles from './styles.module.css';
import { makeWebsocketUrl } from '@/api/http';
import { Message } from '@/api/chat';
import { TERMINATION_STRING } from '@/api/websocket';

interface MessageProps {
  message: Message;
}

export default function Message(props: MessageProps) {
  const { message } = props;
  const [ displayedContent, setDisplayedContent ] = useState('');
  const [ showLoading, setShowLoading ] = useState(false);
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
        console.log('WebSocket closed');
        setShowLoading(false);
        wsInitialized.current = false;
      };
      ws.onerror = (error) => {
        console.log('WebSocket error:', error);
        setShowLoading(false);
        wsInitialized.current = false;
      };

      return () => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.close();
        }
      };
    } else if (!message.streaming) {
      setDisplayedContent(message.content || '');
      wsInitialized.current = false;
    }

    return () => {
      wsInitialized.current = false;
    };
  }, [message.message_id, message.streaming, message.websocket, message.content]);

  return (
    <SimpleGrid cols={1} className={styles.root}>
      <Grid>
        <strong>{message.sender}</strong>
      </Grid>
      <Grid>
        <span>
          {displayedContent}
          {showLoading && <span> <Loader color="black" size={12}/></span>}
        </span>
      </Grid>
    </SimpleGrid>
  );
}
