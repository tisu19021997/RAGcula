"use client";

import React, { useEffect, useState } from "react";
import { Layout, Flex, Divider } from "antd";

import axInstance from "@/app/api/config";
import UploadModal from "@/app/components/upload-modal";
import ChatSection from "@/app/components/chat-section";
import { IDocumentGet } from "@/app/interfaces/idocument.interface";
import DocList from "@/app/components/doc-list";

const { Content, Sider } = Layout;

const App = () => {
  const [uploadedFiles, setUploadedFiles] = useState<IDocumentGet[]>([]);
  const onDeleteFile = (docId: string) => {
    setUploadedFiles((prevstate) =>
      prevstate.filter((item) => item.id !== docId)
    );
  };

  useEffect(() => {
    let ignore: boolean = false;

    const getUploadedFiles = async () => {
      const { data } = await axInstance.get("/upload", {
        timeout: 20000,
      });

      if (!ignore) {
        // Update documents UI.
        data.map((item: IDocumentGet) => {
          setUploadedFiles((prevState) => [...prevState, item]);
        });
      }
    };
    getUploadedFiles();

    return () => {
      ignore = true;
    };
  }, []);

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Sider theme="light" width="300px">
        <Flex vertical>
          <UploadModal
            onUploadSucces={(data) =>
              setUploadedFiles((prevState) => [...prevState, data])
            }
          />
          <Divider />
          {uploadedFiles.map((doc, index) => (
            <DocList
              key={doc.id}
              docId={doc.id}
              onDelete={onDeleteFile}
              name={doc.display_name}
              docType="abc"
            />
          ))}
        </Flex>
      </Sider>
      <Layout>
        <Content style={{ margin: "16px 16px" }}>
          <ChatSection />
        </Content>
      </Layout>
    </Layout>
  );
};

export default App;
