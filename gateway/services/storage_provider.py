from abc import ABC, abstractmethod


class StorageProvider(ABC):

    @abstractmethod
    def upload_file(self, file, filename, content_type):
        pass

    @abstractmethod
    def list_files(self):
        pass

    @abstractmethod
    def download_file(self, filename):
        pass

    @abstractmethod
    def get_storage_usage(self):
        pass

    @abstractmethod
    def migrate_object_to(self, filename, target_provider):
        pass