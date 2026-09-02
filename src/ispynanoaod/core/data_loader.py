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
    
    # Branches always expected, regardless of nanoAOD flavor.
    EVENT_BRANCHES = [
        'run', 'event', 'luminosityBlock',
        'MET_pt', 'MET_phi',
        'PV_x', 'PV_y', 'PV_z',
    ]

    # Per-object collections that may or may not be present depending on the
    # nanoAOD flavor/version (e.g. plain NanoAOD has no PFCands; some private
    # productions omit FatJet, IsoTrack, or SV). Each entry is resolved
    # against the branches actually found in a file rather than assumed
    # present, so a new collection only needs an entry here plus a factory
    # method - see EventDisplay._render_event().
    COLLECTIONS = {
        'jet': {'count': 'nJet', 'branches': ['Jet_pt', 'Jet_eta', 'Jet_phi']},
        'photon': {'count': 'nPhoton', 'branches': ['Photon_pt', 'Photon_eta', 'Photon_phi']},
        'muon': {'count': 'nMuon', 'branches': ['Muon_pt', 'Muon_eta', 'Muon_phi', 'Muon_charge']},
        'electron': {'count': 'nElectron', 'branches': ['Electron_pt', 'Electron_eta', 'Electron_phi', 'Electron_charge']},
        'sv': {'count': 'nSV', 'branches': ['SV_x', 'SV_y', 'SV_z']},
        'fatjet': {'count': 'nFatJet', 'branches': ['FatJet_pt', 'FatJet_eta', 'FatJet_phi']},
        'isotrack': {'count': 'nIsoTrack', 'branches': ['IsoTrack_pt', 'IsoTrack_eta', 'IsoTrack_phi', 'IsoTrack_charge']},
        'pfcand': {'count': 'nPFCands', 'branches': ['PFCands_pt', 'PFCands_eta', 'PFCands_phi', 'PFCands_charge', 'PFCands_pdgId']},
    }

    DEFAULT_BRANCHES = EVENT_BRANCHES + [
        branch
        for spec in COLLECTIONS.values()
        for branch in [spec['count']] + spec['branches']
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

    def available_collections(self, events: ak.Array) -> set:
        """
        Determine which optional collections (see COLLECTIONS) have all of
        their branches present in already-loaded event data.

        Parameters:
        -----------
        events : awkward.Array
            Event data as returned by load_root_file()

        Returns:
        --------
        set
            Names of available collections, e.g. {'jet', 'muon', 'pfcand'}
        """
        fields = set(events.fields)
        return {
            name for name, spec in self.COLLECTIONS.items()
            if spec['count'] in fields and all(b in fields for b in spec['branches'])
        }
