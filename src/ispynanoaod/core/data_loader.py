"""
Data loading utilities
"""
import os
import uproot
import awkward as ak
from typing import List, Optional, Union

class DataLoader:
    """
    Handles loading and preprocessing of objects.
    """
    
    DEFAULT_BRANCHES = [
        'run', 'event', 'luminosityBlock',
        'nJet', 'Jet_pt', 'Jet_eta', 'Jet_phi',
        'MET_pt', 'MET_phi',
        'nPhoton', 'Photon_pt', 'Photon_eta', 'Photon_phi',
        'nMuon', 'Muon_pt', 'Muon_eta', 'Muon_phi', 'Muon_charge',
        'nElectron', 'Electron_pt', 'Electron_eta', 'Electron_phi', 'Electron_charge',
        'nSV', 'SV_x', 'SV_y', 'SV_z',
        'PV_x', 'PV_y', 'PV_z',
        'nFatJet', 'FatJet_pt', 'FatJet_eta', 'FatJet_phi',
        'nIsoTrack', 'IsoTrack_pt', 'IsoTrack_eta', 'IsoTrack_phi', 'IsoTrack_charge',
    ]
    
    def __init__(self):
        """Initialize the data loader."""
        pass
        
    def load_root_file(self,
                       filename: str,
                       branches: Optional[List[str]] = None,
                       tree_name: str = 'Events',
                       max_events: Optional[int] = None) -> ak.Array:
        """
        Load events from a ROOT file.
        
        Parameters:
        -----------
        filename : str
            Path to the ROOT file
        branches : list, optional
            List of branches to load. If None, loads default branches.
        tree_name : str
            Name of the tree in the ROOT file
        max_events : int, optional
            Maximum number of events to load
            
        Returns:
        --------
        awkward.Array
            Loaded event data
        """
        if not os.path.exists(filename):
            raise FileNotFoundError(f"File not found: {filename}")
            
        if branches is None:
            branches = self.DEFAULT_BRANCHES
            
        try:
            with uproot.open(filename) as file:
                tree = file[tree_name]
                
                # Check which branches actually exist
                available_branches = tree.keys()
                valid_branches = [b for b in branches if b in available_branches]
                
                if not valid_branches:
                    raise ValueError("No valid branches found in file")
                    
                # Load the data
                events = tree.arrays(
                    valid_branches,
                    library='ak',
                    entry_stop=max_events
                )
                
                return events
                
        except Exception as e:
            raise RuntimeError(f"Error loading ROOT file: {str(e)}")
