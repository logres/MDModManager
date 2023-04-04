from .resource_manager import ResourceManager
import json
import os


class Resource:
    def __init__(self, id: str, resource_hash: str, name: str, description: str, resource_type: str) -> None:
        self.id = id
        self.resource_hash = resource_hash
        self.name = name
        self.description = description
        self.resource_type = resource_type

    def to_json(self):
        return {"id": self.id, "resource_hash": self.resource_hash, "name": self.name, "description": self.description,
                "resource_type": self.resource_type}

    @staticmethod
    def from_json(data) -> "Resource":
        return Resource(id=data["id"], resource_hash=data["resource_hash"], name=data["name"], description=data["description"],
                        resource_type=data["resource_type"])


class Mod:
    def __init__(self, id: str, name: str, description: str, resource_ids: list[str]) -> None:
        self.id = id
        self.name = name
        self.description = description
        self.resource_ids = resource_ids

    def to_json(self):
        return {"id": self.id, "name": self.name, "description": self.description,
                "resource_ids": self.resource_ids}

    @staticmethod
    def from_json(data) -> "Mod":
        return Mod(id=data["id"], name=data["name"], description=data["description"],
                   resource_ids=data["resource_ids"])


class Record:
    def __init__(self, id: str, resource_id: str) -> None:
        self.id = id
        self.resource_id = resource_id

    def to_json(self):
        return {"id": self.id, "resource_id": self.resource_id}

    @staticmethod
    def from_json(data) -> "Record":
        return Record(id=data["id"], resource_id=data["resource_id"])

    def __eq__(self, o: object) -> bool:
        if isinstance(o, Record):
            return self.id == o.id and self.resource_id == o.resource_id
        return False


class ModManager:
    def __init__(self, local_path, target_path) -> None:
        self._local_path = local_path
        self._target_path = target_path
        # mods: Dict[str, Mod], resources: Dict[str, Resource], records: list[Record]
        self._data = self.load_data()
        self.resource_manager = ResourceManager(
            local_path=local_path, target_path=target_path)

    def apply_mod(self, mod_id: str):
        """
        应用mod
        """
        mod = self._data["mods"][mod_id]
        for resource_id in mod.resource_ids:
            self.resource_manager.apply_resource(
                resource_id, resource_hash=self._data["resources"][resource_id].resource_hash)
            self._data["records"].append(
                Record(id=mod_id, resource_id=resource_id))
        print("Mod applied.")

    def reset_mod(self, mod_id: str):
        """
        重置mod
        """
        mod = self._data["mods"][mod_id]
        for resource_id in mod.resource_ids:
            self.resource_manager.reset_resource(
                resource_hash=self._data["resources"][resource_id].resource_hash)
            self._data["records"].remove(
                Record(id=mod_id, resource_id=resource_id))
        print("Mod reset.")

    def get_mods(self) -> list[Mod]:
        return self._data["mods"].values()

    def get_resources(self) -> list[Resource]:
        return self._data["resources"].values()

    def get_records(self) -> list[Record]:
        return self._data["records"]

    def get_mod(self, mod_id: str) -> Mod:
        return self._data["mods"][mod_id]

    def get_resource(self, resource_id: str) -> Resource:
        return self._data["resources"][resource_id]

    def get_record(self, record_id: str) -> Record:
        return self._data["records"][record_id]

    def get_mod_preview(self, mod_id: str, size: tuple[int, int]) -> list[Resource]:
        return self.resource_manager.get_mod_preview(mod_id, size)

    def load_data(self):
        data_path = os.path.join(self._local_path, "data.json")
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
            data = {
                "mods": {mod["id"]: Mod.from_json(mod) for mod in raw_data["mods"]},
                "resources": {resource["id"]: Resource.from_json(resource) for resource in raw_data["resources"]},
                "records": [Record.from_json(record) for record in raw_data["records"]],
                "max_mod_id": raw_data["max_mod_id"],
                "max_resource_id": raw_data["max_resource_id"]
            }
        except FileNotFoundError:
            data = {"mods": {}, "resources": {}, "records": [], "max_mod_id": 1, "max_resource_id": 1}
            with open(data_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        return data

    def save_data(self):
        data_path = os.path.join(self._local_path, "data.json")
        with open(data_path, "w", encoding="utf-8") as f:
            json.dump({
                "mods": [mod.to_json() for mod in self._data["mods"].values()],
                "resources": [resource.to_json() for resource in self._data["resources"].values()],
                "records": [record.to_json() for record in self._data["records"]],
                "max_mod_id": self._data["max_mod_id"],
                "max_resource_id": self._data["max_resource_id"]
            }, f, ensure_ascii=False, indent=4)

    def add_resource(self, resource_path: str, name: str, description: str, resource_type: str):
        # 记录资源
        resource_id = str(int(self._data['max_resource_id']) + 1)
        self._data['max_resource_id'] = resource_id
        resource_hash = resource_path.split("/")[-1]
        self.resource_manager.add_resource(
            resource_id, resource_hash, resource_path)
        self._data["resources"][str(resource_id)] = Resource(
            id=str(resource_id), resource_hash=resource_hash, name=name, description=description, resource_type=resource_type)

    def delete_mod(self, mod_id: str):
        # 删除mod
        # mod = self._data["mods"][mod_id]
        # for resource_id in mod.resource_ids:
        #     self.resource_manager.delete_resource(
        #         resource_hash=self._data["resources"][resource_id].resource_hash)
        del self._data["mods"][mod_id]

    def add_mod(self, resource_ids: list[str], name: str, description: str, preview_path: str):
        # 记录mod
        mod_id = str(int(self._data['max_mod_id']) + 1)
        self._data['max_mod_id'] = mod_id
        self._data['max_mod_id'] = mod_id
        self._data["mods"][str(mod_id)] = Mod(
            id=str(mod_id), name=name, description=description, resource_ids=resource_ids)
        if preview_path:
            self.resource_manager.add_mod_preview(
                mod_id, preview_path
            )

    def init(self):
        self.resource_manager.init()

    def close(self):
        self.resource_manager.close()
        self.save_data()
