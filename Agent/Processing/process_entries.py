import argparse
from Modules.module_manager import Manager


def argparse_argument():
    parser = argparse.ArgumentParser(description="Agent Configuration")

    # 설정 인자 추가
    parser.add_argument('-vectordb', action='append', nargs=4, metavar=('ORG_NAME', 'IP', 'PORT', 'DB_NAMES:FILE,....'), help='Enter the name, IP, and port for a vector database')
    parser.add_argument('-llm', action='append', nargs=4, metavar=('ORG_NAME', 'IP', 'PORT','LLM_NAMES,....'), help='LLM_NAMES is the list of LLMs in ORG_NAME')
    # 인자 파싱
    args = parser.parse_args(['-vectordb', 'ETRI_vectordb', '127.0.0.1', '8001', 'customdb:./File/prompt-faq.csv,chromadb:./File/sample.pdf',
                              '-vectordb', 'KIST_vectordb', '127.0.0.1', '10001', 'test1db:aaa.csv,test2db:bbb.csv',
                              '-llm', 'ETRI_llm', '127.0.0.1', '8002', 'koalpaca_12_8',
                              '-llm', 'KIST_llm', '127.0.0.1', '10002', 'koalpaca_12_8'])
                                  
    return args


def process_entries(manager_type, entries, mainmanager, classregistry):
    if entries:
        manager = Manager(manager_type)
        mainmanager.register_manager(manager)

        for entry in entries:
            org_name, ip, port, names_files = entry
            retrived_class = classregistry.get(org_name)

            if retrived_class:
                instance = retrived_class(org_name, ip, port, names_files, manager)
                instance.load()
                manager.register_module(instance)
            else:
                print(f"{org_name} class not found")


