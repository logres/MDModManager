import PySimpleGUI as sg
from manager import ModManager, Mod


# def format_tree_resources(mods: list[Mod]) -> sg.TreeData:
#     tree_data = sg.TreeData()
#     for mod in mods:
#         tree_data.Insert("", mod.id, mod.name, values=[mod.description])
#     return tree_data


class Data:
    def __init__(self, id, name) -> None:
        self.id = id
        self.name = name

    @classmethod
    def from_mod(cls, mod: Mod):
        return cls(id=mod.id, name=mod.name)

    @classmethod
    def from_mods(cls, mods: list[Mod]):
        return [cls.from_mod(mod) for mod in mods]

    @classmethod
    def from_resource(cls, resource):
        return cls(id=resource.id, name=resource.name)

    @classmethod
    def from_resources(cls, resources):
        return [cls.from_resource(resource) for resource in resources]


class ListTreeComponent:
    def __init__(self, window, key) -> None:
        self._window = window
        self._key = key

    def render(self, data_list: list[Data]):
        the_key = self._key+"TREE-"
        self._window[the_key].update(values=self.generate_tree(data_list))

    @staticmethod
    def generate_tree(data_list: list[Data]):
        tree_data = sg.TreeData()
        for data in data_list:
            tree_data.Insert("", data.id, data.name, values=[])
        return tree_data

    def layout(self, tree_data=sg.TreeData()):
        return sg.Tree(data=tree_data, headings=[], auto_size_columns=True,
                       num_rows=20, col0_width=20, key=self._key+"TREE-", show_expanded=False, enable_events=True,)

    def get_key(self):
        return self._key+"TREE-"


class InfoPreviewComponent:
    def __init__(self, window, key) -> None:
        self._window = window
        self._key = key

    def render(self, name, description, image):
        if image is None:
            image = b""
        self._window[self._key+"IMAGE-"].update(data=image)
        self._window[self._key+"TITLE-"].update(name)
        self._window[self._key+"DES-"].update(description)

    def layout(self):
        return sg.Column([[sg.Image(key=self._key+"IMAGE-")],
                          [sg.Text("Title", key=self._key+"TITLE-")],
                          [sg.Text("Description", key=self._key+"DES-")]])


# TODO: 组件式编程

