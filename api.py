from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import asyncio
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from browser_use import Agent
import gradio as gr
from gradio.themes import Soft

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Browser Use API",
    description="API for browser automation tasks",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TaskRequest(BaseModel):
    task: str
    api_key: Optional[str] = None
    model: str = "gpt-4o"
    headless: bool = True

class TaskResponse(BaseModel):
    status: str
    result: str
    error: Optional[str] = None

# Create Gradio interface
def create_ui():
    with gr.Blocks(title='Browser Use GUI', theme=Soft()) as interface:
        gr.Markdown("""
        # 🌐 Browser Use Task Automation
        
        This interface allows you to automate browser tasks using AI. Enter your task description and API key to get started.
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                api_key = gr.Textbox(
                    label='OpenAI API Key',
                    placeholder='sk-...',
                    type='password',
                    info='Required for API access'
                )
                
                task = gr.Textbox(
                    label='Task Description',
                    placeholder='E.g., Find flights from New York to London for next week',
                    lines=3,
                    info='Describe what you want the browser to do'
                )
                
                with gr.Row():
                    model = gr.Dropdown(
                        choices=['gpt-4o', 'gpt-3.5-turbo'],
                        label='Model',
                        value='gpt-4o',
                        info='Choose the AI model to use'
                    )
                    headless = gr.Checkbox(
                        label='Run Headless',
                        value=True,
                        info='Run browser in background'
                    )
                
                submit_btn = gr.Button(
                    'Run Task',
                    variant='primary',
                    size='lg'
                )
                
            with gr.Column(scale=1):
                output = gr.Textbox(
                    label='Output',
                    lines=10,
                    interactive=False,
                    info='Task execution results will appear here'
                )
                
                with gr.Row():
                    clear_btn = gr.Button('Clear Output')
                    copy_btn = gr.Button('Copy to Clipboard')
        
        # Add event handlers
        submit_btn.click(
            fn=lambda *args: asyncio.run(run_browser_task(*args)),
            inputs=[task, api_key, model, headless],
            outputs=output,
        )
        
        clear_btn.click(
            fn=lambda: "",
            outputs=output
        )
        
        copy_btn.click(
            fn=lambda text: text,
            inputs=output,
            outputs=gr.Textbox(label="Copied!", visible=False)
        )
        
        # Add examples
        gr.Examples(
            examples=[
                ["Search for flights from New York to London for next week"],
                ["Find the best restaurants in San Francisco"],
                ["Compare prices for a new laptop"],
                ["Book a hotel in Paris for next month"],
                ["Find job openings for software engineers in New York"]
            ],
            inputs=task
        )
        
        # Add footer
        gr.Markdown("""
        ---
        Made with ❤️ using Browser Use
        
        Note: Make sure you have a valid OpenAI API key and sufficient credits.
        """)
        
        return interface

async def run_browser_task(
    task: str,
    api_key: str,
    model: str = 'gpt-4o',
    headless: bool = True,
) -> str:
    if not api_key.strip():
        return 'Please provide an API key'

    os.environ['OPENAI_API_KEY'] = api_key
    
    try:
        agent = Agent(
            task=task,
            llm=ChatOpenAI(model=model),
        )
        result = await agent.run()
        return str(result)
    except Exception as e:
        return f"Error occurred: {str(e)}"

@app.post("/run-task", response_model=TaskResponse)
async def run_task(request: TaskRequest):
    try:
        if request.api_key:
            os.environ['OPENAI_API_KEY'] = request.api_key
        elif not os.getenv('OPENAI_API_KEY'):
            raise HTTPException(status_code=400, detail="OpenAI API key is required")

        result = await run_browser_task(
            task=request.task,
            api_key=request.api_key or "",
            model=request.model,
            headless=request.headless
        )

        return TaskResponse(
            status="success",
            result=result
        )

    except Exception as e:
        return TaskResponse(
            status="error",
            result="",
            error=str(e)
        )

# Create Gradio interface
interface = create_ui()

# Mount Gradio app
app = gr.mount_gradio_app(app, interface, path="/")

# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 