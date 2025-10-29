"""
3D rendering and scene management.
"""
import json
from pythreejs import *
from typing import List, Callable, Optional, Union

class EventRenderer:
    """
    Manages the 3D scene, camera, lighting, and rendering.
    """
    
    def __init__(self, width: int = 800, height: int = 500, background: str = '#232323'):
        """
        Initialize the renderer.
        
        Parameters:
        -----------
        width : int
            Renderer width in pixels
        height : int
            Renderer height in pixels
        background : str
            Background color (hex string)
        """
        self.width = width
        self.height = height
        self.background = background
        
        # Setup components
        self._setup_lights()
        self._setup_camera()
        self._setup_scene()
        self._setup_renderer()
        
        # State
        self.picker = None
        self.last_hovered_object = None
        
    def _setup_lights(self):
        """Setup scene lighting."""
        light_pos = 15.0
        self.lights = [
            DirectionalLight(
                color='white',
                position=[-light_pos, light_pos, light_pos],
                intensity=1
            ),
            DirectionalLight(
                color='white',
                position=[light_pos, -light_pos, -light_pos],
                intensity=1
            )
        ]
        
    def _setup_camera(self):
        """Setup perspective camera."""
        self.camera = PerspectiveCamera(
            position=[5, 5, 10],
            up=[0, 1, 0],
            children=self.lights,
            aspect=self.width / self.height
        )
        
    def _setup_scene(self):
        """Setup the 3D scene."""
        self.scene = Scene(background=self.background)
        
    def _setup_renderer(self):
        """Setup the threejs renderer with controls."""
        self.renderer = Renderer(
            camera=self.camera,
            scene=self.scene,
            controls=[OrbitControls(controlling=self.camera)],
            width=self.width,
            height=self.height
        )
        
    def add_objects(self, objects: Union[List, object]):
        """
        Add 3D objects to the scene.
        
        Parameters:
        -----------
        objects : list or single object
            3D objects to add to the scene
        """
        if not isinstance(objects, list):
            objects = [objects]
            
        for obj in objects:
            if isinstance(obj, list):
                # Handle nested lists
                self.add_objects(obj)
            else:
                self.scene.add(obj)
                
    def clear_scene(self):
        """Remove all objects from the scene."""
        self.scene.children = []
        
    def setup_picking(self, hover_callback: Optional[Callable] = None):
        """
        Setup object picking/hovering functionality.
        
        Parameters:
        -----------
        hover_callback : callable, optional
            Function to call when objects are hovered
        """
        if self.picker is None:
            self.picker = Picker(
                controlling=self.scene,
                event='mousemove',
                lineThreshold=0.1,
                pointThreshold=0.1,
                all=True
            )
            
            # Add picker to renderer controls
            current_controls = list(self.renderer.controls)
            current_controls.append(self.picker)
            self.renderer.controls = current_controls
            
        # Setup hover handling
        def on_object_hovered(change):
            hovered_object = change['new']
            
            # Reset previous object
            if (self.last_hovered_object and
                self.last_hovered_object != hovered_object):
                self._reset_object_appearance(self.last_hovered_object)
                
            # Handle new hovered object
            if hovered_object and hasattr(hovered_object, 'name'):
                self._highlight_object(hovered_object)
                
                if hover_callback:
                    obj_info = self._get_object_info(hovered_object)
                    hover_callback(hovered_object, obj_info)
                    
                self.last_hovered_object = hovered_object
            else:
                if hover_callback:
                    hover_callback(None, None)
                self.last_hovered_object = None
                
        self.picker.observe(on_object_hovered, names=['object'])
        
    def _highlight_object(self, obj):
        """Highlight a hovered object."""

        # Don't highlight EB
        if obj.name == 'EB':
            return

        if hasattr(obj, 'material') and hasattr(obj.material, 'color'):
            obj.material.color = '#ffffff'
            
    def _reset_object_appearance(self, obj):
        """Reset object to original appearance."""
        if not hasattr(obj, 'name') or not hasattr(obj, 'material'):
            return
            
        # Reset colors based on object type.
        # This should be somewhere central.
        # And if we change the colors in the API
        # these no longer apply.
        color_map = {
            'Jet': '#ffff00',
            'MET': '#ff00ff',
            'Muon': '#ff0000',
            'Electron': '#19ff19',
            'PV': '#ffff00',
            'SV': '#ff6600',
            'FatJet': '#ff6600',
            'IsoTrack': '#ffff00',
            'Photon': '#ffff00'
        }
        
        if obj.name in color_map and hasattr(obj.material, 'color'):
            obj.material.color = color_map[obj.name]
            
    def _get_object_info(self, obj) -> Optional[str]:
        """Get formatted information string for an object."""
        if hasattr(obj, 'props') and obj.props:
            return f"{obj.name} {json.dumps(obj.props)}"
        elif hasattr(obj, 'name'):
            return obj.name
        return None
        
    def set_camera_position(self, position: List[float]):
        """
        Set camera position.
        
        Parameters:
        -----------
        position : list
            [x, y, z] camera position
        """
        self.camera.position = position
        
    def set_background_color(self, color: str):
        """
        Set scene background color.
        
        Parameters:
        -----------
        color : str
            Background color (hex string)
        """
        self.background = color
        self.scene.background = color
        
    def get_widget(self):
        """
        Get the renderer widget for display in notebooks.
        
        Returns:
        --------
        Renderer
            The pythreejs renderer widget
        """
        return self.renderer
        
    def reset_view(self):
        """Reset camera to default position and orientation."""
        self.camera.position = [5, 5, 10]
        self.camera.up = [0, 1, 0]
        
    def fit_to_view(self, objects: Optional[List] = None):
        """
        Adjust camera to fit objects in view.
        
        Parameters:
        -----------
        objects : list, optional
            Specific objects to fit. If None, fits all scene objects.
        """
        # This would require calculating bounding boxes
        # and adjusting camera distance accordingly
        # For now, just reset to a reasonable default
        self.reset_view()
