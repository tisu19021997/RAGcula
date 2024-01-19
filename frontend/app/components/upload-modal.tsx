import React, { useState } from 'react';
import { Button, Flex, FloatButton, Modal, theme } from 'antd';
import { useForm, SubmitHandler } from 'react-hook-form';
import { UploadOutlined } from '@ant-design/icons';
import { DropzoneField } from '@/app/components/dropzone';


interface FormInputs {
    file: FileList;
}

const UploadModal: React.FC = () => {
    const { token: { paddingMD, marginMD } } = theme.useToken();
    const [open, setOpen] = useState(false);
    const form = useForm<FormInputs>();
    const onSubmit: SubmitHandler<FormInputs> = (data) => {
        console.log(data);
    };

    const showModal = () => {
        setOpen(true);
    };

    const handleCancel = () => {
        setOpen(false);
    };

    return (
        <div style={{ padding: `0 ${paddingMD}px` }}>
            <Modal
                open={open}
                title="New document"
                onCancel={handleCancel}
                footer={null}
                destroyOnClose={true}
            >
                <form onSubmit={form.handleSubmit(onSubmit)}>
                    <Flex vertical gap='large'>
                        <DropzoneField control={form.control} name='file' />
                        <Flex gap='small' justify='flex-end' style={{ width: '100%' }}>
                            <Button
                                htmlType='submit'
                                type='primary'
                                size='middle'
                            >
                                Upload
                            </Button>
                        </Flex>
                    </Flex>
                </form>
            </Modal>
            <Button
                onClick={showModal}
                shape='default'
                size='large'
                type='primary'
                icon={<UploadOutlined />}
                style={{ width: '100%', marginTop: marginMD }}
            >Upload new document</Button>
        </div>
    );
};

export default UploadModal;