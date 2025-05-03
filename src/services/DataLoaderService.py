from .BaseService import BaseService
import pandas as pd

class DataLoaderService(BaseService):
    def __init__(self, csv_path: str):
        """
        Initialize the DataLoader with a CSV file path.
        
        Args:
            csv_path (str): Path to the CSV file containing diarization results.
        """
        super().__init__()
        self.csv_path = csv_path
        self.data = pd.read_csv(csv_path)
        self.logger.info(f"DataLoader initialized with CSV file: {csv_path}")
    
    def get_data(self) -> pd.DataFrame:
        """
        Load the data from the CSV file.
        
        Returns:
            pd.DataFrame: DataFrame containing the diarization results.
        """
        self.logger.info("Data loaded successfully.")
        return self.data