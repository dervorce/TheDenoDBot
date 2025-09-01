from UnitProfileCode import ProfileData

from typing import Dict, Any
import json
import os
import glob

class ProfileManager:
    def __init__(self, folder_path: str):
        self.folder_path = folder_path
        self.profiles: Dict[str, ProfileData] = {}

    def load_profiles(self):
        self.profiles.clear()
        json_files = glob.glob(os.path.join(self.folder_path, "*.json"))
        print(f"[DEBUG] Found JSON files: {json_files}")
        
        for filepath in json_files:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, dict):
                print(f"[WARN] Skipping {filepath}, not a dict: {data}")
                continue

            # Each JSON can have multiple profiles inside
            for name, profile_dict in data.items():
                print(f"[DEBUG] Found JSON entry: {name}")
                self.profiles[name] = ProfileData(profile_dict, name)

        # for name, profileData in self.profiles.items():
        #     if (profileData.base_min_speed == 1 and profileData.base_max_speed == 2):
        #         print(f"[DEBUG] Profile: {name}, MinSpeed: {profileData._current_min_speed}, MaxSpeed: {profileData._current_max_speed}")



    def get_profile(self, name: str) -> ProfileData:
        if name not in self.profiles:
            raise ValueError(f"Profile '{name}' not found in ProfileManager.")
        return self.profiles[name]

    def all_profiles(self) -> Dict[str, ProfileData]:
        return self.profiles
    
    def get_all_active_profiles(self) -> Dict[str, ProfileData]:
        return {k: v for k, v in self.profiles.items() if v.is_active}

    def save_profiles(self, output_path: str = None):
        if output_path is None:
            output_path = os.path.join(self.folder_path, "all_profiles.json")

        data = {name: profile.to_dict() for name, profile in self.profiles.items()}

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        print(f"[INFO] Profiles saved to {output_path}")