"""
User interface controls for the event display.
"""
import ipywidgets as widgets
from typing import Callable, Optional

class EventControls:
    """
    Manages UI controls for event navigation and display options.
    """
    
    def __init__(self):
        """Initialize the controls."""
        self.prev_button = None
        self.next_button = None
        
    def setup_navigation(self, 
                        prev_callback: Callable, 
                        next_callback: Callable,
                        max_events: int = 100):
        """
        Setup navigation controls.
        
        Parameters:
        -----------
        prev_callback : callable
            Function to call for previous event
        next_callback : callable
            Function to call for next event
        max_events : int
            Maximum number of events
        """
        self.prev_button = widgets.Button(
            description='',
            disabled=False,
            button_style='',
            tooltip='Previous Event',
            icon='step-backward'
        )
        
        self.next_button = widgets.Button(
            description='',
            disabled=False,
            button_style='',
            tooltip='Next Event', 
            icon='step-forward'
        )
        
        # Connect callbacks
        self.prev_button.on_click(lambda b: prev_callback())
        self.next_button.on_click(lambda b: next_callback())
        
    def create_widget(self) -> widgets.Widget:
        """
        Create the complete control widget.
        
        Returns:
        --------
        widgets.Widget
            Complete control interface
        """
        if self.prev_button is None or self.next_button is None:
            # Create simple navigation if not setup
            self.prev_button = widgets.Button(description='Previous')
            self.next_button = widgets.Button(description='Next')
            
        button_box = widgets.HBox([self.prev_button, self.next_button])

        return button_box
