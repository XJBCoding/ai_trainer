import pymongo
import random
import string
import datetime


class PlanController:
    def __init__(self, id):
        client = pymongo.MongoClient(
            "mongodb+srv://kunjian:iotproject@cluster0-ttnra.mongodb.net/test?retryWrites=true")
        mydb = client["IoTProject"]
        self.profile = mydb['Profile']
        self.movements = mydb['Movements']
        self.trainingPlan = mydb["TrainingPlan"]
        self.historydb = mydb['TrainingHistory']
        self.coupondb = mydb['Coupon']
        self.id = id
        self.plan = self.getTodayTraining()
        self.weight = self.getWeight()
        self.history = {'userid': id, 'date': str(datetime.datetime.now())[0:10],'movement':[],
                        'target':[],'count':[],'qualifiedrate':[],'target_cal':0,'actual_cal':0}
        
    # generate exercise plan for a week based on profile
    def generatePlan(self):
        movement_num = 1
        target = self.profile.find_one({"userid": self.id})["target"]
        muscles = ["chest", "back", "biceps", "triceps", "shoulder", "quadricep", "hamstring"]
        day = 0
        for muscle in muscles:
            day += 1
            muscle_move = list()
            for movement in self.movements.find({'type': target, 'muscle': muscle}):
                muscle_move.append(movement["name"])
            selection = random.sample(range(len(muscle_move)), movement_num)
            for i in selection:
                mov_name = muscle_move[i]
                mov_unit = self.movements.find_one({'name': mov_name})["unit"]
                mov_calorie = self.movements.find_one({'name': mov_name})["calorie"]
                self.trainingPlan.insert_one({'userid': self.id, 'day': day, 'name': mov_name,\
                                              'type': target, 'muscle': muscle,'unit': mov_unit,\
                                              'calorie': mov_calorie})

    # The return object is a list of dictionaries, dictionaries' structure is the same as that in mongoDB
    def getTodayTraining(self):
        day = 0
        if self.trainingPlan.find_one({'userid': self.id}) is None:
            self.generatePlan()

        for plan in self.trainingPlan.find({'userid': self.id}):
            if plan['day'] > day:
                day = plan['day']

        temp_plan = list()
        for movement in self.trainingPlan.find({'userid': self.id, 'day':day}):
            temp_plan.append(movement)
        return temp_plan

    def recommendWeight(self, movement):
        history = self.historydb.find_one({'userid': self.id, 'movement': movement},sort=[('_id', pymongo.DESCENDING)])
        if history is None:
            recommend_weight = 10
        else:
            print(history)
            movement_list = history['movement']
            index = movement_list.index(movement)
            weight = history['weight'][index]
            rate = history['qualifiedrate'][index]
            if rate < 70:
                recommend_weight = weight-2
            elif rate > 95:
                recommend_weight = weight+2
            else:
                recommend_weight = weight
        return recommend_weight


    def getWeight(self):
        return float(self.profile.find_one({'userid': self.id})["weight"])

    def caloriePerSet(self, movement):
        basicCal = 0.00883 * self.weight
        movement = self.profile.find_one({'name': movement})
        addiCal = movement['calorie'] * 5 / movement['unit']
        return format(basicCal + addiCal, '.2f')

    # When Raspberry pi finish today's training, call this function
    def deleteLastPlan(self):
        day = 0
        if self.trainingPlan.find_one({'userid': self.id}) is None:
            self.generatePlan()
        for plan in self.trainingPlan.find({'userid': self.id}):
            if plan['day'] > day:
                day = plan['day']
        self.trainingPlan.delete_many({"userid": self.id, 'day': day})

    def updateHistory(self,movement,target,count,qualifiedrate,target_cal,actual_cal):
        self.history['movement'].append(movement)
        self.history['target'].append(target)
        self.history['count'].append(count)
        self.history['qualifiedrate'].append(qualifiedrate)
        self.history['target_cal'] += target_cal
        self.history['actual_cal'] += actual_cal

    # The input should be a well-structured dictionary object
    def uploadTrainingHistory(self):
        self.historydb.insert_one(self.history)

    def generateCoupon(self):
        coupon = ''.join(random.choices(string.ascii_uppercase + string.digits, k=15))
        while self.coupondb.find_one({'coupon': coupon}) is not None:
            coupon = ''.join(random.choices(string.ascii_uppercase + string.digits, k=15))
        self.coupondb.insert_one({'userid': self.id, 'coupon': coupon})
        return coupon






