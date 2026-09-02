import ipywidgets as widgets
from IPython.display import display

from .data_loader import DataLoader
from ..objects.objects import ObjectFactory
from ..objects.detector import DetectorGeometry
from ..display.renderer import EventRenderer
from ..display.controls import EventControls

class EventDisplay:
    """
    Main class for displaying particle physics events in 3D.
    
    This class handles data loading, 3D object creation, and
    interactive visualization in Jupyter notebooks.
    """
    
    def __init__(self, width=800, height=500, background='#232323'):
        """
        Initialize the event display.
        
        Parameters:
        -----------
        width : int
            Display width in pixels
        height : int
            Display height in pixels
        background : str
            Background color (hex string)
        """
        self.width = width
        self.height = height
        self.background = background
        
        # Core components
        self.data_loader = DataLoader()
        self.object_factory = ObjectFactory()
        self.detector_geometry = DetectorGeometry()
        self.renderer = EventRenderer(width, height, background)
        self.controls = EventControls()
        
        # State
        self.events_data = None
        self.current_event_index = 0
        self.max_events = 0
        # Which optional collections (see DataLoader.COLLECTIONS) are present
        # in the currently loaded file - resolved once on load, not per event.
        self.available_collections = set()

        # Detector geometry is static, so it's built once and reused across
        # every event instead of being recreated on each render. The build
        # is deferred to the first render (see _ensure_detector_geometry())
        # rather than done here, so that callers configuring it in between
        # (e.g. display.detector_geometry.configure_eb(...)) still take effect.
        self._detector_built = False

        # UI components
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the user interface widgets."""
        self.info_widget = widgets.HTML()
        self.pick_info_widget = widgets.HTML(value='Object info: ')
        
        # Setup controls
        self.controls.setup_navigation(
            self._on_previous_event,
            self._on_next_event
        )
        
        # Setup object picking
        self.renderer.setup_picking(self._on_object_hover)
        
    def load_file(self, filename, branches=None):
        """
        Load events from a ROOT file.
        
        Parameters:
        -----------
        filename : str
            Path to ROOT file
        branches : list, optional
            Specific branches to load
        """
        self.events_data = self.data_loader.load_root_file(filename, branches)
        self.available_collections = self.data_loader.available_collections(self.events_data)
        self.max_events = len(self.events_data) - 1
        self.current_event_index = 0

    def load_data(self, events_data):
        """
        Load events from pre-processed data.
        
        Parameters:
        -----------
        events_data : awkward.Array
            Event data array
        """
        self.events_data = events_data
        self.available_collections = self.data_loader.available_collections(self.events_data)
        self.max_events = len(events_data) - 1
        self.current_event_index = 0
        
    def show_event(self, event_index=None):
        """
        Display a specific event.
        
        Parameters:
        -----------
        event_index : int, optional
            Index of event to show. If None, shows current event.
        """
        if event_index is not None:
            self.current_event_index = min(max(0, event_index), self.max_events)
            
        if self.events_data is None:
            raise ValueError("No event data loaded. Use load_file() or load_data() first.")
            
        event = self.events_data[self.current_event_index]
        self._render_event(event)
        
    def _ensure_detector_geometry(self):
        """Build the (static) detector geometry once, on first use."""
        if self._detector_built:
            return

        # NOTE: These geometries are just placeholders and not realistic
        detector_objects = self.detector_geometry.create_full_detector(
            include_tracker=False,
            include_hcal=False,
            include_muon=False,
            include_axes=False
        )
        self.renderer.add_detector_objects(detector_objects)
        self._detector_built = True

    def _render_event(self, event):
        """Render a single event to the 3D scene."""
        self._ensure_detector_geometry()

        # Clear previous event's objects (detector geometry is static and persists)
        self.renderer.clear_event_objects()

        # Update event info
        self._update_event_info(event)

        # Add 3D objects
        objects = []
        
        # Jets
        if 'jet' in self.available_collections and event['nJet'] > 0:
            jets = self.object_factory.create_jets(
                event['Jet_pt'], event['Jet_eta'], event['Jet_phi']
            )
            objects.extend(jets)

        # FatJets (ak8)
        if 'fatjet' in self.available_collections and event['nFatJet'] > 0:
            fjets = self.object_factory.create_fjets(
                event['FatJet_pt'], event['FatJet_eta'], event['FatJet_phi']
            )
            objects.extend(fjets)

        # Muons
        if 'muon' in self.available_collections and event['nMuon'] > 0:
            muons = self.object_factory.create_muons(
                event['Muon_pt'], event['Muon_eta'],
                event['Muon_phi'], event['Muon_charge']
            )
            objects.extend(muons)

        # Electrons
        if 'electron' in self.available_collections and event['nElectron'] > 0:
            electrons = self.object_factory.create_electrons(
                event['Electron_pt'], event['Electron_eta'],
                event['Electron_phi'], event['Electron_charge']
            )
            objects.extend(electrons)

        # IsoTracks
        if 'isotrack' in self.available_collections and event['nIsoTrack'] > 0:
            tracks = self.object_factory.create_tracks(
                event['IsoTrack_pt'], event['IsoTrack_eta'],
                event['IsoTrack_phi'], event['IsoTrack_charge']
            )
            objects.extend(tracks)

        # PFCands (PFNano only)
        if 'pfcand' in self.available_collections and event['nPFCands'] > 0:
            pfcands = self.object_factory.create_pfcands(
                event['PFCands_pt'], event['PFCands_eta'],
                event['PFCands_phi'], event['PFCands_charge'],
                event['PFCands_pdgId']
            )
            objects.extend(pfcands)

        # MET
        met = self.object_factory.create_met(
            event['MET_pt'], event['MET_phi']
        )
        objects.append(met)

        # Vertices
        if 'sv' in self.available_collections and event['nSV'] > 0:
            svs = self.object_factory.create_secondary_vertices(
                event['SV_x'], event['SV_y'], event['SV_z']
            )
            objects.extend(svs)

        pv = self.object_factory.create_primary_vertex(
            event['PV_x'], event['PV_y'], event['PV_z']
        )
        objects.append(pv)

        # Photons
        if 'photon' in self.available_collections and event['nPhoton'] > 0:
            photons = self.object_factory.create_photons(
                event['Photon_pt'], event['Photon_eta'],
                event['Photon_phi']
            )
            objects.extend(photons)
        
        # Add all objects to scene
        self.renderer.add_objects(objects)

    def _update_event_info(self, event):
        """Update the event information display."""
        info_text = (f"Run/Event/LS : "
                    f"{event['run']}/"
                    f"{event['event']}/"
                    f"{event['luminosityBlock']}")
        self.info_widget.value = info_text
    
    def _on_previous_event(self):
        """Handle previous event button click."""
        if self.current_event_index > 0:
            self.current_event_index -= 1
            self.show_event()
            
    def _on_next_event(self):
        """Handle next event button click."""
        if self.current_event_index < self.max_events:
            self.current_event_index += 1
            self.show_event()
            
    def _on_object_hover(self, obj, obj_info):
        """Handle object hover events."""

        # NOTE: Need to fix color behavior when picking
        
        if obj_info:
            self.pick_info_widget.value = f'Object info: {obj_info}'
        else:
            self.pick_info_widget.value = 'Object info: '
            
    def display(self):
        """Display the complete interface in the notebook."""
        # Create the main layout
        control_box = self.controls.create_widget()
        info_box = widgets.VBox([self.info_widget])
        pick_box = widgets.VBox([self.pick_info_widget])
        renderer_widget = self.renderer.get_widget()
        
        # Display everything
        display(control_box)
        display(info_box)
        display(pick_box)
        display(renderer_widget)
        
        # Show first event if data is loaded
        if self.events_data is not None:
            self.show_event(0)
