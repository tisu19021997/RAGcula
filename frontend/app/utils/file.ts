export const validateFile = (file: File) => {
    const fileSizeMb = file.size / (1024 * 1024);
    const MAX_FILE_SIZE_MB = 5;
    if (fileSizeMb > MAX_FILE_SIZE_MB) {
        return false;
    }
    return true;
};