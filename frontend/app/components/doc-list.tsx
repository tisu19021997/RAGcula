import React, { useState } from 'react';
import { PaperClipOutlined, DeleteOutlined } from '@ant-design/icons';
import { gray } from '@ant-design/colors';
import { Typography, Flex, Space, Button, Popconfirm, message, theme } from 'antd';
import axInstance from '@/app/api/config';
import { useAuth } from '@/app/auth/provider';

const { Text } = Typography;

interface DocListProps {
    name: string;
    docId?: string | null;
    docType?: string;
    onDelete: (docId: string) => void
}



const DocList: React.FC<DocListProps> = (props) => {
    const { name, docId, onDelete } = props;
    const [isHovered, setIsHovered] = useState<boolean>(false);
    const { token: { paddingMD } } = theme.useToken();
    const { user } = useAuth();
    const deleteHandler = async (e?: React.MouseEvent<HTMLElement | MouseEvent>) => {
        const res = await axInstance.delete(
            'chat/upload',
            {
                params: {
                    user_id: user.uid,
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
                <Text ellipsis style={{ width: '200px' }}>{name}</Text>
            </Space>
            <Popconfirm
                title='Delete file?'
                description={`This will delete ${name}`}
                onConfirm={confirmDelete}
                okText='Delete'
                cancelText='Cancel'
            >
                <Button
                    danger
                    icon={<DeleteOutlined />}
                    style={{ color: gray[0] }}
                    hidden={!isHovered}
                // onClick={deleteHandler}
                />
            </Popconfirm>

        </Flex>
    )
};

export default DocList;