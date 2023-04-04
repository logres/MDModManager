import os
from PIL import Image
import io
import shutil


class ResourceManager:
    """
    Directly Manage with FileSystem
    """

    def __init__(self, local_path, target_path):
        self.resource_path = os.path.join(local_path, "resource")
        self.backup_path = os.path.join(local_path, "backup")
        self.mod_path = os.path.join(local_path, "mod")
        self.init_folder()
        self.game_resource_path = target_path

    def init_folder(self):
        os.makedirs(self.resource_path, exist_ok=True)
        os.makedirs(self.backup_path, exist_ok=True)
        os.makedirs(self.mod_path, exist_ok=True)

    def get_mod_preview(self, resource_id: str, size: tuple[int, int] = (250, 250)):
        preview_path = os.path.join(
            self.mod_path, resource_id, "preview.png")
        if not os.path.exists(preview_path):
            return None
        image = Image.open(preview_path)
        image.thumbnail(size)
        with io.BytesIO() as output:
            image.save(output, format='PNG')
            png_bytes = output.getvalue()
        return png_bytes

    def add_mod_preview(self, mod_id: str, preview_path: str):
        mod_preview_path = os.path.join(
            self.mod_path, mod_id, "preview.png")
        os.makedirs(os.path.dirname(mod_preview_path), exist_ok=True)
        shutil.copyfile(preview_path, mod_preview_path)

    def apply_resource(self, resource_id: str, resource_hash: str):
        mod_resource_path = os.path.join(
            self.resource_path, resource_id, resource_hash)
        game_resource_path = os.path.join(
            self.game_resource_path, resource_hash[:2], resource_hash)
        backup_resource_path = os.path.join(
            self.backup_path, resource_hash[:2], resource_hash)
        # Save game resource to backup if not Exist
        if not os.path.exists(backup_resource_path):
            os.makedirs(os.path.dirname(backup_resource_path), exist_ok=True)
            shutil.copyfile(game_resource_path, backup_resource_path)
        # replace game resource with mod resource
        shutil.copyfile(mod_resource_path, game_resource_path)

    def reset_resource(self, resource_hash: str):
        game_resource_path = os.path.join(
            self.game_resource_path, resource_hash[:2], resource_hash)
        backup_resource_path = os.path.join(
            self.backup_path, resource_hash[:2], resource_hash)
        # replace game resource with backup resource
        shutil.copyfile(backup_resource_path, game_resource_path)

    def add_resource(self, resource_id: str, resource_hash: str, resource_path: str):
        mod_resource_path = os.path.join(
            self.resource_path, resource_id, resource_hash)
        os.makedirs(os.path.dirname(mod_resource_path), exist_ok=True)
        shutil.copyfile(resource_path, mod_resource_path)

    def init(self):
        # Create Resource Directory
        # os.makedirs(self.resource_path, exist_ok=True)
        # os.makedirs(self.backup_path, exist_ok=True)
        # os.makedirs(self.mod_path, exist_ok=True)
        # os.makedirs(self.game_resource_path, exist_ok=True)
        pass

    def close(self):
        pass
