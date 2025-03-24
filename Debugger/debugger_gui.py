import tkinter as tk
from tkinter import ttk
import threading

from FlowAgents.handoff_agent import HandoffAgent


class AgentDebugGUI:
    def __init__(self, agent):
        self.agent = agent
        self.root = None
        self.frame = None
        self.running = True
        
        # Start GUI in a separate thread
        self.thread = threading.Thread(target=self._run_gui)
        self.thread.daemon = True
        self.thread.start()
    
    def _run_gui(self):
        """Run the GUI in a separate thread"""
        self.root = tk.Tk()
        self.root.title("Agent Debug GUI")
        self.root.geometry("1200x800")
        
        # Create main container that fills window
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create scrollable canvas for content
        canvas = tk.Canvas(main_container)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        
        # Create the frame that will contain all our content
        self.frame = ttk.Frame(canvas)
        
        # Configure scrolling
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.create_window((0, 0), window=self.frame, anchor="nw")
        
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        self.frame.bind("<Configure>", configure_scroll_region)
        
        # Pack the scrollbar and canvas
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Refresh button at bottom
        refresh_button = ttk.Button(
            self.root, text="Refresh", command=self.refresh
        )
        refresh_button.pack(side=tk.BOTTOM, pady=10)
        
        # Initial refresh
        self.refresh()
        
        # Start GUI main loop
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.root.mainloop()
    
    def _on_closing(self):
        """Handle GUI window closing"""
        self.running = False
        self.root.destroy()
    
    def refresh(self):
        """Refresh the GUI with current agent state"""
        if not self.running or not self.frame:
            return
            
        # Clear the current display
        for widget in self.frame.winfo_children():
            widget.destroy()
        
        # Draw the agent tree
        self._draw_agent(self.agent, self.frame)
    
    def _draw_agent(self, agent, parent_frame, level=0):
        """Draw an agent and its conversation in the tree view"""
        # Agent frame with collapsible content
        agent_frame = ttk.Frame(parent_frame)
        agent_frame.pack(fill=tk.X, expand=True, pady=2)
        
        # Agent header with toggle button
        header_frame = ttk.Frame(agent_frame)
        header_frame.pack(fill=tk.X, expand=True)
        
        expanded = tk.BooleanVar(value=True)
        toggle_btn = ttk.Button(header_frame, text="▼", width=2)
        toggle_btn.pack(side=tk.LEFT, padx=(level*20, 0))
        
        ttk.Label(header_frame, text=agent.name).pack(side=tk.LEFT, padx=5)
        
        # Agent content (will be toggled)
        content_frame = ttk.Frame(agent_frame)
        content_frame.pack(fill=tk.X, expand=True, padx=10)
        
        def toggle_content():
            if expanded.get():
                content_frame.pack_forget()
                toggle_btn.configure(text="►")
                expanded.set(False)
            else:
                content_frame.pack(fill=tk.X, expand=True, padx=10)
                toggle_btn.configure(text="▼")
                expanded.set(True)
        
        toggle_btn.configure(command=toggle_content)
        
        # Conversation section
        conversation_frame = ttk.LabelFrame(content_frame, text="Conversation")
        conversation_frame.pack(fill=tk.X, expand=True, pady=5)
        
        # Display conversation messages
        conversation = agent.chat_flow_manager.chat_flow
        if not conversation:
            ttk.Label(conversation_frame, text="No conversation yet").pack(padx=10, pady=5)
        else:
            for message in conversation:
                self._draw_message(message, conversation_frame)
        
        # If this is a HandoffAgent, show subagents
        if isinstance(agent, HandoffAgent) and agent.subagents:
            for subagent in agent.subagents:
                self._draw_agent(subagent, content_frame, level + 1)
    
    def _draw_message(self, message, parent_frame):
        """Draw a message with proper expand/collapse functionality"""
        # Message container
        msg_container = ttk.Frame(parent_frame)
        msg_container.pack(fill=tk.X, expand=True, pady=1)
        
        # Message header with toggle
        header = ttk.Frame(msg_container)
        header.pack(fill=tk.X, expand=True)
        
        # Expansion state
        expanded = tk.BooleanVar(value=False)
        
        # Toggle button
        toggle_btn = ttk.Button(header, text="►", width=2)
        toggle_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # Message preview label
        label_text = f"[{message.importance}]. [{message.messagerole.value}]"
        ttk.Label(header, text=label_text, width=20).pack(side=tk.LEFT, padx=5)
        
        # Message content in a text widget that wraps properly
        content_preview = tk.Text(header, wrap=tk.WORD, height=1, width=80)
        content_preview.insert("1.0", message.message)
        content_preview.configure(state="disabled")
        content_preview.pack(fill=tk.X, expand=True, padx=5)
        
        # Details frame (hidden by default)
        details_frame = ttk.Frame(msg_container)
        
        # Content in full
        content_full = tk.Text(details_frame, wrap=tk.WORD, height=10, width=80)
        content_full.insert("1.0", message.message)
        content_full.configure(state="disabled")
        content_full.pack(fill=tk.X, expand=True, padx=5, pady=5)
        
        # Message metadata
        metadata = ttk.Frame(details_frame)
        metadata.pack(fill=tk.X, expand=True, pady=5)
        
        ttk.Label(metadata, text=f"Token Size: {message.get_token_size()}").pack(side=tk.LEFT, padx=5)
        
        created_at = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
        ttk.Label(metadata, text=f"Created: {created_at}").pack(side=tk.LEFT, padx=5)
        
        # Toggle function that shows/hides details
        def toggle_details():
            if expanded.get():
                details_frame.pack_forget()
                toggle_btn.configure(text="►")
                expanded.set(False)
            else:
                details_frame.pack(fill=tk.X, expand=True, padx=10, pady=5)
                toggle_btn.configure(text="▼")
                expanded.set(True)
        
        toggle_btn.configure(command=toggle_details)


def create_debug_gui(agent):
    """Create a non-blocking debug GUI for the agent"""
    return AgentDebugGUI(agent)
