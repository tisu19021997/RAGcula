'use client'

import { pdfjs } from 'react-pdf';

pdfjs.GlobalWorkerOptions.workerSrc = new URL(
    'pdfjs-dist/build/pdf.worker.min.js',
    import.meta.url,
).toString();

import React, { useEffect, useState } from 'react';
import { Layout, Flex, theme, Divider } from 'antd';

import axInstance from "@/app/api/config";
import UploadModal from '@/app/components/upload-modal';
import ChatSection from '@/app/components/chat-section';
import { IDocumentGet } from "@/app/interfaces/idocument.interface";
import { useAuth } from '@/app/auth/provider';
import DocList from '@/app/components/doc-list';
import ProtectedRoute from '@/app/components/protected-route';

const { Content, Sider } = Layout;

const App = () => {
    const {
        token: { paddingMD },
    } = theme.useToken();
    const { user } = useAuth();
    const [uploadedFiles, setUploadedFiles] = useState<IDocumentGet[]>([]);
    const onDeleteFile = (docId: string) => {
        setUploadedFiles((prevstate) => prevstate.filter((item) => item.id !== docId));
    };

    useEffect(() => {
        const getUploaded = async () => {
            if (user.uid) {
                const { data } = await axInstance.get(
                    'chat/upload',
                    {
                        params: {
                            user_id: user.uid
                        },
                        timeout: 20000,
                    },
                );
                // Retrieve the uploaded files.
                data.map((item: IDocumentGet) => {
                    setUploadedFiles((prevState) => [...prevState, item])
                });

            }
        }
        getUploaded();
        return () => { }
    }, [user]);

    return (

        <Layout style={{ minHeight: '100vh' }}>
            <Sider theme='light' width='300px'>
                <Flex vertical>
                    <UploadModal onUploadSucces={(data) => setUploadedFiles((prevState) => [...prevState, data])} />
                    <Divider />
                    {uploadedFiles.map((doc, index) =>
                        <DocList
                            docUrl={doc.s3_url}
                            key={doc.id}
                            docId={doc.id}
                            onDelete={onDeleteFile}
                            name={doc.s3_path.split('/')[1]}
                            docType='abc' />
                    )}
                </Flex>
            </Sider>
            <Layout>
                <Content style={{ margin: '16px 16px' }}>
                    <ChatSection />
                </Content>
            </Layout>
        </Layout>

    )
}

export default App;