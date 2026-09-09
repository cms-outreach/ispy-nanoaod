"""
User interface controls for the event display.
"""
import ipywidgets as widgets
from typing import Callable, List, Optional

class EventControls:
    """
    Manages UI controls for event navigation and display options.
    """

    def __init__(self):
        """Initialize the controls."""
        self.prev_button = None
        self.next_button = None
        # Persistent container for visibility checkboxes - its children are
        # replaced (not the container itself) whenever the set of object
        # types changes, so an already-displayed widget updates in place.
        self.visibility_container = widgets.HBox()

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

    def setup_visibility_toggles(self,
                                type_names: List[str],
                                toggle_callback: Callable[[str, bool], None]):
        """
        (Re)build one visibility checkbox per object type. Replaces any
        previously built checkboxes, e.g. after loading a file with a
        different set of available collections.

        Parameters:
        -----------
        type_names : list of str
            Object type names to show a toggle for, e.g. ['MET', 'PV', 'Jet', 'Muon']
        toggle_callback : callable
            Called as toggle_callback(type_name, visible) when a checkbox changes
        """
        checkboxes = []
        for type_name in type_names:
            checkbox = widgets.Checkbox(
                value=True,
                description=type_name,
                indent=False,
                layout=widgets.Layout(width='110px')
            )
            checkbox.observe(
                lambda change, t=type_name: toggle_callback(t, change['new']),
                names='value'
            )
            checkboxes.append(checkbox)

        self.visibility_container.children = checkboxes

    def create_visibility_widget(self) -> widgets.Widget:
        """
        Create the visibility toggle widget.

        Returns:
        --------
        widgets.Widget
            Container of visibility checkboxes, updated in place by
            setup_visibility_toggles()
        """
        return self.visibility_container
