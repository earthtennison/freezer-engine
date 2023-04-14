from csv_database import csv_database

# for datetime type
from datetime import datetime

class Conversation():
    def __init__(self, db_path):

        # current message user input
        self.current_msg = ""

        # conver_type are add_item, update_item, list_item
        self.conver_type = ""

        self.conver_index = 0

        self.item = {'name':None, 'expiry_date':None, 'store_place':None, 'quantity':None, 'category':None}

        self.db = csv_database(db_path)



    def get_conver_type(self, msg: str):

        if msg.lower() in ['add item', 'เพิ่มของ', 'เพิ่ม', 'add']:
            self.conver_type  = 'add_item'
        elif msg.lower() in ['update item']:
            self.conver_type = 'update_item'
        elif msg.lower() in ['list item']:
            self.conver_type = 'list_item'
        else:
            # send dafault message
            self.conver_type = 'default'

    def push_msg(self, current_msg):
        self.current_msg = current_msg
        # print("Bot:",self.current_msg)

        # check if is initial message of the conversation
        if self.conver_index == 0:
            self.get_conver_type(self.current_msg)



    def response(self):

        # rule base for response
        if self.conver_type == 'default':
            self.conver_index = 0
            self.conver_type = ''
            return "Hello, I am Freezer. Please tell me what to do:\n" + \
                "1. add item\n" + \
                "2. update item\n" + \
                "3. list item"
        elif self.conver_type == 'add_item':
            # switch case
            if self.conver_index == 0:
                self.conver_index += 1
                return "What's the name of item?"
            elif self.conver_index == 1:
                self.item['name'] = self.current_msg
                self.conver_index += 1
                return "What's the date of expiration?"
            elif self.conver_index == 2:
                date_str = self.current_msg
                try:
                    if date_str.count('.') == 2:
                        date_obj = datetime.strptime(date_str, '%d.%m.%Y')
                    else:
                        date_obj = datetime.strptime(date_str, '%d.%m')
                        date_str += '.2023'
                except ValueError:
                    print("Incorrect date format dd.mm.yyyy or dd.mm")
                    return "Tell me the date again in format dd.mm.yyyy or dd.mm"
                self.item['expiry_date'] = date_str # todo set to default data format
                self.conver_index += 1
                return "How many piece of {}?".format(self.item['name'])
            elif self.conver_index == 3:
                self.item['quantity'] = int(self.current_msg)
                self.conver_index += 1
                return "Where will you store the item? fridge home, fridge back home, fridge condo, cabinet" # todo show flex icon
            elif self.conver_index == 4:
                self.item['store_place'] = self.current_msg

                # push item to database
                self.db.push(self.item)

                self.conver_index = 0
                self.conver_type = ''

                return "Roger that!"
            # todo add picture
                
        elif self.conver_type == 'update_item':
            if self.conver_index == 0:
                self.conver_index += 1
                return "What's the name of item you want to update?"
            elif self.conver_index == 1:
                self.item['name'] = self.current_msg
                self.conver_index += 1
                return "What's the new quantity?"
            elif self.conver_index == 2:
                self.item['quantity'] = int(self.current_msg)
                if self.item['quantity'] == 0:
                    # delete item
                    self.db.df = self.db.df.loc[self.db.df['name'] != self.item['name']]
                    self.db.save_csv()
                    return "I delete {}".format(self.item['name'])
                else:
                    # update item
                    self.db.df.loc[self.db.df['name'] == self.item['name'],'quantity'] = self.item['quantity']
                    self.db.save_csv()
                    return "{} updated".format(self.item['name'])


        elif self.conver_type == 'list_item':
            msg = "Here's all items:\n"
            for idx, row in self.db.df.iterrows():
                msg += '- ' + row['name'] + '\n'
            
            self.conver_index = 0
            self.conver_type = ""
            
            return msg




if __name__ == '__main__':

    con = Conversation("./database/data1.csv")

    while True:
        # Get user input
        user_input = input("You: ")
        con.push_msg(user_input)
        print(con.response())
