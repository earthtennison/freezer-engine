import pandas as pd
import os
import uuid

class csv_database:
    def __init__(self, file_path):
        if os.path.exists(file_path):
            self.file_path = file_path
            self.load_csv()
        else:
            # create new database
            self.file_path = file_path
            self.df = pd.DataFrame(columns=['item_id', 'name', 'expiry_date', 'store_place', 'quantity', 'category', 'exist', 'image_id','add_date'])
    
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
    
    def gen_id(self):
        # check if id is already in the database
        id = str(uuid.uuid4().fields[-1])[:5]
        while id in self.df['item_id'].tolist():
            id = str(uuid.uuid4().fields[-1])[:5]
        return id
    
    def get_id(self, **kwargs):
        columns = ['item_id', 'name', 'expiry_date', 'store_place', 'quantity', 'category', 'exist', 'image_id','add_date']
        indices = pd.Series([True]*len(self.df))
        for key, value in kwargs.items():
            if key in columns:
                indices = indices & (self.df[key] == value)
            else:
                print('[csv_database] keyword {} not in columns'.format(key))

        return self.df.loc[indices, 'item_id'].to_list()



if __name__ == '__main__':
    pass
    db = csv_database('database\data2.csv')
    print(db.get_id(name='pepsi'))