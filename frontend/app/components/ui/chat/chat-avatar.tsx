import React from 'react';
import { User2 } from "lucide-react";
import Image from "next/image";
import { Avatar } from 'antd';

interface ChatAvatarProps {
  role: string;
  name?: string | null;
};

const ChatAvatar: React.FC<ChatAvatarProps> = ({ role, name }) => {
  if (role === "user") {
    return (
      <Avatar>{name?.charAt(0).toUpperCase()}</Avatar>
    );
  }

  return (
    <Avatar src="/avatar.jpeg" />
    // <div className="flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-md border bg-black text-white shadow">
    //   <Image
    //     className="rounded-md"
    //     src="/avatar.jpeg"
    //     alt="A green pepe"
    //     width={24}
    //     height={24}
    //     priority
    //   />
    // </div>
  );
}


export default ChatAvatar;