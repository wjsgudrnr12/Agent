from models import *

class ClassRegistry:
    def __init__(self):
        self._registry = {}

    def register(self, name):
        def decorator(cls):
            self._registry[name] = cls
            print(f"class '{name}' registered successfully.")
            return cls
        return decorator

    def get(self, name):
        return self._registry.get(name)

classregistry = ClassRegistry()

@classregistry.register('my_class', )
class MyClass:
    def __init__(self, name):
        self.name = name

    def greet(self):
        print(f"Hello, {self.name}!")

class Module:
    def __init__(self, name):
        self.name = name

    def check_status(self):
        return self.is_running

class Manager:
    def __init__(self, name):
        self.name = name
        self.modules = {}
    
    def register_module(self, module):
        self.modules[module.name] = module
        print(f"Module '{module.name}' registered successfully.")

    def get_module(self, name):
        module = self.modules.get(name)
        if module:
            print(f"Module '{name}' found.")
            return module
        else:
            print(f"Module '{name}' not found.")
            return None

    def check_module_status(self, name):
        module = self.get_module(name)
        if module:
            status = "running" if module.check_status() else "not running"
            print(f"Module '{name}' is {status}.")
            return module.check_status()
        else:
            print(f"No status available for module '{name}'.")
            return None

manager = Manager("vectordb")

class MainManager:
    def __init__(self):
        self.managers = {}

    def register_manager(self, name, manager):
        self.managers[name] = manager
        print(f"Manager '{name}' registered successfully.")

    def get_manager(self, name):
        manager = self.managers.get(name)
        if manager:
            print(f"Manager '{name}' found.")
            return manager
        else:
            print(f"Manager '{name}' not found.")
            return None
        

def llm_load(modelname:str) -> Answer:
    print(modelname)
    llmclass = classregistry.get(modelname)
    if llmclass:        
        retrieved_instance = manager.get_module(modelname)
        if retrieved_instance is not None:
            print("The model you requested has already been loaded.")
            return {'content': "The model you requested has already been loaded." }        
        
        else:    
            instance = llmclass(modelname)
            instance.init()
            manager.register_module(instance)
            #answer = instance.gen("1980년대에 첫 번째 혁신적인 기술을 보셨다고 하셨는데, 어떤 기술이었나요?")
            return {'content': "model load ok" }
        
def llm_query(modelname:str, prompt: Prompt) -> Answer:
    print(modelname)
    retrieved_instance = manager.get_module(modelname)
    if retrieved_instance:
        answer = retrieved_instance.gen(prompt.content)
        return {'content': answer }
    else:
        print("not found....")
        return {'content': "not found...." }

