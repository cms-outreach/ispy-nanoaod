"""
Factory for creating 3D objects
"""

import math
import numpy as np
from pythreejs import *
from typing import List, Union
import random

class ObjectFactory:
    """
    Factory class for creating 3D objects of physics things
    """
    
    def __init__(self):
        self.styles = {
            'jet': {
                'color': '#ffff00',
                'opacity': 0.5,
                'radius_top': 0.3,
                'radius_bottom': 0.0,
                'length': 1.1
            },
            'muon': {
                'color': '#ff0000',
                'scale': 0.1,
                'head_length': 0.2,
                'head_width': 0.1
            },
            'electron': {
                'color': '#19ff19',
                'scale': 0.1,
                'head_length': 0.2,
                'head_width': 0.1
            },
            'met': {
                'color': '#ff00ff',
                'scale': 0.1,
                'head_length': 0.2,
                'head_width': 0.2,
                'distance': 1.24
            },
            'primary_vertex': {
                'color': '#ffff00',
                'radius': 0.01
            },
            'secondary_vertex': {
                'color': '#ff6600',
                'radius': 0.01
            }
        }
        
    def create_jets(self, pt_array, eta_array, phi_array) -> List:
        """
        Create 3D jet objects.
        
        Parameters:
        -----------
        pt_array : array-like
            Transverse momentum values
        eta_array : array-like
            Pseudorapidity values
        phi_array : array-like
            Azimuthal angle values
            
        Returns:
        --------
        list
            List of jet 3D objects
        """
        jets = []
        style = self.styles['jet']
        
        for pt, eta, phi in zip(pt_array, eta_array, phi_array):
            jet = self._create_jet(float(pt), float(eta), float(phi), style)
            jets.append(jet)
            
        return jets
        
    def _create_jet(self, pt, eta, phi, style):
        """Create a single jet object."""
        theta = 2 * math.atan(pow(math.e, -eta))
        
        # Direction vector
        dir_vec = np.array([
            math.cos(phi),
            math.sin(phi),
            math.sinh(eta)
        ])
        dir_vec /= np.linalg.norm(dir_vec)
        
        # Create cone geometry
        geometry = CylinderGeometry(
            radiusTop=style['radius_top'],
            radiusBottom=style['radius_bottom'],
            height=style['length'],
            radialSegments=32,
            heightSegments=1,
            openEnded=True
        )
        
        # Create material
        material = MeshBasicMaterial(
            color=style['color'],
            side='DoubleSide',
            transparent=True,
            opacity=style['opacity']
        )
        
        # Create mesh
        jet = Mesh(geometry=geometry, material=material)
        
        # Position and orient the jet
        length = style['length'] * 0.5
        jet.rotateZ(phi - math.pi/2)
        jet.rotateX(math.pi/2 - theta)
        jet.position = (dir_vec * length).tolist()
        
        # Add metadata
        jet.name = 'Jet'
        jet.props = {'pt': pt, 'eta': eta, 'phi': phi}
        
        return jet
        
    def create_muons(self, pt_array, eta_array, phi_array, charge_array) -> List:
        """Create 3D muon objects."""
        muons = []
        style = self.styles['muon']

        for pt, eta, phi, charge in zip(pt_array, eta_array, phi_array, charge_array):
            muon = self._create_lepton(
                float(pt), float(eta), float(phi), int(charge), 'Muon', style
            )
            muons.append(muon)
    
        return muons
        
    def create_electrons(self, pt_array, eta_array, phi_array, charge_array) -> List:
        """Create 3D electron objects."""
        electrons = []
        style = self.styles['electron']

        for pt, eta, phi, charge in zip(pt_array, eta_array, phi_array, charge_array):
            electron = self._create_lepton(
                float(pt), float(eta), float(phi), int(charge), 'Electron', style
            )
            electrons.append(electron)

        return electrons
        
    def _create_lepton(self, pt, eta, phi, charge, name, style):
        """Create a lepton (muon or electron) track"""

        # Assume for now that the track starts from (0,0,0)
        vertex = (0,0,0)

        # Check the direction of the B-field
        Bz = 3.8
        radius = pt / (np.fabs(charge)*Bz)
        
        centerX = vertex[0] + radius*charge*np.sin(phi)
        centerY = vertex[1] - radius*charge*np.cos(phi)
        pz = pt*np.sinh(eta)
        phi0 = np.arctan2(vertex[1] - centerY, vertex[0] - centerX)
        omega = (charge*Bz) / pt
        pitch = pz / (pt*np.fabs(omega))

        maxAngle = 4*np.pi
        numPoints = 1000
        points = []

        for i in range(0, numPoints+1):

            t = (i/numPoints)*maxAngle
            x = centerX + radius*np.cos(phi0+t)
            y = centerY + radius*np.sin(phi0+t)
            z = vertex[2] + t*pitch
            r = np.sqrt(x*x +y*y)

            # We don't have an endpoint for the tracks.
            # For now propagate to the extent of the "EB".
            # Also, we need to get these numbers from somewhere,
            # not hard-coded.
            if np.fabs(z) > 3 or r > 1.21:
                break
            
            points.append((x,y,z))
            
        points = np.array(points)
        
        geometry = BufferGeometry(
            attributes={
                'position': BufferAttribute(points, normalized=False)
            }
        )
        
        material = LineBasicMaterial(color=style['color'])
        track = Line(geometry=geometry, material=material)

        track.name = name
        track.props = {'pt': pt, 'eta': eta, 'phi': phi, 'charge': charge}
        return track
                
    def create_met(self, pt, phi):
        """Create missing energy object."""
        style = self.styles['met']
        
        px = math.cos(float(phi))
        py = math.sin(float(phi))
        
        dir_vec = np.array([px, py, 0])
        dir_vec /= np.linalg.norm(dir_vec)
        
        d = style['distance']
        length = float(pt) * style['scale']
        length = min(length, 5.0)  # Cap the length
        
        # Create line for the shaft
        line_geometry = LineSegmentsGeometry(
            positions=[[(dir_vec * d).tolist(), (dir_vec * (length + d - 0.2)).tolist()]]
        )
        line_material = LineMaterial(linewidth=3, color=style['color'])
        line = LineSegments2(line_geometry, line_material)
        
        # Create cone for the head
        cone_geometry = CylinderGeometry(
            radiusTop=0.0,
            radiusBottom=0.1,
            height=0.2,
            radialSegments=32,
            heightSegments=1,
            openEnded=True
        )
        
        cone = Mesh(cone_geometry, MeshBasicMaterial(color=style['color']))
        cone.rotateZ(float(phi) - math.pi/2)
        cone.position = (dir_vec * (length + d - 0.2)).tolist()
        
        # Add metadata to cone (for picking)
        cone.name = 'MET'
        cone.props = {'pt': float(pt), 'phi': float(phi)}
        
        # Group line and cone
        met = Object3D(children=(line, cone))
        
        return met
        
    def create_primary_vertex(self, x, y, z):
        """Create primary vertex object."""
        style = self.styles['primary_vertex']
        
        geometry = SphereGeometry(
            radius=style['radius'],
            widthSegments=32,
            heightSegments=32
        )
        
        vertex = Mesh(
            geometry,
            MeshBasicMaterial(color=style['color'])
        )
        
        vertex.name = 'PV'
        vertex.position = [0.01*float(x), 0.01*float(y), 0.01*float(z)]
        
        return vertex
        
    def create_secondary_vertices(self, x_array, y_array, z_array) -> List:
        """Create secondary vertex objects."""
        vertices = []
        style = self.styles['secondary_vertex']
        
        for x, y, z in zip(x_array, y_array, z_array):
            geometry = SphereGeometry(
                radius=style['radius'],
                widthSegments=32,
                heightSegments=32
            )
            
            vertex = Mesh(
                geometry,
                MeshBasicMaterial(color=style['color'])
            )
            
            vertex.name = 'SV'
            vertex.position = [0.01*float(x), 0.01*float(y), 0.01*float(z)]
            vertices.append(vertex)
            
        return vertices
        
    def set_style(self, particle_type: str, **kwargs):
        """
        Update styling for a particle type.
        
        Parameters:
        -----------
        particle_type : str
            Type of particle ('jet', 'muon', 'electron', etc.)
        **kwargs : dict
            Style parameters to update
        """
        if particle_type in self.styles:
            self.styles[particle_type].update(kwargs)
        else:
            self.styles[particle_type] = kwargs
