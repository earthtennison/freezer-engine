import pandas as pd
import os

class csv_database:
    def __init__(self, file_path):
        if os.path.exists(file_path):
            self.file_path = file_path
            self.load_csv()
        else:
            # create new database
            self.file_path = file_path
            self.df = pd.DataFrame(columns=['name', 'expiry_date', 'store_place', 'quantity', 'category'])
    
    def get_item(self, item_name):
        return self.df.loc[self.df['name']==item_name]
    
    def push(self, item):
        item_se = pd.Series(item)
        self.df = pd.concat([self.df, item_se.to_frame().T], ignore_index=True)
        self.df.to_csv(self.file_path, index=False)

    def save_csv(self):
        self.df.to_csv(self.file_path, index=False)
        print("Saved to {}".format(self.file_path))
        print(self.df)

    def load_csv(self):
        self.df = pd.read_csv(self.file_path)
        # print("Loaded {}:".format(self.file_path))
        # print(self.df)


if __name__ == '__main__':
    pass