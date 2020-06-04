from mainapp.core.recommendations.recommender import Recommend


class EnergyRecommend(Recommend):

    def find_energy(self, recipe_id):
        energy = self.db.aggregation('recipes', [
            {"$match":
                {
                    "id": recipe_id
                }
            },
            {"$group":
                {"_id":
                    {
                        "food_energy": "$food_energy"
                    }
                }
            }
        ])
        if not energy: return None
        return energy[0]["food_energy"]
