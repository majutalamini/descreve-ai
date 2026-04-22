import google.generativeai as genai
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List
import PIL.Image
import io
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")
else:
    @app.get("/")
    async def serve_index():
        return FileResponse("index.html")
    
    @app.get("/{filename}")
    async def serve_static(filename: str):
        if os.path.exists(filename):
            return FileResponse(filename)
        raise HTTPException(status_code=404)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise Exception("GOOGLE_API_KEY não encontrada. Configure o arquivo .env")

genai.configure(api_key=GOOGLE_API_KEY)

modelo_disponivel = None
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        modelo_disponivel = m.name
        print(f"Modelo encontrado: {m.name}")
        break

if not modelo_disponivel:
    raise Exception("Nenhum modelo disponível")

model = genai.GenerativeModel(model_name=modelo_disponivel)

@app.post("/gerar-guia")
async def gerar_guia(files: List[UploadFile] = File(...)):
    try:
        imagens_processadas = []
        
        for file in files:
            conteudo = await file.read()
            img = PIL.Image.open(io.BytesIO(conteudo)).convert("RGB")
            imagens_processadas.append(img)

        if not imagens_processadas:
            raise HTTPException(status_code=400, detail="Nenhuma imagem enviada.")

        prompt = (
            "Você é um assistente especializado em criar guias passo a passo a partir de imagens.\n\n"
            "Analise estas imagens que mostram um procedimento sequencial (ex: instalação de software, "
            "configuração de sistema, tutorial de aplicativo, etc.).\n\n"
            "Siga estas regras rigorosamente:\n"
            "1. Identifique qual procedimento está sendo mostrado nas imagens\n"
            "2. Comece com uma frase de introdução amigável: 'Siga os passos para [ação principal]:'\n"
            "3. Para cada passo, use o formato: 'Número - Ação > Subação > Detalhe'\n"
            "4. Seja claro, direto e objetivo\n"
            "5. Use verbos de ação no imperativo (Ex: Clique, Digite, Selecione, Acesse)\n"
            "6. Não adicione explicações extras, apenas os passos numerados\n"
            "7. Mantenha uma linha em branco entre a introdução e o primeiro passo\n\n"
            "EXEMPLO DE SAÍDA ESPERADA:\n"
            "Siga os passos para instalar o Minecraft na sua máquina:\n\n"
            "1 - Entre em seu navegador > Digite 'minecraft.net' > Acesse o site oficial\n"
            "2 - Clique em 'Download' > Escolha seu sistema operacional > Baixe o instalador\n"
            "3 - Execute o arquivo baixado > Siga as instruções da tela > Conclua a instalação\n\n"
            "Agora analise as imagens enviadas e gere o guia no mesmo formato:"
        )
        
        response = model.generate_content([prompt, *imagens_processadas])
        
        return {"guia": response.text}

    except Exception as e:
        print(f"Erro no servidor: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)