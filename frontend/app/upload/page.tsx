'use client'

import React, { useState } from 'react';
import { Button, FormControl, VStack, Card, CardBody, CardHeader, CardFooter, HStack, Tag, TagLabel, CloseButton, Input, Heading, Flex, ButtonGroup, Textarea, FormLabel, FormHelperText, Box } from '@chakra-ui/react'
import { useFieldArray, useForm } from 'react-hook-form';
import { IUser } from "@/app/interfaces/iuser.interface";
import { useAuth } from "@/app//auth/provider";;
import axInstance from "@/app/api/config";
import { PlusIcon, SendHorizonalIcon } from 'lucide-react';

interface FormValues {
    files: {
        file_: FileList | null;
        description_: string;
        question_: string;
    }[]
}

const App = () => {
    // Maximum number of documents.
    const N_MAX_DOCUMENT = 3;
    // Form handling.
    const {
        register,
        handleSubmit,
        formState: { errors },
        control,
        getValues,
        setValue,
    } = useForm<FormValues>({
        defaultValues: {
            files: [{ file_: null, description_: '', question_: '' }]
        }
    });
    const { fields, append, remove } = useFieldArray({
        name: 'files',
        control,
    })
    const [isSubmitting, setIsSubmitting] = useState<boolean>(false)

    // Sending files and form fields to server.
    const uploadFiles = handleSubmit(async (data) => {
        try {
            const formData = new FormData();
            data.files.forEach(({ file_, description_, question_ }, index) => {
                if (file_) {
                    formData.append('files', file_[0])
                    formData.append('descriptions', description_)
                    formData.append('questions', question_)

                    // formData.append(`files`, file_[0]);
                    // formData.append('descriptions', description_);
                    // formData.append('questions', question_);
                }
            });

            // Set loading progress.
            setIsSubmitting(true);
            const response = await axInstance.post(
                '/chat/upload',
                formData,
                {
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'multipart/form-data',
                    }
                }
            );
            // console.log(response.data);
        } catch (error) {
            // TODO: handle this error too bitch.
            console.error(error);
        } finally {
            setIsSubmitting(false);
        }
    });

    return (
        <main className="background-gradient">
            <Flex direction='column' alignItems='center' p='8'>
                <form onSubmit={uploadFiles}>
                    <VStack mt='8' gap='8'>
                        <Flex gap='4'>
                            {fields.map((field, index) => {
                                return (
                                    <Card key={field.id}>
                                        <CardHeader>
                                            <Flex minWidth='max-content' alignItems='center' justifyContent='space-between'>
                                                <Heading size='lg'>Document #{index}</Heading>
                                                <CloseButton
                                                    onClick={() => {
                                                        // There should always be at least 1 file.
                                                        if (fields.length == 1) return;
                                                        remove(index);
                                                    }}
                                                    disabled={fields.length == 1}
                                                />
                                            </Flex>
                                        </CardHeader>
                                        <CardBody>
                                            <VStack gap='4'>
                                                <FormControl isRequired>
                                                    <Input
                                                        {...register(
                                                            `files.${index}.file_`,
                                                            { required: true, }
                                                        )}
                                                        variant='filled'
                                                        type='file'
                                                        accept='.pdf'
                                                        padding={1}
                                                    />
                                                </FormControl>
                                                <FormControl isRequired>
                                                    <FormLabel>Specify when AI could use this document</FormLabel>
                                                    <Textarea
                                                        {...register(
                                                            `files.${index}.description_`,
                                                            { required: true, }
                                                        )}
                                                        size='md'
                                                        placeholder='Example: useful for personal background, skills, education, and accomplishments.'
                                                    />
                                                </FormControl>

                                                <FormControl isRequired>
                                                    <FormLabel>Give questions that could be answered from this document</FormLabel>
                                                    <Textarea
                                                        {...register(
                                                            `files.${index}.question_`,
                                                            { required: true, }
                                                        )}
                                                        size='md'
                                                        placeholder="Give some questions that can be answered by this doc."
                                                    />
                                                    <FormHelperText>Use 'Enter' to separate questions. </FormHelperText>
                                                </FormControl>
                                            </VStack>
                                        </CardBody>
                                    </Card>
                                )
                            })}
                        </Flex>

                        <ButtonGroup gap='2'>
                            <Button
                                leftIcon={<PlusIcon />}
                                type="button"
                                // className="flex justify-center rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-semibold leading-6 text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
                                onClick={() => {
                                    // Reach maximum number of documents.
                                    if (fields.length === N_MAX_DOCUMENT) return;
                                    append({
                                        file_: null,
                                        description_: '',
                                        question_: ''
                                    })
                                }}
                                colorScheme='teal'
                                variant='outline'
                                isDisabled={fields.length == N_MAX_DOCUMENT}
                            >
                                Add another
                            </Button>
                            <Button
                                leftIcon={<SendHorizonalIcon />}
                                type='submit'
                                colorScheme='teal'
                                isLoading={isSubmitting}

                            >
                                Upload
                            </Button>
                        </ButtonGroup>
                    </VStack>
                </form>
            </Flex>
        </main >
    )
}


export default App;