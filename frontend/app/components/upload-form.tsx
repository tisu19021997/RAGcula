import React from 'react';
import { Form, Input, Upload } from 'antd';
import { InboxOutlined } from '@ant-design/icons';
import { DropzoneField } from './dropzone';

interface FormInputs {
    file: FileList;
}

interface UploadFormProps {
    onCreate: (values: FormInputs) => void;
    onCancel: () => void;
}

const normFile = (e: any) => {
    if (Array.isArray(e)) {
        return e;
    }
    return e?.fileList;
};

const UploadForm: React.FC<UploadFormProps> = ({
    onCreate,
    onCancel
}) => {
    const [form] = Form.useForm();

    return (
        <Form
            form={form}
            layout='vertical'
            name='upload_form'
        >
            <Form.Item name='dragger' valuePropName='file' getValueFromEvent={normFile}>
                <Upload.Dragger name='files'>
                    <p className="ant-upload-drag-icon">
                        <InboxOutlined />
                    </p>
                    <p className="ant-upload-text">Click or drag file to this area to upload</p>
                    <p className="ant-upload-hint">
                        Supported file types: pdf
                    </p>
                </Upload.Dragger>
            </Form.Item>

            <Form.Item
                label='When to use this document'
                name='description'
                rules={[{ required: true, message: 'This field is required.' }]}
            >
                <Input placeholder='E.g useful for career background, skills, education.' />
            </Form.Item>

            <Form.Item
                label='Questions could be answered from this document'
                name='question'
                rules={[{ required: true, message: 'This field is required.' }]}
            >
                <Input.TextArea placeholder='E.g Which university did you attend to?' rows={3} />
            </Form.Item>

        </Form>
    )
};

export default UploadForm;