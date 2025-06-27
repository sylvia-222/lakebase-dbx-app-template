import gradio as gr

def hello_world():
    return "hello world"

demo = gr.Interface(
    fn=hello_world,
    inputs=None,
    outputs="text",
    title="Hello World App"
)

if __name__ == "__main__":
    demo.launch() 