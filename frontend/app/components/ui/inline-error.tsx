'use client'

interface InlineErrorProps {
    message: string;
}

const InlineError = ({ message }: InlineErrorProps) => {
    return (
        <div className="text-red-700 text-sm py-2">
            <span className="block sm:inline">{message}</span>
        </div>
    )
}

export default InlineError;