import React, { useState } from 'react';
import { PaperClipOutlined, DeleteOutlined, EyeOutlined, QuestionCircleOutlined } from '@ant-design/icons';
import { gray } from '@ant-design/colors';
import { Typography, Flex, Space, Button, Popconfirm, theme } from 'antd';
import { red } from "@ant-design/colors";

import axInstance from '@/app/api/config';

const { Text } = Typography;

interface DocListProps {
    name: string;
    docUrl?: string;
    docId?: string | null;
    docType?: string;
    onDelete: (docId: string) => void
}



const DocList: React.FC<DocListProps> = (props) => {
    const { name, docId, docUrl, onDelete } = props;
    const [isHovered, setIsHovered] = useState<boolean>(false);
    const { token: { paddingMD } } = theme.useToken();
    const deleteHandler = async (e?: React.MouseEvent<HTMLElement | MouseEvent>) => {
        const res = await axInstance.delete(
            '/upload',
            {
                params: {
                    document_id: docId,
                },
            },
        );
        if (docId && (res.status === 200)) {
            onDelete(docId);
        }
    };
    const confirmDelete = (e?: React.MouseEvent<HTMLElement | MouseEvent>) => {
        deleteHandler(e);
    };

    return (
        <Flex
            justify='space-between'
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
            style={{ height: 32, padding: `0 ${paddingMD}px` }}
        >
            <Space size='small'>
                <PaperClipOutlined />
                <Text ellipsis style={{ width: '180px' }}>{name}</Text>
            </Space>


            <Button
                type='text'
                icon={<EyeOutlined />}
                href={docUrl}
                target='_blank'
                rel='noopener noreferrer'
                style={{ color: gray[0] }}
                hidden={!isHovered}
            />

            <Popconfirm
                title='Delete file?'
                description={`This will delete ${name}`}
                onConfirm={confirmDelete}
                okText='Delete'
                cancelText='Cancel'
                icon={<QuestionCircleOutlined style={{ color: 'red' }} />}
            >
                <Button
                    danger
                    type='text'
                    icon={<DeleteOutlined style={{ color: red[4] }} />}
                    style={{ color: gray[0] }}
                    hidden={!isHovered}
                />
            </Popconfirm>


        </Flex>
    )
};

export default DocList;