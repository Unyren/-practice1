class OrganizerError(Exception):
    pass


class TagReadError(OrganizerError):
    pass


class FileOperationError(OrganizerError):
    pass


class DuplicateFileError(FileOperationError):
    pass
