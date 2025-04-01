import asyncio
import os
from dataclasses import dataclass
from typing import List, Optional
import time
from datetime import datetime

# Third-party imports
import gradio as gr
from gradio.themes import Soft
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.table import Table

# Local module imports
from browser_use import Agent

load_dotenv()

@dataclass
class ActionResult:
    is_done: bool
    extracted_content: Optional[str]
    error: Optional[str]
    include_in_memory: bool

@dataclass
class AgentHistoryList:
    all_results: List[ActionResult]
    all_model_outputs: List[dict]

def create_status_table(status: str, start_time: float) -> Table:
    table = Table(show_header=False, box=None)
    table.add_row("Status", status)
    table.add_row("Time Elapsed", f"{time.time() - start_time:.1f}s")
    return table

def create_result_panel(content: str, step: int) -> Panel:
    header = Text(f'Step {step}', style='bold blue')
    return Panel(content, title=header, border_style='blue')

async def run_browser_task(
    task: str,
    api_key: str,
    model: str = 'gpt-4o',
    headless: bool = True,
    progress=gr.Progress(),
) -> str:
    if not api_key.strip():
        return 'Please provide an API key'

    os.environ['OPENAI_API_KEY'] = api_key
    start_time = time.time()
    console = Console()
    
    try:
        # Create progress tracking
        progress(0, desc="Initializing agent...")
        
        agent = Agent(
            task=task,
            llm=ChatOpenAI(model=model),
        )
        
        progress(0.2, desc="Running task...")
        result = await agent.run()
        
        progress(0.8, desc="Processing results...")
        
        # Format the result with timestamps and status
        formatted_result = f"""
Task: {task}
Started: {datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')}
Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Duration: {time.time() - start_time:.1f}s

Result:
{result}
"""
        
        progress(1.0, desc="Complete!")
        return formatted_result
        
    except Exception as e:
        error_msg = f"""
Error occurred:
{str(e)}

Time elapsed: {time.time() - start_time:.1f}s
"""
        return error_msg

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

if __name__ == "__main__":
    interface = create_ui()
    interface.launch(share=True) 