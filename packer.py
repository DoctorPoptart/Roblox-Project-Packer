from os.path import isdir, isfile, join, basename, dirname, exists, splitext
from os import listdir, getcwd, mkdir
from time import sleep

from sys import argv

header = 'metatable = {__index = function(self, index) if not rawget(self, index) then local tbl = setmetatable({}, metatable);self[index] = tbl;return tbl end end}\nmodules, loaded_modules, _require = setmetatable({}, metatable), {}, require'
bottom = 'function load(f) local a = loaded_modules[f] or f(); loaded_modules[f] = a; return a end\nfunction require(v) local t = typeof(v);if t == "function" then return load(v) elseif t == "table" then local a = v["main"];if a then return load(a) end end end'
module_format = "modules{path}['{name}'] = function()\n{source}\nend"
script_format = "return (function()\n{source}\nend)()"

def packer():
    cwd = getcwd()
    args = {i:v for i, v in enumerate(argv)}
    
    output = args.get(1, "output.lua")

    project = join(cwd, "project")
    init_file = join(project, "init.lua")

    def search(dir: str, modules: list, old_path=[]):
        found_module = False
        if dir == project:
            cur_path = []
        else:
            cur_path = [*old_path, basename(dir)]

        for path in listdir(dir):
            path = join(dir, path)   
            if isdir(path):
                has_modules, folder_path = search(path, modules, cur_path)
                if has_modules:
                    found_module = True
            else:
                bn = basename(path)
                rn, ext = splitext(bn)
                if "." in bn and ext == ".lua" and path != init_file:
                    found_module = True
                    with open(path, "r", encoding="utf-8") as file:
                        source = file.read()
                        module_path = "".join([f'["{c}"]' for c in cur_path])
                        tabbed_lines = "\n".join(["\t"+l for l in source.splitlines()])
                        
                        module = module_format.format(path=module_path, name=rn, source=tabbed_lines)
                        modules.append(module)
        return found_module, cur_path
                        

    def run():
        if not isdir(project): 
            mkdir(project)  
        if not isfile(init_file):
            open(init_file, "w").close()

        modules = []
        search(project, modules)

        with open(init_file, "r", encoding="utf-8") as file:
            tabbed_lines = "\n".join(["\t"+l for l in file.read().splitlines()])
            source = script_format.format(source=tabbed_lines)


        output_list = [header, *modules, bottom, source]

        with open(output, "w", encoding="utf-8") as file:
            file.write("\n\n".join(output_list))
    while True:
        sleep(0.1)
        try:
            run()
        except Exception:
            pass


packer()