import { Message } from "@/components/chat";

interface MessageFeedProps {
  className: string;
}

export default function MessageFeed(props: MessageFeedProps) {
  const { className } = props;

  return (
    <div className={className}>
      <Message sender={"Detective Somerset"} message={"This case has layers that we're only just beginning to peel back."}></Message>
      <Message sender={"Detective Mills"} message={"Every clue feels like it's leading to a bigger puzzle. It's like nothing adds up."}></Message>
      <Message sender={"Detective Somerset"} message={"That's because we're looking at the pieces individually. We need to see the bigger picture."}></Message>
      <Message sender={"Detective Mills"} message={"But that's just it, isn't it? Every time we think we see the whole picture, it changes."}></Message>
      <Message sender={"Tracy"} message={"Is it always like this? This... consuming?"}></Message>
      <Message sender={"Detective Somerset"} message={"It can be. It's not just about solving a case. It's about understanding the why."}></Message>
      <Message sender={"Detective Mills"} message={"And sometimes, the 'why' is the hardest part to grasp."}></Message>
      <Message sender={"Tracy"} message={"But you still try, despite that?"}></Message>
      <Message sender={"Detective Somerset"} message={"Especially because of that. Understanding the 'why' might not change what happened, but it can sometimes prevent it from happening again."}></Message>
      <Message sender={"Detective Mills"} message={"He's right. It's the small victories, the lives we save moving forward, that count."}></Message>
      <Message sender={"Tracy"} message={"It sounds like a heavy burden to carry."}></Message>
      <Message sender={"Detective Somerset"} message={"It is. But it's also a privilege. To stand for those who can't stand for themselves."}></Message>
      <Message sender={"Detective Mills"} message={"And we carry it together. That makes it a bit lighter."}></Message>
      <Message sender={"Tracy"} message={"Thank you for what you do. For keeping the fight, even when it gets tough."}></Message>
      <Message sender={"Detective Somerset"} message={"Thank you, Tracy. Support makes all the difference."}></Message>
      <Message sender={"Detective Mills"} message={"Yeah, thank you. It's good to be reminded why we do this."}></Message>
    </div>
  );
}
