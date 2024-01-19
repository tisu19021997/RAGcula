import { Controller, Control } from 'react-hook-form';
import { FC } from "react";
import { InboxOutlined } from '@ant-design/icons';
import type { UploadProps } from 'antd';
import { message, Upload } from 'antd';

const { Dragger } = Upload;
const props: UploadProps = {
    name: 'file',
    multiple: false,
    showUploadList: {
        showDownloadIcon: true,
        downloadIcon: 'Download',
    },
    maxCount: 1,
};

export const DropzoneField: FC<{ control: Control<any>; name: string; }> = (
    { control, name }) => {
    return (
        <Controller
            control={control}
            name={name}
            rules={{
                required: { value: true, message: 'This field is required' },
            }}
            render={({ field: { onChange, onBlur }, fieldState }) => (
                <Dragger
                    {...props}
                    multiple={false}
                    beforeUpload={() => false}
                    accept={'application/pdf'}
                    onChange={(info) => {
                        const { status } = info.file;
                        if (status !== 'uploading') {
                            console.log(info.file, info.fileList);
                        }
                        onChange(info.fileList);
                    }}
                    onDrop={(event) => {
                        onChange(event.dataTransfer.files);
                    }}
                >
                    <p className="ant-upload-drag-icon">
                        <InboxOutlined />
                    </p>
                    <p className="ant-upload-text">Click or drag file to this area to upload</p>
                    <p className="ant-upload-hint">
                        Supported file types: pdf
                    </p>
                </Dragger>
            )}
        />
    );
};