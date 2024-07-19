import os
from PyPDF2 import PdfReader

from VectorDB.chromadb.chroma import Chroma
#from models import Document, ChromdbQuery, File, Query
from models import Document, File, Query
from module_manager import classregistry

db = Chroma("chromadb")

@classregistry.register('chromadb', )
class ChromadbModule:
    def __init__(self, name):
        self.name = name
        pass

    def some_method(self):
        pass

    def load(self, file: File):
        filename = os.path.basename(file.path)
        fulltext = ""

        with open(file.path, "rb") as f:
            pdf = PdfReader(f)

            for page in pdf.pages:
                text = page.extract_text()
                chunks = [text[i:i+1000] for i in range(0, len(text), 900)]
                pageNum = pdf.get_page_number(page)
                fulltext += text

                for i, chunk in enumerate(chunks):
                    doc = Document(
                        id=f"{filename}-p{pageNum}-{i}",
                        text=chunk,
                        metadata={"filename": filename, "page": pageNum}
                    )
                    print("Upserting: ", doc.id)
                    db.upsert(doc)
        
        return {
            "filename": filename,
            "total_pages": len(pdf.pages),
            "data": "chromadb load ok"
        }
    
#    def query(self, query: ChromdbQuery) -> list[Document]:
    def query(self, query: Query) -> list[Document]:
        result = db.query(query.query, query.top_k)

        print(result)
        return result
    

if __name__ == '__main__':

    chromadb = ChromadbInterface("chromadb")
    file = File(path="./File/sample.pdf")
    file.path = "./File/sample.pdf"
    chromadb.load(file)

    query = Query(query="이 논문의 내용은 어떤 내용이에요?", top_k=1)
    print(chromadb.query(query))









    