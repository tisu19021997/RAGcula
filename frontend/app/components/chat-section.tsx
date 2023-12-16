"use client";

import { useChat } from "ai/react";
import { ChatInput, ChatMessages } from "./ui/chat";
import Dropdown from "./ui/dropdown";

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
    body: { user: "trucquynh123" }, // TODO: use username or user_id for each user.
  });

  return (
    <div className="space-y-4 max-w-5xl w-full">
      <Dropdown />
      <ChatMessages
        messages={messages}
        isLoading={isLoading}
        reload={reload}
        stop={stop}
      />
      <ChatInput
        input={input}
        handleSubmit={handleSubmit}
        handleInputChange={handleInputChange}
        isLoading={isLoading}
      />

    </div>
  );
}
