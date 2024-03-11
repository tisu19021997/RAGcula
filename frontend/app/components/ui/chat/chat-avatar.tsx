import React from "react";
import { Avatar } from "antd";

interface ChatAvatarProps {
  role: string;
  name?: string | null;
}

const ChatAvatar: React.FC<ChatAvatarProps> = ({ role, name }) => {
  if (role === "user") {
    return <Avatar>{name?.charAt(0).toUpperCase()}</Avatar>;
  }

  return <Avatar src="/avatar.jpeg" />;
};

export default ChatAvatar;
