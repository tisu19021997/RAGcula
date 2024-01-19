import { Input } from "../input";
import { ChatHandler } from "./chat.interface";
import { Button } from "antd";
import { ArrowUpOutlined } from "@ant-design/icons";

export default function ChatInput(
  props: Pick<
    ChatHandler,
    "isLoading" | "handleSubmit" | "handleInputChange" | "input"
  >,
) {
  return (
    <form
      onSubmit={props.handleSubmit}
      className="flex w-full items-start justify-between gap-4 rounded-xl bg-white p-4 shadow-xl"
    >
      <Input
        autoFocus
        name="message"
        placeholder="Ask questions related to professional background, skills, education... "
        className="flex-1"
        value={props.input}
        onChange={props.handleInputChange}
      />
      <Button
        type='default'
        htmlType='submit'
        loading={props.isLoading}
        icon={<ArrowUpOutlined />}
        size='large'
      />
    </form>
  );
}
