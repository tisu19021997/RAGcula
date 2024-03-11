"use client";

import { useChat } from "ai/react";
import { Card, Flex, Select } from "antd";
import { ChatInput, ChatMessages } from "./ui/chat";

export default function ChatSection() {
  const {
    messages,
    input,
    isLoading,
    handleSubmit,
    handleInputChange,
    reload,
    stop,
  } = useChat({
    api: `${process.env.NEXT_PUBLIC_API}/chat`,
    onError: (err: Error) => {
      console.log(err);
    },
  });

  return (
    <Flex vertical justify="space-between" gap={16} style={{ height: "100%" }}>
      <Card title="Chat">
        <ChatMessages
          messages={messages}
          isLoading={isLoading}
          reload={reload}
          stop={stop}
        />
      </Card>

      <ChatInput
        input={input}
        handleSubmit={handleSubmit}
        handleInputChange={handleInputChange}
        isLoading={isLoading}
      />
    </Flex>
  );
}
