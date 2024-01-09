"use client";

import { useRef, useState, ReactNode, Fragment } from "react";
import { UseFormRegisterReturn } from 'react-hook-form'
import { InputGroup, Card, CardBody, CardHeader, CardFooter, HStack, Tag, TagLabel, TagCloseButton, VStack, CloseButton, Input } from '@chakra-ui/react'

interface FileUploaderProps {
    fileRegister: UseFormRegisterReturn;
    accept?: string;
    multiple?: boolean;
    children?: ReactNode;
    descRegister: UseFormRegisterReturn;
    questionRegister: UseFormRegisterReturn;
}

const FileUploader = (props: FileUploaderProps) => {
    const { fileRegister, accept, multiple, children, descRegister, questionRegister } = props;
    const inputRef = useRef<HTMLInputElement | null>(null);
    const { ref, onChange, ...rest } = fileRegister;
    const [fileNames, setFileNames] = useState<string[]>([]);

    const handleClick = () => inputRef.current?.click();

    return (
        <VStack>
            <InputGroup onClick={handleClick}>
                <input
                    type={'file'}
                    multiple={multiple || false}
                    hidden
                    accept={accept}
                    {...rest}
                    ref={(e) => {
                        ref(e);
                        inputRef.current = e;
                    }}
                    onChange={(e) => { onChange(e); }}
                />
                {children}
            </InputGroup>

            <HStack spacing={4} align='start'>
                {fileNames.map((fileName, idx) => (
                    <Card key={idx} width={"100%"}>
                        <CardHeader>
                            <HStack>
                                <Tag
                                    size='lg'
                                    borderRadius='full'
                                    // variant='solid'
                                    colorScheme='purple'
                                >
                                    <TagLabel>{fileName}</TagLabel>
                                    {/* <TagCloseButton /> */}
                                </Tag>
                                <CloseButton />
                            </HStack>
                        </CardHeader>

                        <CardBody>
                            <InputGroup flexDirection={"column"}>
                                <Input
                                    {...descRegister}
                                    placeholder="Describe when to use this file."
                                />
                                <Input
                                    {...questionRegister}
                                    placeholder="Give some questions that can be answered using this file."
                                />
                            </InputGroup>
                        </CardBody>

                        <CardFooter>
                            b
                        </CardFooter>
                    </Card>
                ))}
            </HStack>

        </VStack>
    )
}

export default FileUploader;