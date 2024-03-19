import React, { useState } from "react";
import { Button, Flex, Modal, Form, Upload, Input, theme, message } from "antd";
import { UploadFile } from "antd";
import { UploadOutlined, InboxOutlined } from "@ant-design/icons";

import { IDocumentGet } from "@/app/interfaces/idocument.interface";
import axInstance from "@/app/api/config";

interface FormInputs {
  file: [UploadFile];
}

interface UploadModelProps {
  onUploadSucces: (data: IDocumentGet) => void;
}

const normFile = (e: any) => {
  if (Array.isArray(e)) {
    return e;
  }
  return e?.fileList;
};

const UploadModal: React.FC<UploadModelProps> = ({ onUploadSucces }) => {
  // Antd stuffs.
  const [messageApi, contextHolder] = message.useMessage();
  const {
    token: { paddingMD, marginMD },
  } = theme.useToken();
  // Open/close state.
  const [open, setOpen] = useState<boolean>(false);
  // Loading state when uploading.
  const [isUploading, setIsUploading] = useState<boolean>(false);
  // Upload form.
  const [form] = Form.useForm();

  const onSubmit = () => {
    form
      .validateFields()
      .then(async (values: FormInputs) => {
        setIsUploading(true);

        // Create a FormData for multipart request.
        const formData: FormData = new FormData();
        const { file } = values;
        if (file[0].originFileObj) {
          formData.append("file", file[0].originFileObj);
          // formData.append("description", description);
          // formData.append("question", question);

          const { data } = await axInstance.post("/upload/single", formData, {
            timeout: 50000,
            headers: {
              Accept: "application/json",
              "Content-Type": "multipart/form-data",
            },
          });
          messageApi.open({
            type: "success",
            content: "Uploaded. Go chat and leave me alone.",
            duration: 3,
          });
          onUploadSucces(data);
        }
        form.resetFields();
      })
      .catch((info) => {
        messageApi.open({
          type: "error",
          content: "Sorry, our sever fucked up.",
          duration: 5,
        });
        console.log(info);
      })
      .finally(() => setIsUploading(false));
  };

  const showModal = () => {
    setOpen(true);
  };

  const onCancel = () => {
    setOpen(false);
    form.resetFields();
  };

  return (
    <div style={{ padding: `0 ${paddingMD}px` }}>
      {contextHolder}
      <Modal
        open={open}
        title="New document"
        onCancel={onCancel}
        footer={[
          <Button
            key="submit"
            htmlType="submit"
            type="primary"
            size="middle"
            onClick={onSubmit}
            loading={isUploading}
          >
            Upload
          </Button>,
        ]}
        destroyOnClose={true}
      >
        {/* <form onSubmit={form.handleSubmit(onSubmit)}> */}
        <Flex vertical gap="large">
          <Form form={form} layout="vertical" name="upload_form">
            <Form.Item
              name="file"
              valuePropName="file"
              getValueFromEvent={normFile}
              rules={[{ required: true, message: "This field is required." }]}
            >
              <Upload.Dragger
                name="files"
                beforeUpload={() => false}
                accept={"application/pdf"}
                maxCount={1}
              >
                <p className="ant-upload-drag-icon">
                  <InboxOutlined />
                </p>
                <p className="ant-upload-text">
                  Click or drag file to this area to upload
                </p>
                <p className="ant-upload-hint">Supported file types: pdf</p>
              </Upload.Dragger>
            </Form.Item>

            {/* <Form.Item
              label="When to use this document"
              name="description"
              rules={[{ required: true, message: "This field is required." }]}
            >
              <Input placeholder="E.g useful for career background, skills, education." />
            </Form.Item>

            <Form.Item
              label="Questions could be answered from this document"
              name="question"
              rules={[{ required: true, message: "This field is required." }]}
            >
              <Input.TextArea
                placeholder="E.g Which university did you attend to?"
                rows={3}
              />
            </Form.Item> */}
          </Form>
        </Flex>
        {/* </form> */}
      </Modal>
      <Button
        onClick={showModal}
        shape="default"
        size="large"
        type="primary"
        icon={<UploadOutlined />}
        style={{ width: "100%", marginTop: marginMD }}
      >
        Upload new document
      </Button>
    </div>
  );
};

export default UploadModal;
