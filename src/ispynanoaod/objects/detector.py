"""
Detector geometry components.
"""

import math
from pythreejs import *
from typing import List


class DetectorGeometry:
    """
    Creates 3D representations of detector components.
    """
    
    def __init__(self):
        """Initialize detector geometry with default parameters."""
        self.eb_config = {
            'radius_top': 1.12,
            'radius_bottom': 1.24,
            'height': 6.0,
            'color': '#7fccff',
            'opacity': 0.2,
            'wireframe': True
        }
        
    def create_eb(self) -> List:
        """
        Create electromagnetic barrel (EB) geometry.
        
        Returns:
        --------
        list
            List containing EB 3D object
        """
        config = self.eb_config
        
        geometry = CylinderGeometry(
            radiusTop=config['radius_top'],
            radiusBottom=config['radius_bottom'],
            height=config['height'],
            radialSegments=64,
            heightSegments=1,
            openEnded=True,
            thetaStart=0,
            thetaLength=2 * math.pi
        )
        
        material = MeshBasicMaterial(
            color=config['color'],
            wireframe=config['wireframe'],
            transparent=True,
            opacity=config['opacity']
        )
        
        eb = Mesh(geometry=geometry, material=material)
        eb.rotateX(math.pi / 2)
        eb.name = 'EB'
        
        return [eb]
        
    def create_hcal_barrel(self) -> List:
        """
        Create hadron calorimeter barrel geometry.
        
        Returns:
        --------
        list
            List containing HCAL barrel 3D object
        """
        geometry = CylinderGeometry(
            radiusTop=1.8,
            radiusBottom=2.95,
            height=7.0,
            radialSegments=64,
            heightSegments=1,
            openEnded=True
        )
        
        material = MeshBasicMaterial(
            color='#ff9999',
            wireframe=True,
            transparent=True,
            opacity=0.15
        )
        
        hcal = Mesh(geometry=geometry, material=material)
        hcal.rotateX(math.pi / 2)
        hcal.name = 'HCAL_Barrel'
        
        return [hcal]
        
    def create_tracker(self) -> List:
        """
        Create simplified tracker geometry.
        
        Returns:
        --------
        list
            List containing tracker 3D objects
        """
        tracker_objects = []
        
        # Pixel detector layers
        for radius in [0.04, 0.07, 0.11]:
            geometry = CylinderGeometry(
                radiusTop=radius,
                radiusBottom=radius,
                height=0.5,
                radialSegments=32,
                heightSegments=1,
                openEnded=True
            )
            
            material = MeshBasicMaterial(
                color='#999999',
                wireframe=True,
                transparent=True,
                opacity=0.3
            )
            
            layer = Mesh(geometry=geometry, material=material)
            layer.rotateX(math.pi / 2)
            layer.name = f'Pixel_Layer_{radius}'
            tracker_objects.append(layer)
            
        return tracker_objects
        
    def create_muon_system(self) -> List:
        """
        Create muon detection system geometry.
        
        Returns:
        --------
        list
            List containing muon system 3D objects
        """
        geometry = CylinderGeometry(
            radiusTop=4.0,
            radiusBottom=4.2,
            height=12.0,
            radialSegments=64,
            heightSegments=1,
            openEnded=True
        )
        
        material = MeshBasicMaterial(
            color='#cc99ff',
            wireframe=True,
            transparent=True,
            opacity=0.1
        )
        
        muon_system = Mesh(geometry=geometry, material=material)
        muon_system.rotateX(math.pi / 2)
        muon_system.name = 'Muon_System'
        
        return [muon_system]
        
    def create_coordinate_axes(self, length: float = 2.0) -> List:
        """
        Create coordinate system axes.
        
        Parameters:
        -----------
        length : float
            Length of the axes
            
        Returns:
        --------
        list
            List containing coordinate axes
        """
        axes = []
        
        # X-axis (red)
        x_axis = ArrowHelper(
            dir=[1, 0, 0],
            origin=[0, 0, 0],
            length=length,
            color='#ff0000',
            headLength=0.2,
            headWidth=0.1
        )
        x_axis.name = 'X_Axis'
        axes.append(x_axis)
        
        # Y-axis (green)
        y_axis = ArrowHelper(
            dir=[0, 1, 0],
            origin=[0, 0, 0],
            length=length,
            color='#00ff00',
            headLength=0.2,
            headWidth=0.1
        )
        y_axis.name = 'Y_Axis'
        axes.append(y_axis)
        
        # Z-axis (blue)
        z_axis = ArrowHelper(
            dir=[0, 0, 1],
            origin=[0, 0, 0],
            length=length,
            color='#0000ff',
            headLength=0.2,
            headWidth=0.1
        )
        z_axis.name = 'Z_Axis'
        axes.append(z_axis)
        
        return axes
        
    def configure_eb(self, **kwargs):
        """
        Configure electromagnetic barrel parameters.
        
        Parameters:
        -----------
        **kwargs : dict
            Configuration parameters to update
        """
        self.eb_config.update(kwargs)
        
    def create_full_detector(self,
                             include_tracker: bool = False,
                             include_hcal: bool = False,
                             include_muon: bool = False,
                             include_axes: bool = False) -> List:
        """
        Create complete detector geometry.
        
        Parameters:
        -----------
        include_tracker : bool
            Whether to include tracker geometry
        include_hcal : bool
            Whether to include HCAL geometry
        include_muon : bool
            Whether to include muon system geometry
        include_axes : bool
            Whether to include coordinate axes
            
        Returns:
        --------
        list
            List of all detector components
        """
        detector_objects = []
        
        # Always include EB (for now)
        detector_objects.extend(self.create_eb())
        
        if include_tracker:
            detector_objects.extend(self.create_tracker())
            
        if include_hcal:
            detector_objects.extend(self.create_hcal_barrel())
            
        if include_muon:
            detector_objects.extend(self.create_muon_system())
            
        if include_axes:
            detector_objects.extend(self.create_coordinate_axes())
            
        return detector_objects


