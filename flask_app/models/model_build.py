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

        self.remainder_pick = None

    @classmethod
    def build_truck(cls, data):
        # lw5412[0] = pick, lw5412[1] = remainder
        lw5412_pick_remainder = list(divmod(data['lw5412'], 34))
        fc5412_pick_remainder = list(divmod(data['fc5412'], 26))
        if fc5412_pick_remainder[1] == 1 and fc5412_pick_remainder[0] == 1:
            fc5412_pick_remainder = list(divmod(data['fc5412'], 27))

        lw12_pick_remainder = list(divmod(data['lw12'], 34))
        fc12_pick_remainder = list(divmod(data['fc12'], 26))
        if fc12_pick_remainder[1] == 1 and fc12_pick_remainder[0] == 1:
            fc12_pick_remainder = list(divmod(data['fc12'], 27))

        if 'update' in data:
            build_data = {
                'lw5412p' : lw5412_pick_remainder[0],
                'lw5412r' : lw5412_pick_remainder[1],
                'fc5412p' : fc5412_pick_remainder[0],
                'fc5412r' : fc5412_pick_remainder[1],
                'lw12p' : lw12_pick_remainder[0],
                'lw12r' : lw12_pick_remainder[1],
                'fc12p' : fc12_pick_remainder[0],
                'fc12r' : fc12_pick_remainder[1]
            }
            return build_data

        remainder_picks = []

        #rid of lw5412 remainder
        if lw5412_pick_remainder[1] > 0:
            mixed_pick = [{'lw54' : lw5412_pick_remainder[1]}]
            fc54_sheets = 0
            lw12_sheets = 0
            fc12_sheets = 0
            lw54pick_inches = float(lw5412_pick_remainder[1] * 0.5)

            while True:
                #combine fc5412
                while lw54pick_inches < 16.25 and fc5412_pick_remainder[1] > 0:
                    if fc5412_pick_remainder[1] != 1:
                        lw54pick_inches += 1.25
                        fc54_sheets += 2
                        fc5412_pick_remainder[1] -= 2
                    else:
                        lw54pick_inches += .625
                        fc54_sheets += 1
                        fc5412_pick_remainder[1] -= 1

                if lw54pick_inches> 17:
                    lw54pick_inches -= .625
                    fc54_sheets -= 1
                    fc5412_pick_remainder[1] += 1

                #combine lw12 (if needed)
                while lw54pick_inches < 16.25 and lw12_pick_remainder[1] > 0:
                    if lw12_pick_remainder[1] != 1:
                        lw54pick_inches += 1
                        lw12_sheets += 2
                        lw12_pick_remainder[1] -= 2
                    else:
                        lw54pick_inches += .5
                        lw12_sheets += 1
                        lw12_pick_remainder[1] -= 1

                if lw54pick_inches> 17:
                    lw54pick_inches -= .5
                    lw12_sheets -= 1
                    lw12_pick_remainder[1] += 1

                if lw12_pick_remainder[1] == 0 and fc5412_pick_remainder[1] == 0:
                    while lw54pick_inches < 16.25 and fc12_pick_remainder[1] > 0:
                        if fc12_pick_remainder[1] != 1:
                            lw54pick_inches += 1.25
                            fc12_sheets += 2
                            fc12_pick_remainder[1] -= 2
                        else:
                            lw54pick_inches += .625
                            fc12_sheets += 1
                            fc12_pick_remainder[1] -= 1

                    if lw54pick_inches> 17:
                        lw54pick_inches -= .625
                        fc12_sheets -= 1
                        fc12_pick_remainder[1] += 1
                #check that the pick was filled, if not, pull from lw12 pick and complete.
                if lw54pick_inches < 16.25 and lw12_pick_remainder[0] > 0:
                    lw12_pick_remainder[0] -= 1
                    lw12_pick_remainder[1] += 34
                else:
                    if lw12_sheets > 0:
                        mixed_pick.append({'lw12' : lw12_sheets})
                    if fc54_sheets > 0:
                        mixed_pick.append({'fc54' : fc54_sheets})
                    if fc12_sheets > 0:
                        mixed_pick.append({'fc12': fc12_sheets})
                    if lw54pick_inches >= 16.25:
                        lw5412_pick_remainder[1] = 0
                    break
            remainder_picks.append(mixed_pick)

        #rid of fc5412
        if fc5412_pick_remainder[1] > 0:
            mixed_pick2 = [{'fc54' : fc5412_pick_remainder[1]}]
            lw12_sheets = 0
            fc54pick_inches = float(fc5412_pick_remainder[1] * 0.625)

            while True:
                #combine lw12
                while fc54pick_inches < 16.25 and lw12_pick_remainder[1] > 0:
                    if lw12_pick_remainder[1] != 1:
                        fc54pick_inches += 1
                        lw12_sheets += 2
                        lw12_pick_remainder[1] -= 2
                    else:
                        fc54pick_inches += .5
                        lw12_sheets += 1
                        lw12_pick_remainder[1] -= 1

                if fc54pick_inches> 17:
                    fc54pick_inches -= .5
                    lw12_sheets -= 1
                    lw12_pick_remainder[1] += 1

                #check that the pick was filled, if not, pull from lw12 pick and complete.
                if fc54pick_inches < 16.25 and lw12_pick_remainder[0] > 0:
                    lw12_pick_remainder[0] -= 1
                    lw12_pick_remainder[1] += 34
                else:
                    if lw12_sheets > 0:
                        mixed_pick2.append({'lw12' : lw12_sheets})
                    break
            remainder_picks.append(mixed_pick2)

        #rid of fc12
        if fc12_pick_remainder[1] > 0:
            mixed_pick3 = [{'fc12' : fc12_pick_remainder[1]}]
            lw12_sheets = 0
            fc12pick_inches = float(fc12_pick_remainder[1] * .625)

            while True:
                while fc12pick_inches < 16.25 and lw12_pick_remainder[1] > 0:
                    if lw12_pick_remainder[1] != 1:
                        fc12pick_inches += 1
                        lw12_sheets += 2
                        lw12_pick_remainder[1] -= 2
                    else:
                        fc12pick_inches += .5
                        lw12_sheets += 1
                        lw12_pick_remainder[1] -= 1

                if fc12pick_inches> 17:
                    fc12pick_inches -= .5
                    lw12_sheets -= 1
                    lw12_pick_remainder[1] += 1

            #check that the pick was filled, if not, pull from lw12 pick and complete.
                if fc12pick_inches < 16.25 and lw12_pick_remainder[0] > 0:
                    lw12_pick_remainder[0] -= 1
                    lw12_pick_remainder[1] += 34
                else:
                    if lw12_sheets > 0:
                        mixed_pick3.append({'lw12' : lw12_sheets})
                        fc12_pick_remainder[1] = 0
                    break
            remainder_picks.append(mixed_pick3)

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
                'fc12r' : fc12_pick_remainder[1]
            }

            query = """
                    INSERT INTO builds (order_id, lw5412p, lw5412r, fc5412p, fc5412r, lw12p, lw12r, fc12p, fc12r)
                    VALUES (%(order_id)s, %(lw5412p)s, %(lw5412r)s, %(fc5412p)s, %(fc5412r)s, %(lw12p)s, %(lw12r)s, %(fc12p)s, %(fc12r)s)
                    """

            results = connectToMySQL(db).query_db(query, build_data)
            build = Build.get_build_by_id({'id' : results})
            build.remainder_pick = remainder_picks
            return build
        # if the id already exists, it means we are trying to get the remainder picks
        if len(remainder_picks) > 0:
            remainder_pick_prints = []
            for pick in remainder_picks:
                total_sheets = 0
                keys = []
                vals = []
                for sheets in pick:
                    for key, val in sheets.items():
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

            return remainder_pick_prints
        remainder_picks = None
        return remainder_picks


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
                SET lw5412p = %(lw5412p)s, lw5412r = %(lw5412r)s, lw12p = %(lw12p)s, lw12r = %(lw12r)s, fc12p = %(fc12p)s, fc12r = %(fc12r)s, fc5412p = %(fc5412p)s, fc5412r = %(fc5412r)s
                WHERE id = {order_id};
                """
        results = connectToMySQL(db).query_db(query, build_data)
        return results