class App:
    def __init__(self) -> None:
        local_path = sg.popup_get_folder("选择本地Mod路径")
        game_resource_path = sg.popup_get_folder("选择游戏资源路径")
        self.mod_manager = ModManager(
            local_path=local_path, target_path=game_resource_path)

    def import_resource(self):
        layout = [
            [sg.Text("选择文件：")],
            [sg.Input(), sg.FileBrowse()],
            [sg.Text("名称：")],
            [sg.Input()],
            [sg.Text("描述：")],
            [sg.Input()],
            [sg.Text("类型:,")],
            [sg.Input()],
            [sg.Button("确定"), sg.Button("取消")],
        ]
        window = sg.Window("导入资源", layout)
        while True:
            event, values = window.read()
            if event in (sg.WINDOW_CLOSED, "取消"):
                window.close()
                return None
            elif event == "确定":
                filename = values[0]
                name = values[1]
                description = values[2]
                resource_type = values[3]
                window.close()
                return {"filename": filename, "name": name, "description": description, "resource_type": resource_type}

    def create_mod(self):
        # Choose Resource From A Tree to Create A Mod
        info_preview = InfoPreviewComponent(None, key="-INFO-")
        resource_tree = ListTreeComponent(None, key="-THE-RESOURCE-")
        layout = [
            [sg.Text("选择资源：")],
            [resource_tree.layout(ListTreeComponent.generate_tree(Data.from_resources(self.mod_manager.get_resources()))),
             info_preview.layout()],
            [sg.Text("Mod资源：")],
            [sg.Input(key="-RESOURCE-")],
            [sg.Text("Mod名称：")],
            [sg.Input(key="-NAME-")],
            [sg.Text("Mod描述：")],
            [sg.Input(key="-DESCRIPTION-")],
            [sg.Text("Mod图片(可选)：")],
            [sg.Input(key="-IMAGE-"), sg.FileBrowse()],
            [sg.Button(key="-ADD-", button_text="添加"),
             sg.Button(key="-REMOVE-", button_text="移除")],
            [sg.Button(key="-COMMIT-", button_text="确定"),
             sg.Button(key="-CANCEL-", button_text="取消")],
        ]
        window = sg.Window("新建Mod", layout)
        info_preview._window = window
        resource_tree._window = window
        # resource_tree.render(Data.from_resources(self.mod_manager.get_resources()))
        resource_ids = set()
        while True:
            event, values = window.read()
            print(event, values)
            if event in (sg.WINDOW_CLOSED, "取消"):
                window.close()
                return None
            elif event == resource_tree.get_key():
                resource_id = values[resource_tree.get_key()][0]
                resource = self.mod_manager.get_resource(resource_id)
                info_preview.render(resource.name, resource.description, None)
            elif event == "-COMMIT-":
                name = values["-NAME-"]
                description = values["-DESCRIPTION-"]
                image = values["-IMAGE-"]
                window.close()
                return {"resource_ids": list(resource_ids), "name": name, "description": description, "image": image}
            elif event == "-ADD-":
                resource_id = values[resource_tree.get_key()][0]
                print(resource_id)
                resource_ids.add(resource_id)
                resource_names = [self.mod_manager.get_resource(
                    resource_id).name for resource_id in resource_ids]
                window["-RESOURCE-"].update(",".join(resource_names))
            elif event == "-REMOVE-":
                resource_id = values["-TREE-"][0]
                resource_ids.remove(resource_id)
                resource_names = [self.mod_manager.get_resource(
                    resource_id).name for resource_id in resource_ids]
                window["-RESOURCE-"].update(",".join(resource_names))

    def run(self):
        sg.theme("Dark Blue 3")
        tree_mod = ListTreeComponent(None, "-MAIN-MOD-")
        tree_resource = ListTreeComponent(None, "-MAIN-RESOURCE-")
        tree_tab_group = sg.TabGroup([
            [
                sg.Tab("Mod", [[tree_mod.layout()]], key="-TAB-MOD-"),
                sg.Tab("Resource", [[tree_resource.layout()]],
                       key="-TAB-RESOURCE-")
            ]
        ], key="-TAB-GROUP-", enable_events=True)
        previewer = InfoPreviewComponent(None, "-INFO-")
        layout = [
            [sg.Button(key="-LOAD-RESOURCE-", button_text="导入资源"),
             sg.Button(key="-New-Mod-", button_text="新建Mod")],
            [tree_tab_group, sg.VSeperator(), previewer.layout()],
            [sg.Button(key="-APPLY-", button_text="应用"),
             sg.Button(key="-RESET-", button_text="重置"),
             sg.Button(key="-DELETE-", button_text="删除")]
        ]
        window = sg.Window("Md Mod 管理器", layout)
        tree_mod._window = window
        tree_resource._window = window
        previewer._window = window

        while True:
            event, values = window.read()
            print(event, values)
            if event == sg.WINDOW_CLOSED:
                # 处理窗口关闭事件
                self.mod_manager.close()
                break
            elif event == "-LOAD-RESOURCE-":
                the_resource = self.import_resource()
                if the_resource is not None:
                    self.mod_manager.add_resource(
                        the_resource["filename"], the_resource["name"], the_resource["description"], the_resource["resource_type"])
                # update tree
                tree_resource.render(
                    Data.from_resources(self.mod_manager.get_resources()))
            elif event == "-New-Mod-":
                the_mod = self.create_mod()
                if the_mod is not None:
                    self.mod_manager.add_mod(
                        the_mod["resource_ids"], the_mod["name"], the_mod["description"], the_mod["image"])
                # update tree
                tree_mod.render(
                    Data.from_mods(self.mod_manager.get_mods()))
            elif event == "-TAB-GROUP-":
                if window['-TAB-GROUP-'].get() == "-TAB-MOD-":
                    tree_mod.render(
                        Data.from_mods(self.mod_manager.get_mods()))
                elif window['-TAB-GROUP-'].get() == "-TAB-RESOURCE-":
                    tree_resource.render(
                        Data.from_resources(self.mod_manager.get_resources()))
            elif event == "-APPLY-":
                if window['-TAB-GROUP-'].get() == "-TAB-MOD-":
                    mod_id = values["-MAIN-MOD-TREE-"][0]
                    self.mod_manager.apply_mod(mod_id)
            elif event == "-RESET-":
                if window['-TAB-GROUP-'].get() == "-TAB-MOD-":
                    mod_id = values["-MAIN-MOD-TREE-"][0]
                    self.mod_manager.reset_mod(mod_id)
            elif event == "-DELETE-":
                if window['-TAB-GROUP-'].get() == "-TAB-MOD-":
                    mod_id = values["-MAIN-MOD-TREE-"][0]
                    self.mod_manager.delete_mod(mod_id)
                    tree_mod.render(
                        Data.from_mods(self.mod_manager.get_mods()))
            elif event == tree_mod.get_key():  # 实际上就一个Key
                if len(values[event]) == 0:
                    continue
                mod_id = values[event][0]
                mod = self.mod_manager.get_mod(mod_id)
                previewer.render(
                    mod.name, mod.description, self.mod_manager.get_mod_preview(
                        mod_id, size=(500, 500))
                )
            elif event == tree_resource.get_key():
                if len(values[event]) == 0:
                    continue
                resource_id = values[event][0]
                resource = self.mod_manager.get_resource(resource_id)
                previewer.render(resource.name, resource.description, None)


if __name__ == "__main__":
    App().run()
    # main()
