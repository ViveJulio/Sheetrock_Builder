from flask_app.config.mysqlconnection import connectToMySQL


db = "sheetrock_builder_schema"

class Build():

    def __init__(self, data):
        #lw12p = picks, lw12r = remainder
        self.id = data['id']
        self.order_id = data['order_id']
        self.lw5412p = data['lw5412p']
        self.lw5412r = data['lw5412r']
        self.fc5412p = data['fc5412p']
        self.fc5412r = data['fc5412r']
        self.lw12p = data['lw12p']
        self.lw12r = data['lw12r']
        self.fc12p = data['fc12p']
        self.fc12r = data['fc12r']
        self.m1212p = data['m1212p']
        self.m1212r = data['m1212r']
        self.m5812p = data['m5812p']
        self.m5812r = data['m5812r']

        self.remainder_pick = None

    @classmethod
    def build_truck(cls, data):
        # sheets will be added 1 by 1 to fill mixed picks
        # the absolute minimum thickness to add a final sheet is indacated below for 5/8" and 1/2"
        mint58 = 16.376
        mint12 = 16.52
        # lw5412[0] = pick, lw5412[1] = remainder
        lw5412_pick_remainder = list(divmod(data['lw5412'], 34))
        fc5412_pick_remainder = list(divmod(data['fc5412'], 26))
        if fc5412_pick_remainder[1] == 1 and fc5412_pick_remainder[0] == 1:
            fc5412_pick_remainder = list(divmod(data['fc5412'], 27))

        fc12_pick_remainder = list(divmod(data['fc12'], 26))
        if fc12_pick_remainder[1] == 1 and fc12_pick_remainder[0] == 1:
            fc12_pick_remainder = list(divmod(data['fc12'], 27))

        mm1212_pick_remainder = list(divmod(data['m1212'], 34))
        mm5812_pick_remainder = list(divmod(data['m5812'], 26))
        if mm5812_pick_remainder[1] == 1 and mm5812_pick_remainder[0] == 1:
            mm5812_pick_remainder = list(divmod(data['m5812'], 27))

        picks = []
        temp_pick = {}

        #add all remaining sheets to 1 dict to cycle through
        sheet_types_remainder = {'lw5412' : lw5412_pick_remainder[1], 'fc5412' : fc5412_pick_remainder[1],
                                'lw12' : data['lw12'], 'fc12' : fc12_pick_remainder[1], 'mm1212' : mm1212_pick_remainder[1], 'mm5812' : mm5812_pick_remainder[1]}

        #use a ticker to indicate there are more than 2 sheet types greater than 0
        ticker = 0
        for val in sheet_types_remainder.values():
            if val > 0:
                ticker += 1

        #if lw12 and only 1 other type is to be organized, create full picks of lw12
        if ticker <= 2 and data['lw12'] > 0:
            lw12_pick_remainder = list(divmod(data['lw12'], 34))
            sheet_types_remainder['lw12'] = lw12_pick_remainder[1]
        else:
            lw12_pick_remainder = None

        #cycle through remaining sheets starting with 1/2" x 54"
        for key, val in sheet_types_remainder.items():
            print('cycle through', key)
            # skip lw12 as it is our filler
            if key == 'lw12':
                continue
            #temp sheet will prevent doubling sheets
            temp_sheet = key
            if val > 0:
                temp_pick[key] = val
                if key[:2] == 'fc' or key[2:4] == '58':
                    current_thick = val * .625
                else:
                    current_thick = val * .5
                for key, val in sheet_types_remainder.items():
                    if len(temp_pick) == 0:
                        continue
                    if key != temp_sheet:
                        if val > 0:
                            temp_pick[key] = 0
                            print('fill with',key, 'current_thick', current_thick)
                            if key[:2] == 'lw' or key[:4] == 'mm12':
                                while val > 0 and current_thick < mint12:
                                    current_thick += .5
                                    val -= 1
                                    sheet_types_remainder[key] -= 1
                                    temp_pick[key] += 1
                                if current_thick > mint12:
                                    picks.append(temp_pick)
                                    temp_pick = {}
                            else:
                                while val > 0 and current_thick < mint58:
                                    current_thick += .625
                                    val -= 1
                                    sheet_types_remainder[key] -= 1
                                    temp_pick[key] += 1
                                if current_thick > mint58:
                                    picks.append(temp_pick)
                                    temp_pick = {}
            if len(temp_pick) == 0:
                sheet_types_remainder[temp_sheet] = 0

        if len(temp_pick) > 0:
            picks.append(temp_pick)
            temp_pick = {}

        lw12_pick_remainder = list(divmod(sheet_types_remainder['lw12'], 34))
        if lw12_pick_remainder[1] > 0:
            picks.append({'lw12' : lw12_pick_remainder[1]})


        #checks to see if this is an update to an existing order
        if 'update' in data:
            build_data = {
                'lw5412p' : lw5412_pick_remainder[0],
                'lw5412r' : lw5412_pick_remainder[1],
                'fc5412p' : fc5412_pick_remainder[0],
                'fc5412r' : fc5412_pick_remainder[1],
                'lw12p' : lw12_pick_remainder[0],
                'lw12r' : lw12_pick_remainder[1],
                'fc12p' : fc12_pick_remainder[0],
                'fc12r' : fc12_pick_remainder[1],
                'm1212p' : mm1212_pick_remainder[0],
                'm1212r' : mm1212_pick_remainder[1],
                'm5812p' : mm5812_pick_remainder[0],
                'm5812r' : mm5812_pick_remainder[1]
            }
            return build_data

        #this series of actions will perform for new orders with no id yet to prevent duplicate code and duplicate orders
        if 'id' not in data:
            build_data = {
                'order_id' : data['order_id'],
                'lw5412p' : lw5412_pick_remainder[0],
                'lw5412r' : lw5412_pick_remainder[1],
                'fc5412p' : fc5412_pick_remainder[0],
                'fc5412r' : fc5412_pick_remainder[1],
                'lw12p' : lw12_pick_remainder[0],
                'lw12r' : lw12_pick_remainder[1],
                'fc12p' : fc12_pick_remainder[0],
                'fc12r' : fc12_pick_remainder[1],
                'm1212p' : mm1212_pick_remainder[0],
                'm1212r' : mm1212_pick_remainder[1],
                'm5812p' : mm5812_pick_remainder[0],
                'm5812r' : mm5812_pick_remainder[1]
            }

            query = """
                    INSERT INTO builds (order_id, lw5412p, lw5412r, fc5412p, fc5412r, lw12p, lw12r, fc12p, fc12r, m1212p, m1212r, m5812p, m5812r)
                    VALUES (%(order_id)s, %(lw5412p)s, %(lw5412r)s, %(fc5412p)s, %(fc5412r)s, %(lw12p)s, %(lw12r)s, %(fc12p)s, %(fc12r)s, %(m1212p)s, %(m1212r)s, %(m5812p)s, %(m5812r)s)
                    """

            results = connectToMySQL(db).query_db(query, build_data)
            build = Build.get_build_by_id({'id' : results})
            build.remainder_pick = picks
            return build
        # if the id already exists, it means we are trying to get the remainder picks
        if len(picks) > 0:
            remainder_pick_prints = []
            for pick in picks:
                total_sheets = 0
                keys = []
                vals = []
                for key, val in pick.items():
                    total_sheets += val
                    keys.append(key)
                    vals.append(val)
                if len(keys) == 1:
                    remainder_pick_prints.append(f'remainder pick: {total_sheets} sheets ({keys[0]} {vals[0]})')
                if len(keys) == 2:
                    remainder_pick_prints.append(f'remainder pick: {total_sheets} sheets ({keys[0]} {vals[0]}, {keys[1]} {vals[1]})')
                if len(keys) == 3:
                    remainder_pick_prints.append(f'remainder pick: {total_sheets} sheets ({keys[0]} {vals[0]}, {keys[1]} {vals[1]}, {keys[2]} {vals[2]})')
                if len(keys) == 4:
                    remainder_pick_prints.append(f'remainder pick: {total_sheets} sheets ({keys[0]} {vals[0]}, {keys[1]} {vals[1]}, {keys[2]} {vals[2]}, {keys[3]} {vals[3]})')
                if len(keys) == 5:
                    remainder_pick_prints.append(f'remainder pick: {total_sheets} sheets ({keys[0]} {vals[0]}, {keys[1]} {vals[1]}, {keys[2]} {vals[2]}, {keys[3]} {vals[3]}, {keys[4]} {vals[4]})')

            return remainder_pick_prints
        picks = None
        return picks


    @classmethod
    def get_build_by_id(cls, build_id):
        query = """
                SELECT * FROM builds
                WHERE builds.id = %(id)s
                """
        results = connectToMySQL(db).query_db(query, build_id)
        print('-------',results)
        return cls(results[0])

    @classmethod
    def update_build(cls,data,order_id):
        data['update'] = True
        build_data = Build.build_truck(data)
        query = f"""
                UPDATE builds
                SET lw5412p = %(lw5412p)s, lw5412r = %(lw5412r)s, lw12p = %(lw12p)s, lw12r = %(lw12r)s, fc12p = %(fc12p)s, fc12r = %(fc12r)s, fc5412p = %(fc5412p)s, fc5412r = %(fc5412r)s, m1212p = %(m1212p)s, m1212r = %(m1212r)s, m5812p = %(m5812p)s, m5812r = %(m5812r)s
                WHERE id = {order_id};
                """
        results = connectToMySQL(db).query_db(query, build_data)
        return results
